from typing import cast

import pandas as pd
import statsmodels.api as sm

from statsmodels.tsa.stattools import adfuller


def first_difference(data: pd.Series):
    name = data.name
    ret = data.diff().dropna()
    ret.name = name

    return ret


class ArbitragePair:
    """
    store a pair of data and judge their cointegration
    """

    def __init__(self, coin1: pd.Series, coin2: pd.Series, formative_period: tuple, trading_period: tuple = None,
                 threshold: float = .05, trading_fee: float = .0001):
        self.coin1 = coin1
        self.coin2 = coin2
        self.threshold = threshold
        self.trading_fee = trading_fee
        self.cointegration = False
        self.formative_period = (pd.to_datetime(formative_period[0], format='%Y%m%d'),
                                 pd.to_datetime(formative_period[1], format='%Y%m%d'))
        self.trading_period = (pd.to_datetime(trading_period[0], format='%Y%m%d'),
                               pd.to_datetime(trading_period[1], format='%Y%m%d'))
        self.ADF_statistic = None
        self.OLS_results = None

    @classmethod
    def ADF_test(cls, data: pd.Series, alpha=0.05, case: str = ''):
        # 航空公司乘客数据adf检验
        result = adfuller(data[:])
        result = cast(list, result)
        match case:
            case 'residual':
                case = 'OLS Residual'
            case 'first difference':
                case = f'{data.name} First Difference'
            case 'origin':
                case = f'{data.name}'
        print(f'{case} ADF Test:')
        print('ADF Statistics: %f' % result[0])
        print('p-value: %f' % result[1])
        print('Critical values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))
        print(f'Result: The series is {"not " if result[1] > alpha else ""}stationary')
        return (result[1] < alpha, result[0]) if case == 'OLS Residual' else result[1] < alpha

    def get_residual(self):
        # 创建线性回归模型并拟合数据
        model = sm.OLS(self.coin1.loc[self.formative_period[0]:self.formative_period[1]],
                       sm.add_constant(self.coin2.loc[self.formative_period[0]:self.formative_period[1]]))
        results = model.fit()
        self.OLS_results = results
        # 获取残差
        residuals = results.resid

        return pd.Series(residuals)

    def check_cointegration(self):
        # if (
        #         not self.ADF_test(self.coin1[1:], case='origin')
        #         and not self.ADF_test(self.coin2[1:], case='origin')
        #         and self.ADF_test(first_difference(self.coin1[1:]), case='first_difference')
        #         and self.ADF_test(first_difference(self.coin2[1:]), case='first_difference')
        # ):
        coin_bool, ADF_statistic = self.ADF_test(self.get_residual(), case='residual', alpha=0.01)
        self.ADF_statistic = ADF_statistic
        if coin_bool:
            self.cointegration = True
            print(f'{self.coin1.name} and {self.coin2.name} are cointegrated')
            return True
        else:
            print(f'{self.coin1.name} and {self.coin2.name} are not cointegrated')
            return False


def find_cointegration(data: pd.DataFrame, formative_period: tuple, trading_period: tuple = None):
    """
    find from data if there is cointegration pair
    :param trading_period: the period to trade the cointegration pair
    :param formative_period: the period to form the cointegration pair
    :param data:dataframe that contains different commodity's price
    :return: list of CointegrationPair
    """
    f_start, f_end = pd.to_datetime(formative_period[0], format='%Y%m%d'), pd.to_datetime(formative_period[1],
                                                                                          format='%Y%m%d')
    cointegration_pairs = []
    # corr_mat = data.loc[f_start:f_end].corr()
    # pd.DataFrame(corr_mat).to_csv('corr.csv')
    stationary_bool = [0] * len(data.columns)
    # check integration
    for i in range(len(data.columns)):
        # stationary_bool[i] = ArbitragePair.ADF_test(data.loc[f_start:f_end].iloc[:, i], case='origin')
        stationary_bool[i] = ArbitragePair.ADF_test(first_difference(data.loc[f_start:f_end].iloc[:, i]),
                                                    case='first difference',
                                                    alpha=0.01)
    print([ticker for ticker, is_true in zip(data.columns, stationary_bool) if is_true])
    # for every integration, check cointegration
    for i in range(len(data.columns) - 1):
        for j in range(i + 1, len(data.columns)):
            if stationary_bool[i] == stationary_bool[j] == 1:
                cointegration_pair = ArbitragePair(data.iloc[:, i],
                                                       data.iloc[:, j],
                                                   formative_period=formative_period, trading_period=trading_period)
                if cointegration_pair.check_cointegration():
                    cointegration_pairs.append(cointegration_pair)

    return cointegration_pairs
