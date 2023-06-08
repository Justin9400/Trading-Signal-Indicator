import yfinance as yf
import datetime
from datetime import datetime
from datetime import date
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd 
import pyautogui
import os

screen_width, screen_height = pyautogui.size()
screen_width, screen_height = int(str(screen_width)), int(str(screen_height))

def main():   
    ticker = getTicker()
    start_date = getDate()
    end_date = datetime.today()
    data_interval = '1d'

    # Download the data with monthly frequency
    df = yf.download(ticker, start = start_date, end = end_date, interval = data_interval)

    # Remove all rows that have empty columns
    # yfinance for some reason outputs empty rows with random dates that are not in the interval
    df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'], how='all', inplace=True)

    MACD(df)

def getTicker():
    is_ticker = False
    while(is_ticker == False):
        ticker = input("Enter a ticker: ")
        check_ticker = yf.Ticker(ticker).history(period = '7d', interval = '1d')    
        number = len(check_ticker)
        if(number == 0):
            print ("Invalid Ticker: ")
        else:
            is_ticker = True
            return ticker

def getDate():
    # Takes the user input for date and ensures that the ticker has been around since then
    rawDate = str(input("Enter a start date in this format (yyyy-mm-dd): "))
    year, month, day = map(int, rawDate.split("-"))
    Date = date(year, month, day)
    return Date

def MACD(df):
    # Calculate the moving averages
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA100'] = df['Close'].rolling(window=100).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    symbols = {'Buy': 'circle', 'BUY': 'circle', 
            'Hold': 'circle', 'HOLD': 'circle',
            'SELL': 'circle', 'Sell': 'circle'}

    # Calculate the MACD indicator
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    df['MACD'] = macd
    df['Signal'] = signal
    df["SMA Overall"] = ""
    df["MACD Overall"] = ""

    previousBuy = False
    previousSell = False

    previousBuyMA = False
    previousSellMA = False
    previousHoldMA = False
    iterator1 = df.iterrows()
    iterator2 = df.iterrows()
    next(iterator2)
    for (i1, row1), (i2, row2) in zip(iterator1, iterator2):
        ### MACD 
        # If the MACD breaks above the signal line and both lines are above the 0 line
        if row1['MACD'] < row1['Signal'] and row2['MACD'] > row2['Signal'] and row2['MACD'] > 0 and row2['Signal'] > 0:
            if previousBuy == False:
                    df.at[i2, 'MACD Overall'] = 'Buy'
                    previousBuy = True
                    previousSell = False
        # If the MACD or the Signal line break above the 0 line and the MACD is above the Signal line
        elif row1['MACD'] < 0 and row1['Signal'] < 0 and row2['MACD'] > 0 or row2['Signal'] > 0 and row2['MACD'] > row2['Signal']:
            if previousBuy == False:
                    df.at[i2, 'MACD Overall'] = 'Buy'
                    previousBuy = True
                    previousSell = False
        # If the MACD is above the signal line then breaks below the signal line and both are below the 0 line 
        elif row1['MACD'] > row1['Signal'] and row2['MACD'] < row2['Signal'] and row2['MACD'] < 0 and row2['Signal'] < 0:
            if previousSell == False:
                    df.at[i2, 'MACD Overall'] = 'Sell'
                    previousSell = True
                    previousBuy = False
        # If the MACD and signal are above the 0 line and then the MACD or signal break below the 0 line 
        elif row1['MACD'] > 0 and row1['Signal'] > 0 and row2['MACD'] < 0 or row2['Signal'] < 0 and row2['MACD'] < row2['Signal']:
            if previousSell == False:
                    df.at[i2, 'MACD Overall'] = 'Sell'
                    previousSell = True
                    previousBuy = False
 
main()