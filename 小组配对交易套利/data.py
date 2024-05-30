# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 10:24:21 2023

@author: 20122
"""


import statsmodels.api as sm
import pandas as pd

from statsmodels.tsa.stattools import adfuller

df1 = pd.read_excel('SC2212.INE.xlsx')
df2 = pd.read_excel('SC2303.INE.xlsx')

df1.rename(columns={'日期': 'date', '收盘价(元)': 'close'}, inplace=True)
df2.rename(columns={'日期': 'date', '收盘价(元)': 'close'}, inplace=True)

df1.dropna(inplace=True)
df2.dropna(inplace=True)
df1['date'] = df1['date'].astype(str)
df2['date'] = df2['date'].astype(str)
df1['date'] = df1['date'].apply(lambda x: int(x[:4] + x[5:7] + x[8:10]))
df2['date'] = df2['date'].apply(lambda x: int(x[:4] + x[5:7] + x[8:10]))


def get_corr_between(start_date, end_date, df1=df1, df2=df2):
    df1_part = df1[(df1['date'] >= start_date) & (df1['date'] <= end_date)]
    df2_part = df2[(df2['date'] >= start_date) & (df2['date'] <= end_date)]
    df1_name = df1.iloc[:, 0].values[0]
    df2_name = df2.iloc[:, 0].values[0]
    df1_part.rename(columns={'close': df1_name}, inplace=True)
    df2_part.rename(columns={'close': df2_name}, inplace=True)
    return pd.merge(df1_part[['date', df1_name]], df2_part[['date', df2_name]], on='date')


def ADF_test(data):
    # 航空公司乘客数据adf检验
    result = adfuller(data)
    print('ADF Statistics: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    print(f'Result: The series is {"not " if result[1] > 0.05 else ""}stationary')


def check_co_integrated(y, x):
    x = sm.add_constant(x)

    # 创建线性回归模型并拟合数据
    model = sm.OLS(y, x)
    results = model.fit()

    # 获取残差
    residuals = results.resid

    print(residuals)
    print(results.summary())
    with open('regression_summary.txt', 'w') as file:
        file.write(results.summary().as_text())
    result = adfuller(residuals)
    print('残差 ADF Statistics: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    print(f'Result: y 与 x {"不" if result[1] > 0.05 else ""}存在协整关系')


matrix = get_corr_between(20210302, 20220302)
print('0阶')
ADF_test(matrix.iloc[:, 1])
ADF_test(matrix.iloc[:, 2])

ADF_test(matrix.iloc[:, 1].diff()[1:])
ADF_test(matrix.iloc[:, 2].diff()[1:])
