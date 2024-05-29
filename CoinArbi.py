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

    def __init__(self, coin1: pd.Series, coin2: pd.Series, threshold, trading_fee: float):
        self.coin1 = coin1
        self.coin2 = coin2
        self.threshold = threshold
        self.trading_fee = trading_fee
        self.cointegration = False

    def ADF_test(self, data: pd.Series, threshold=0.05, case: str = ''):
        # 航空公司乘客数据adf检验
        result = adfuller(data)
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
        print(f'Result: The series is {"not " if result[1] > threshold else ""}stationary')
        return result[1] > threshold

    def get_residual(self):
        # 创建线性回归模型并拟合数据
        model = sm.OLS(self.coin1, sm.add_constant(self.coin2))
        results = model.fit()

        # 获取残差
        residuals = results.resid

        return pd.Series(residuals)

    def check_cointegration(self):
        if (
                not self.ADF_test(self.coin1, case='origin')
                and not self.ADF_test(self.coin2, case='origin')
                and self.ADF_test(first_difference(self.coin1), case='first_difference')
                and self.ADF_test(first_difference(self.coin2), case='first_difference')
        ):

            if self.ADF_test(self.get_residual(), case='residual'):
                self.cointegration = True
                print(f'{self.coin1.name} and {self.coin2.name} are cointegrated')
            else:
                print(f'{self.coin1.name} and {self.coin2.name} are not cointegrated')


def find_cointegration(data: pd.DataFrame):
    """
    find from data if there is cointegration pair
    :param data:dataframe that contains different commodity's price
    :return: list of CointegrationPair
    """
    cointegration_pairs = []
    for i in range(len(data.columns)):
        for j in range(i + 1, len(data.columns)):
            coin1 = data.columns[i]
            coin2 = data.columns[j]
            cointegration_arbitrage = CointegrationPair(coin1, coin2, 30, 2, 0.001)
            z_score = cointegration_arbitrage.get_cointegration()
            if z_score[-1] > 2 or z_score[-1] < -2:
                cointegration_pairs.append((coin1, coin2))
    return cointegration_pairs
