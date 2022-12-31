
# Import libraries
import json
import requests
import pandas as pd
import mplfinance as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import datetime
  
def save_data(key):
    COLUMNS = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'quote_av', 'trades',
               'tb_base_av', 'tb_quote_av', 'ignore']
    # defining key/request url
    
    # requesting data from url
    data = requests.get(key)  
    js = data.json()
    out = json.dumps(js, indent=4)

    with open("data/all_data.json", "w") as outfile:
        outfile.write(out)