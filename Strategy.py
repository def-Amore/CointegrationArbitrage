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
    def __init__(self, pair: ArbitragePair, trading_period: tuple, open_threshold: float = 1.1,
                 close_threshold: float = 0.5, stop_loss_threshold: float = 2.1, ):
        self.pair = pair
        self.trading_period = trading_period
        self.open_threshold = open_threshold
        self.close_threshold = close_threshold
        self.stop_loss_threshold = stop_loss_threshold
        self.OLS_results = pair.OLS_results
        self.std_spread = None
        self.spread = None
        self.trade_signals = None
        self.profit = None

    def trade(self):
        t_start, t_end = self.trading_period
        spread = self.pair.coin1.loc[t_start:t_end] - self.OLS_results.params[1] * self.pair.coin2.loc[t_start:t_end]
        self.spread = spread
        standardized_spread = (spread - spread.mean()) / spread.std()
        standardized_spread.name = 'spread'
        # standardized_spread.to_csv('spread.csv')
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
        # pd.concat([spread, trade_signals], axis=1, join='inner').to_csv('trade_signals.csv')
        self.get_profit()
        print(f'Profit: {self.profit}')

    def get_profit(self):
        profit = 0
        open_idx = None
        for i, trade_signal in zip(self.std_spread.index, self.trade_signals):
            if trade_signal == TradeSignal.LONG:
                open_idx = i
            if trade_signal == TradeSignal.SHORT:
                open_idx = i
            if trade_signal == TradeSignal.STOP_LOSS:
                profit -= np.abs(self.spread[open_idx] - self.spread[i])
            if trade_signal == TradeSignal.CLOSE:
                profit += np.abs(self.spread[open_idx] - self.spread[i])
        self.profit = profit
