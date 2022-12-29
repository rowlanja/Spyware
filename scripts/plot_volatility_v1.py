
# Import libraries
import json
import requests
import pandas as pd
import mplfinance as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import datetime
from sklearn.cluster import AgglomerativeClustering

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

def get_rate_of_changes(values):
    prev_val = values[0]
    rates = []
    x = np.array(range(0, 100))
    for current_val in values[1:]:
        change = current_val - prev_val
        prev_val = current_val
        rate = ( change/current_val ) * 100
        rates.append(rate)
    y = np.array(rates)

    plt.title("Plotting 1-D array")
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    plt.plot(x, y, color = "red", marker = "o", label = "Array elements")
    plt.legend()
    plt.savefig("../plots/change.png")
    return rates


def quantize_changes(df, tolerance=0.25):
    # df: DataFrame with only the column(s) to quantize
    model = AgglomerativeClustering(distance_threshold=2 * tolerance, linkage='complete',
                                    n_clusters=None).fit(df)
    df = df.assign(
        group=model.labels_,
        center=df.groupby(model.labels_).transform(lambda v: (v.max() + v.min()) / 2),
        change=df
    )
    return df

def form_quantized_frame(quant_df, price_df):
    df = pd.DataFrame().assign(
        group=quant_df.group,
        center=quant_df.center,
        Open=price_df.Open,
        Open_time=price_df.Open_time,
        High=price_df.High,
        Low=price_df.Low,
        Close=price_df.Close,
        change=quant_df.change
    )
    return df

def plot_quantized_changes(df):
    hlinessupp = df[df['change'] > 0.5]
    hlinesres = df[df['change'] < -0.5]
    hlines = []
    colors = []
    for r in hlinessupp.to_numpy().tolist():
        hlines.append((r[2]))
        colors.append('g')
    for r in hlinesres.to_numpy().tolist():
        hlines.append((r[2]))
        colors.append('b')

    df.index = pd.DatetimeIndex(df['Open_time'])
    mpl.plot(df,
        type='candle', 
        style='binance', 
        savefig='../plots/volatility_step_in.png',
        hlines= dict(hlines=hlines,linestyle=['-'],linewidths = [2],colors=colors)
    )

# hlines=dict(hlines= support_resistance,linestyle='-',linewidths = (1,1),colors=('b','r')

# Convert array of integers to pandas series
df = get_data()
get_moving_averages(df)
chg = get_rate_of_changes(df.Open)
quantized_changes = quantize_changes(pd.DataFrame(chg))
form_quantized_frame = form_quantized_frame(quantized_changes, df)
plot_quantized_changes(form_quantized_frame)
