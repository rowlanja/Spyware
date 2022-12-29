
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

WINDOW_SIZE = 250
def get_data():
    f = open("data/all_data.json")
    js = json.load(f)

    df = pd.DataFrame(js, columns=COLUMNS)
    df.set_index('Open_time')

    df = df.loc[len(df)-WINDOW_SIZE:,['Open_time','Open', 'High', 'Low', 'Close']]

    df['Open_time']=(pd.to_datetime(df['Open_time'],unit='ms')) 
    df["Open"] = df["Open"].astype("float")
    df["High"] = df["High"].astype("float")
    df["Low"] = df["Low"].astype("float")
    df["Close"] = df["Close"].astype("float")
    df.index = np.arange(len(df))
    return df

def calculate_differential(values):
    prev_val = values[len(values)-WINDOW_SIZE]
    rates = []
    x = np.array(range(0, WINDOW_SIZE-1))
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
    plt.savefig("plots/change.png")
    return rates


def quantize_differential(df, tolerance=0.25):
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

def plot(df):
    hlinessupp = df[df['change'] > 0.5].to_numpy().tolist()
    hlinesres = df[df['change'] < -0.5].to_numpy().tolist()
    hlines, colors = [], []
    for r in hlinessupp:
        hlines.append((r[2]))
        colors.append('g')
    for r in hlinesres:
        hlines.append((r[2]))
        colors.append('b')

    df.index = pd.DatetimeIndex(df['Open_time'])
    mpl.plot(df,
        type='candle', 
        style='binance', 
        savefig='plots/volatility_step_in.png',
        hlines= dict(hlines=hlines,linestyle=['-'],linewidths = [2],colors=colors)
    )

def plot_differentials():
    # Convert array of integers to pandas series
    df = get_data()
    chg = calculate_differential(df.Open)
    quantized_changes = quantize_differential(pd.DataFrame(chg))
    form_frame = form_quantized_frame(quantized_changes, df)
    plot(form_frame)
