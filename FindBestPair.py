from PairArbi import find_cointegration
from DataPrep import get_data_from_csv

# tickers = ['sc2304', 'sc2305', 'sc2306', 'sc2307', 'sc2308', 'sc2309', 'sc2310', ]
# data = get_data(tickers)

data = get_data_from_csv('data_INE.csv', ['SC2303',
                                          'SC2306', 'SC2309', 'SC2312', ])
# data.to_csv('tradingpool.csv')
co_ints_list = []
for i in range(101, 602, 100):
    # test cointegration for all the periods, find the most cointegrated pair.
    print(f'Period: {20210000 + i} to {20220000 + i}')
    co_ints = find_cointegration(data, (20210000 + i, 20220000 + i), trading_period=(20220000 + i, 20230000 + i))
    co_ints_list.append(co_ints)
for co_ints in co_ints_list:
    co_ints.sort(key=lambda x: x.ADF_statistic)
    print(co_ints[0].coin1.name, co_ints[0].coin2.name, co_ints[0].ADF_statistic)

