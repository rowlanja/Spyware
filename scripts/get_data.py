
# Import libraries
import json
import requests
import pandas as pd
import mplfinance as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import datetime

COLUMNS = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'quote_av', 'trades',
               'tb_base_av', 'tb_quote_av', 'ignore']
# [
#   [
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Ignore
#   ]
# ]
# defining key/request url
key = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1000"
  
# requesting data from url
data = requests.get(key)  
js = data.json()
df = pd.DataFrame(js, columns=COLUMNS)
df.set_index('Open_time')

df = df.loc[0:100,['Open_time','Open', 'High', 'Low', 'Close']]

df['Open_time']=(pd.to_datetime(df['Open_time'],unit='ms')) 
df["Open"] = df["Open"].astype("float")
df["High"] = df["High"].astype("float")
df["Low"] = df["Low"].astype("float")
df["Close"] = df["Close"].astype("float")

print(df)
df.index = pd.DatetimeIndex(df['Open_time'])

mpl.plot(df,type='candle', style='charles', savefig='../plots/week.png')