from scripts import plot_volatility_v1
from scripts import get_data
from scripts import plot_week

key = "https://api.binance.com/api/v3/klines?symbol=ATOMUSDT&interval=1h&limit=1000"

get_data.save_data(key)
plot_week.plot()
plot_volatility_v1.plot_differentials()  