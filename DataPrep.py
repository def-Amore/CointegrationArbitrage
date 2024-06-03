from typing import List

from CoinArbi import find_cointegration, CointegrationPair

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.request as urllib2
import json


def get_data_from_csv(file_path: str, symbols: List[str]):
    data = pd.read_csv(file_path, index_col=1)

    groupby_symbol = data.groupby('Symbol')
    merged_data = pd.DataFrame()
    for symbol in symbols:
        tmp_group = groupby_symbol.get_group(symbol)
        tmp_df = pd.DataFrame([np.array(tmp_group['Trddt']), np.log(np.array(tmp_group['Close']))]).T
        tmp_df.set_index(0, inplace=True)
        tmp_df.index.rename('date', inplace=True)
        tmp_df.columns = [symbol]
        if merged_data.empty:
            merged_data = tmp_df
            continue
        merged_data = pd.merge(tmp_df, merged_data, left_index=True, right_index=True, how='inner')
    merged_data.index = pd.to_datetime(merged_data.index, format='%Y/%m/%d')
    merged_data = merged_data.astype(float)

    return merged_data




# 'SC2403','SC2406','SC2409','SC2412'])

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
        print()
    close_result = np.array(close_result)
    close_result = close_result.T
    data = pd.DataFrame(close_result, columns=symbols)
    data.to_csv('data1.csv')
    return data
