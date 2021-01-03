"""
Creating & Back-testing the Strategy
Now, we can proceed to back-test the Money Flow Multiplier strategy on some currency pairs within the hourly time frame. The trading conditions are therefore:
Go long (Buy) whenever the Money Flow Multiplier touches the lower barrier at -90.00 with the previous two values above -90.00.
Go short (Sell) whenever the Money Flow Multiplier touches the upper barrier at 90.00 with the previous two values below 90.00.

https://medium.com/swlh/creating-a-trading-strategy-from-scratch-in-python-fe047cb8f12

"""

def money_flow_multiplier(Data, what, high, low, where):
    # Numerator    
    Data[:, where] = Data[:, what] - Data[:, low]
    Data[:, where + 1] = Data[:, high] - Data[:, what]
    # Denominator    
    Data[:, where + 2] = Data[:, where] - Data[:, where + 1]
    Data[:, where + 3] = Data[:, high] - Data[:, low]
    
    # Avoiding NaN values (Division by zero in case the High equals   the Low)
    for i in range(len(Data)):
        if Data[i, where + 3] == 0:
            Data[i, where + 3] = 0.0001
    # Money Flow Multiplier Formula
    Data[:, where + 4] = (Data[:, where + 2] / Data[:, where + 3]) * 100
    
    return Data
    
def signal(Data, what, buy, sell):
    
    for i in range(len(Data)):
            
        if Data[i, what] < lower_barrier and Data[i - 1, what] > lower_barrier and Data[i - 2, what] > lower_barrier :
            Data[i, buy] = 1
            
        if Data[i, what] > upper_barrier and Data[i - 1, what] < upper_barrier and Data[i - 2, what] < upper_barrier :
            Data[i, sell] = -1
