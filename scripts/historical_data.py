import time
import pandas as pd
from binance.client import Client
import frameselect


class BinanceTicker:
    def __init__(self, ticker_binance, time_frame_binance):
        self.ticker = ticker_binance
        self.time_frame = time_frame_binance
        # If you are living in the US, you need to use the binance.us API
        # self.client = Client("", "", tld="us")
        self.client = Client("", "", tld="com")
        self.file_name = ticker + "-" + time_frame_binance + "-" + ".csv"
        self.header_list = [
            "unix",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close time",
            "Volume USDT",
            "tradecount",
            "taker buy vol",
            "taker buy quote vol",
            "ignore",
        ]

    def check_pair(self, ticker_symbol):
        """
        Checks if the given ticker symbol is a valid pair.
        :param ticker_symbol: The ticker symbol to check.
        :return: True if the ticker symbol is a valid pair, False otherwise.
        """
        if self.client.get_symbol_info(ticker_symbol):
            print("Pair found in Binance API.")
            return self.client.get_symbol_info(ticker_symbol)
        else:
            print("Pair is not found in Binance API.")
            exit()
            return

    def historical_data_write(self):
        """
        Writes the historical data for a given ticker symbol to a csv file.
        """
        df = pd.DataFrame(
            reversed(
                self.client.get_historical_klines(
                    symbol=self.ticker, interval=self.time_frame, start_str=start
                )
            ),
            columns=self.header_list,
        )
        # Converting the unix time to a readable date format for today
        date = pd.to_datetime(df["unix"], unit="ms")
        df.insert(1, "date", date)
        df.drop(
            labels=[
                "volume",
                "close time",
                "tradecount",
                "taker buy vol",
                "taker buy quote vol",
                "ignore",
            ],
            inplace=True,
            axis=1,
        )
        df.to_csv(self.file_name, index=False)
        print("Data writing:", self.file_name)


# Example input:"BTCUSDT 1H", "ETHBTC 3D", "BNBUSDT 15M"
print("Example input: BTCUSDT 1W, ETHBTC 3D, BNBUSDT 1H, ATOMUSDT 15M")
ticker = "BTCUSDT"
binance_api_runtime = time.perf_counter()

time_frame, start = frameselect.frame_select("15M")
med_time_frame, start = frameselect.frame_select("1H")
low_time_frame, start = frameselect.frame_select("4H")

user_ticker = BinanceTicker(ticker, time_frame)
user_ticker_mtf = BinanceTicker(ticker, med_time_frame)
user_ticker_ltf = BinanceTicker(ticker, low_time_frame)


user_ticker.check_pair(ticker)

user_ticker.historical_data_write()
user_ticker_mtf.historical_data_write()
user_ticker_ltf.historical_data_write()

print(
    "Binance API historical data runtime: ",
    time.perf_counter() - binance_api_runtime,
    "seconds",
)


tickers = ['btcusdt', 'atomusdt', 'peopleusdt', 'dydxusdt' ]