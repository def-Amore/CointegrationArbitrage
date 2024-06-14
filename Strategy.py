import numpy as np
import pandas as pd

from PairArbi import ArbitragePair

from enum import Enum, auto


class TradeSignal(Enum):
    LONG = auto()
    SHORT = auto()
    CLOSE = auto()
    STOP_LOSS = auto()
    HOLD = auto()


class Strategy:
    def __init__(self, pair: ArbitragePair, trading_period: tuple, principle: float, open_threshold: float = 1.1,
                 close_threshold: float = 0.5, stop_loss_threshold: float = 2.1, ):
        self.pair = pair
        self.SC2306 = pair.coin1.apply(np.exp)
        self.SC2303 = pair.coin2.apply(np.exp)*pair.OLS_results.params[1]
        self.trading_period = trading_period
        self.open_threshold = open_threshold
        self.close_threshold = close_threshold
        self.stop_loss_threshold = stop_loss_threshold
        self.OLS_results = pair.OLS_results
        self.std_spread = None
        self.spread = None
        self.trade_signals = None
        self.profit = None
        self.principle = principle

    def trade(self):
        t_start, t_end = self.trading_period
        spread = self.pair.coin1.loc[t_start:t_end] - self.OLS_results.params[1] * self.pair.coin2.loc[t_start:t_end]
        standardized_spread = (spread - spread.mean()) / spread.std()

        delog_spread = self.pair.coin1.loc[t_start:t_end].apply(np.exp) - self.OLS_results.params[
            1] * self.pair.coin2.loc[t_start:t_end].apply(np.exp)
        delog_spread.name = 'spread'
        delog_spread.to_csv('spread_delog.csv')
        self.spread = delog_spread
        self.std_spread = standardized_spread


        # trading
        # open position
        open_position = False
        trade_signals = pd.Series([TradeSignal.HOLD] * len(standardized_spread), index=standardized_spread.index,
                                  name='trade_signals')
        for i, price in zip(standardized_spread.index, standardized_spread):
            if not open_position and price > self.open_threshold:
                print(f'Short spread at {i} with price {price}')
                trade_signals.loc[i] = TradeSignal.SHORT
                open_position = True
            if open_position and 0 < price < self.close_threshold:
                print(f'Close position at {i} with price {price}')
                trade_signals.loc[i] = TradeSignal.CLOSE
                open_position = False
            if open_position and price > self.stop_loss_threshold:
                print(f'Stop loss at {i} with price {price}')
                trade_signals.loc[i] = TradeSignal.STOP_LOSS
                open_position = False
            if not open_position and price < -self.open_threshold:
                print(f'Long spread at {i} with price {price}')
                trade_signals.loc[i] = TradeSignal.LONG
                open_position = True
            if open_position and 0 > price > -self.close_threshold:
                print(f'Close position at {i} with price {price}')
                trade_signals.loc[i] = TradeSignal.CLOSE
                open_position = False
            if open_position and price < -self.stop_loss_threshold:
                print(f'Stop loss at {i} with price {price}')
                trade_signals.loc[i] = TradeSignal.STOP_LOSS
                open_position = False
        self.trade_signals = trade_signals
        pd.concat([spread, trade_signals], axis=1, join='inner').to_csv('trade_signals_delog.csv')
        self.get_profit()
        print(f'Profit: {self.profit}')

    def get_profit(self):
        principle = self.principle
        profit = 0
        open_idx = None
        profit_list = []
        open = False
        hand = 0
        # for i, trade_signal in zip(range(0, len(self.trade_signals)), self.trade_signals):
        #     if trade_signal == TradeSignal.LONG:
        #         open_idx = i
        #         hand = principle / self.SC2306.iloc[i]
        #         open = True
        #     if trade_signal == TradeSignal.SHORT:
        #         open_idx = i
        #         hand = principle / self.SC2303.iloc[i]
        #         open = True
        #     if trade_signal == TradeSignal.STOP_LOSS and open:
        #         profit -= hand*np.abs(self.spread.iloc[open_idx] - self.spread.iloc[i])
        #         open = False
        #         hand = 0
        #     if trade_signal == TradeSignal.CLOSE:
        #         profit += hand * np.abs(self.spread.iloc[open_idx] - self.spread.iloc[i])
        #         open = False
        #         hand = 0
        # get the daily return
        LONG, SHORT = False, False
        for i, trade_signal in zip(range(0, len(self.trade_signals)), self.trade_signals):
            if trade_signal == TradeSignal.LONG:
                LONG = True
                profit_list.append(0)
                hand = principle / self.SC2306.iloc[i]
            elif trade_signal == TradeSignal.SHORT:
                SHORT = True
                profit_list.append(0)
                hand = principle / self.SC2303.iloc[i]
            elif trade_signal == TradeSignal.HOLD and LONG:
                profit_list.append(hand*(self.spread.iloc[i] - self.spread.iloc[i - 1])/principle)
            elif trade_signal == TradeSignal.HOLD and SHORT:
                profit_list.append(hand*(self.spread.iloc[i - 1] - self.spread.iloc[i])/principle)
            elif trade_signal == TradeSignal.CLOSE:
                profit_list.append(hand*abs(self.spread.iloc[i] - self.spread.iloc[i - 1])/principle)
                LONG, SHORT = False, False
                hand = 0
            elif trade_signal == TradeSignal.STOP_LOSS and (LONG or SHORT):
                print('Stop loss')
                profit_list.append(-hand*abs(self.spread.iloc[i] - self.spread.iloc[i - 1])/principle)
                LONG, SHORT = False, False
                hand = 0
            elif trade_signal == TradeSignal.HOLD and not LONG and not SHORT:
                profit_list.append(0)
            else:
                profit_list.append(0)
        profit_list = np.array(profit_list)
        print("profit_list", np.mean(profit_list))
        ER = np.mean(profit_list) * 252-.03
        print("Expected Return:", ER)
        std = np.std(profit_list) * np.sqrt(252)
        print("Sharp Ratio:", ER / std)
        downside_std = np.sqrt(np.mean(np.minimum(profit_list, 0) ** 2)) * np.sqrt(252)
        print("Sortino Ratio:", ER / downside_std)
        cumulative_returns = np.cumsum(profit_list)
        max_drawdown = (cumulative_returns.max() - cumulative_returns.min()) / cumulative_returns.max()

        # 计算 Calmar 比率
        calmar_ratio = ER / max_drawdown
        print("Calmar Ratio:",calmar_ratio)
        profit_list = pd.Series(profit_list, index=self.spread.index)
        profit_list.to_csv('profit_list_delog.csv')
        # self.profit = profit/self.principle
