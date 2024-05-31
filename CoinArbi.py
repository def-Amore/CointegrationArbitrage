import pandas as pd
import statsmodels.api as sm
import datetime as dt

from statsmodels.tsa.stattools import adfuller


def first_difference(data: pd.Series):
    return data.diff().dropna()


class CointegrationPair:
    """
    store a pair of data and judge their cointegration
    """

    def __init__(self, coin1: pd.Series, coin2: pd.Series, threshold: float = .05, trading_fee: float = .0001):
        self.coin1 = coin1
        self.coin2 = coin2
        self.threshold = threshold
        self.trading_fee = trading_fee
        self.cointegration = False

    @classmethod
    def ADF_test(cls, data: pd.Series, alpha=0.05, case: str = ''):
        # 航空公司乘客数据adf检验
        result = adfuller(data[1:])
        match case:
            case 'residual':
                case = 'OLS Residual'
            case 'first_difference':
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
        return result[1] < alpha

    def get_residual(self):
        # 创建线性回归模型并拟合数据
        model = sm.OLS(self.coin1[1:], sm.add_constant(self.coin2[1:]))
        results = model.fit()

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

        if self.ADF_test(self.get_residual(), case='residual'):
            self.cointegration = True
            print(f'{self.coin1.name} and {self.coin2.name} are cointegrated')
            return True
        else:
            print(f'{self.coin1.name} and {self.coin2.name} are not cointegrated')
            return False


def find_cointegration(data: pd.DataFrame):
    """
    find from data if there is cointegration pair
    :param data:dataframe that contains different commodity's price
    :return: list of CointegrationPair
    """
    cointegration_pairs = []
    stationary_bool = [0]*len(data.columns)
    # check integration
    for i in range(len(data.columns)):
        stationary_bool[i] = CointegrationPair.ADF_test(first_difference(data.iloc[:,i]),case='origin')
    # for every integration, check cointegration
    for i in range(len(data.columns)-1):
        for j in range(i+1,len(data.columns)):
            if stationary_bool[i] == stationary_bool[j] == 1:
                cointegration_pair = CointegrationPair(data.iloc[:,i], data.iloc[:,j], )
                if cointegration_pair.check_cointegration():
                    cointegration_pairs.append(cointegration_pair)

    return cointegration_pairs


