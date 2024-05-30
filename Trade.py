from CoinArbi import find_cointegration
from DataPrep import get_data

tickers = ['rb1903', 'rb1904', 'rb1905', 'rb1906', 'rb1907', 'rb1908']
data = get_data(tickers)
co_ints = find_cointegration(data)
for co in co_ints:
    print(co.coin1.name, co.coin2.name)
