# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 11:10:40 2020

@author: das68451
"""

# import libraries
import pandas_datareader as web
import pandas as pd
import numpy as np

# test scrape stock data on Tesla 
TSLA_quote = web.DataReader('TSLA', data_source = 'yahoo', start = '2010-01-01', end = '2020-08-20')
print(TSLA_quote)

# now we know it works, let's grab some other company stocks
stocks = ['GOOGL', 'TSLA', 'MRLN', 'UDOW']
numAssets = len(stocks)
source = 'yahoo'
start = '2010-01-01'
end = ' 2020-08-20'

data = pd.DataFrame(columns=stocks)
for symbol in stocks:
  data[symbol] = web.DataReader(symbol, data_source=source, start=start, end=end)['Adj Close']

# check to see if we have the necessary data
list(data)
data['GOOGL']

# calculate parameters based on historical data

# first we will look at logarithmic returns; these are the % changes between stock prices from day to day
# calculate log returns
percent_change = data.pct_change()
returns = np.log(1+percent_change)

returns.head()

# once we have percent changes, we can calculate the average daily returns and covriance matrix for each stock
# covariance matrix is used to calculate volatility

meanDailyReturns = returns.mean()
covMatrix = returns.cov()

# run meanDailyReturns, displays the returns you are getting on average per day from these companies
# run covMatrix, displays...

# now let's create a hypothetical portfolio and see what returns and volatility we get. We'll use random weights for the assets
# Google = 50%, Tesla = 15%, MRLN = 20%, UDOW = 30%
# calculate expected portfolio performance 
weights = np.array([0.5, 0.15, 0.20, 0.15])
portReturn = np.sum(meanDailyReturns * weights)
portStdDev = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights)))

# daily return
portReturn 

# yearly return
portReturn * 365 

# daily STD
portStdDev 

# yearly STD
portStdDev * portStdDev * 365 

##########
# visualizing the data
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 7))
for c in returns.columns.values:
  plt.plot(returns.index, returns[c], lw=3, alpha=0.8, label=c)

plt.legend(loc='upper left', fontsize=12)
plt.ylabel('returns')
# in general, the greater returns a stock gives, the higher its volatility tends to be

#########
# optimizing portfolio weight
import scipy.optimize as sco

def calcPortfolioPerf(weights, meanReturns, covMatrix):
    #calculates portfolio return and std after taking in the inputs of weights, mean returns, cov matrix
    portReturn = np.sum(meanReturns * weights)
    portStdDev = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights)))
    return portReturn, portStdDev

def negSharpeRatio(weights, meanReturns, covMatrix, riskFreeRate):
    # ratio of the mean returns per unit of volatility; e.g. how much you're getting for the risk you're putting in
    # note we need to use negative sharpe ration bc scipy optimization funcs can only minimize
    p_ret, p_var = calcPortfolioPerf(weights, meanReturns, covMatrix)
    return -(p_ret - riskFreeRate) / p_var

def getPortfolioVol(weights, meanReturns, covMatrix):
    #
    return calcPortfolioPerf(weights, meanReturns, covMatrix)[1]

def findMaxSharpeRatioPortfolio(meanReturns, covMatrix, riskFreeRate):
    #
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix, riskFreeRate)
    constraints = ({'type': 'eq', 'fun':lambda x: np.sum(x)-1})
    bounds = tuple((0,1) for asset in range(numAssets))
    
    opts = sco.minimize(negSharpeRatio, numAssets*[1./numAssets,], args = args, method = 'SLSQP', bounds = bounds, constraints = constraints)
    
    return opts

#####
# let's also optimize our portfolio based off of minimizing volatility as well
def findEfficientReturn(meanReturns, covMatrix, targetReturn):
  numAssets = len(meanReturns)
  args = (meanReturns, covMatrix)
  
  def getPortfolioReturn(weights):
    return calcPortfolioPerf(weights, meanReturns, covMatrix)[0]
  
  constraints = ({'type': 'eq', 'fun': lambda x: getPortfolioReturn(x) - targetReturn},
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
  bounds = tuple((0,1) for asset in range(numAssets))
  
  return sco.minimize(getPortfolioVol, numAssets*[1./numAssets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
  
def findEfficientFrontier(meanReturns, covMatrix, rangeOfReturns):
  efficientPortfolios = []
  for ret in rangeOfReturns:
    efficientPortfolios.append(findEfficientReturn(meanReturns, covMatrix, ret))
    
  return efficientPortfolios


# https://towardsdatascience.com/how-to-be-a-successful-investor-simple-portfolio-analysis-with-python-7b66fc90fa68
