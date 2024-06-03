from CoinArbi import find_cointegration, CointegrationPair
from DataPrep import get_data

tickers = ['sc2304', 'sc2305', 'sc2306', 'sc2307', 'sc2308', 'sc2309', 'sc2310', ]
data = get_data(tickers)
co_ints = find_cointegration(data)
for co in co_ints:
    print(co.coin1.name, co.coin2.name)
