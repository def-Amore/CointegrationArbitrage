import pandas as pd

from PairArbi import ArbitragePair

from DataPrep import get_data_from_csv
from Strategy import Strategy


data = get_data_from_csv('data_INE.csv', ['SC2303', 'SC2306'])
trading_pair = ArbitragePair(data['SC2306'],
                             data['SC2303'],
                             (20210601, 20220601),
                             (20220601, 20230101))
trading_pair.check_cointegration()

print(trading_pair.OLS_results.summary())

strategy = Strategy(trading_pair, trading_pair.trading_period)
strategy.trade()
