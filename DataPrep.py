from typing import List

from CoinArbi import find_cointegration, CointegrationPair

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.request as urllib2
import json


def get_data(symbols: List[str], ):
    url_5m = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol='
    data_list = []
    for symbol in symbols:
        url = url_5m + symbol
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req)
        res = rsp.read()
        res_json = json.loads(res)
        data_list.append(res_json)
    close_result = []
    for instrument in data_list:
        oneDay_list = []
        for oneDay in instrument:
            oneDay_list.append(float(oneDay[-2]))
        close_result.append(np.array(oneDay_list))
    close_result = np.array(close_result)
    close_result = close_result.T
    data = pd.DataFrame(close_result, columns=symbols)
    data.to_csv('data1.csv')
    return data
