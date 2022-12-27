
# Import libraries
import json
import requests
import pandas as pd
import mplfinance as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
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


def get_data():
    f = open("../data/all_data.json")
    js = json.load(f)

    df = pd.DataFrame(js, columns=COLUMNS)
    df.set_index('Open_time')

    df = df.loc[0:100,['Open_time','Open', 'High', 'Low', 'Close']]

    df['Open_time']=(pd.to_datetime(df['Open_time'],unit='ms')) 
    df["Open"] = df["Open"].astype("float")
    df["High"] = df["High"].astype("float")
    df["Low"] = df["Low"].astype("float")
    df["Close"] = df["Close"].astype("float")
    return df

def get_moving_averages(df):
    # Convert array of integers to pandas series
    numbers_series = pd.Series(list(df.Open))
    windows = numbers_series.expanding()
    moving_averages = windows.mean()
    moving_averages_list = moving_averages.tolist()
    print(moving_averages_list)

def get_rate_of_changes(values):
    prev_val = values[0]
    for current_val in values[1:]:
        change = current_val - prev_val
        prev_val = current_val
        rate = ( change/current_val ) * 100
         
        print(rate, change, current_val)
  
# Convert array of integers to pandas series
df = get_data()
get_moving_averages(df)
get_rate_of_changes(df.Open)
