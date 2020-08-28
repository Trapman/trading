# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 18:35:32 2020

@author: das68451
"""
# A simple algorithm for finding the best moving average for every stock or ETF

"""
In a time series, a moving average of period N at a certain time t, is the mean value of the N values before t (included). It’s defined for each time instant excluding the first N ones. In this particular case, we are talking about the Simple Moving Average (SMA) because every point of the average has the same weight. There are types of moving averages that weigh every point in a different way, giving more weight to the most recent data. It’s the case of the Exponential Moving Average (EMA) or the Linear Weighted Moving Average (LWMA).
In trading, the number of previous time series observations the average is calculated from is called period. So, an SMA with period 20 indicates a moving average of the last 20 periods.

Moving averages are often used to detect a trend. It’s very common to assume that if the stock price is above its moving average, it will likely continue rising in an uptrend.

Generally speaking, the most used SMA periods in trading are:
20 for swing trading
50 for medium-term trading
200 for long-term trading

In order to find the best period of an SMA, we first need to know how long we are going to keep the stock in our portfolio. If we are swing traders, we may want to keep it for 5–10 business days. If we are position traders, maybe we must raise this threshold to 40–60 days. If we are portfolio traders and use moving averages as a technical filter in our stock screening plan, maybe we can focus on 200–300 days.
"""

import yfinance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

import datetime

# build out the plots
plt.rcParams['figure.figsize'] = [10, 7]

plt.rc('font', size=14)

np.random.seed(0)

y = np.arange(0,100,1) + np.random.normal(0,10,100)

sma = pd.Series(y).rolling(20).mean()

plt.plot(y,label="Time series")
plt.plot(sma,label="20-period SMA")

plt.legend()
plt.show()

# assume we want to keep the SPY ETF on S&P 500 index for 2 days and that we want to analyze 10 years of data
n_forward = 40
name = 'GLD'
start_date = "2010-01-01"
end_date = "2020-06-15"

# Now we can download our data and calculate the return after 2 days.
ticker = yfinance.Ticker("FB")
data = ticker.history(interval="1d",start='2010-01-01',
                      end=end_date)

plt.plot(data['Close'],label='Facebook')


plt.plot(data['Close'].rolling(20).mean(),label = "20-periods SMA")
plt.plot(data['Close'].rolling(50).mean(),label = "50-periods SMA")
plt.plot(data['Close'].rolling(200).mean(),label = "200-periods SMA")

plt.legend()
plt.xlim((datetime.date(2019,1,1),datetime.date(2020,6,15)))
plt.ylim((100,250))
plt.show()

ticker = yfinance.Ticker(name)
data = ticker.history(interval="1d",start=start_date,end=end_date)

data['Forward Close'] = data['Close'].shift(-n_forward)

data['Forward Return'] = (data['Forward Close'] - data['Close'])/data['Close']

# Now we can perform the optimization for searching the best moving average.
"""
We’ll do a for loop that spans among 20-period moving average and 500-period moving average. For each period we split our dataset in training and test sets, then we’ll look only ad those days when the close price is above the SMA and calculate the forward return. Finally, we’ll calculate the average forward return in training and test sets, comparing them using a Welch’s test.
"""

result = []
train_size = 0.6

for sma_length in range(20,500):
  
  data['SMA'] = data['Close'].rolling(sma_length).mean()
  data['input'] = [int(x) for x in data['Close'] > data['SMA']]
  
  df = data.dropna()

  training = df.head(int(train_size * df.shape[0]))
  test = df.tail(int((1 - train_size) * df.shape[0]))
  
  tr_returns = training[training['input'] == 1]['Forward Return']
  test_returns = test[test['input'] == 1]['Forward Return']

  mean_forward_return_training = tr_returns.mean()
  mean_forward_return_test = test_returns.mean()

  pvalue = ttest_ind(tr_returns,test_returns,equal_var=False)[1]
 
  result.append({
      'sma_length':sma_length,
      'training_forward_return': mean_forward_return_training,
      'test_forward_return': mean_forward_return_test,
      'p-value':pvalue
  })
  
  
# We’ll sort all the results by training average future returns in order to get the optimal moving average.
result.sort(key = lambda x : -x['training_forward_return'])

# The first item, which has the best score
result[0]
# the p-value is higher than 5%, so we can assume that the average return in the test set is comparable with the average return in the training set, so we haven’t suffered overfitting.

# let’s see the price chart according to the best moving average we’ve found (which is the 479-period moving average).
best_sma = result[0]['sma_length']
data['SMA'] = data['Close'].rolling(best_sma).mean()

plt.plot(data['Close'],label=name)

plt.plot(data['SMA'],label = "{} periods SMA".format(best_sma))

plt.legend()
plt.show()
