import os
import time
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import historical_data
import indicators_sma_rsi
import support_resistance


@dataclass
class Values:
    ticker_csv: str
    selected_timeframe: str

    def __post_init__(self):
        self.ticker_csv = self.ticker_csv.upper()
        self.selected_timeframe = self.selected_timeframe.lower()


class Supres(Values):
    @staticmethod
    def main(ticker_csv, selected_timeframe, candle_count=254):
        print(
            f"Start main function in {time.perf_counter() - perf} seconds\n"
            f"{ticker_csv} data analysis in progress."
        )
        now_supres = time.perf_counter()
        df = pd.read_csv(
            ticker_csv,
            delimiter=",",
            encoding="utf-8-sig",
            index_col=False,
            nrows=candle_count,
            keep_default_na=False,
        )
        df = df.iloc[::-1]
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        df = pd.concat([df, df.tail(1)], axis=0, ignore_index=True)
        df.dropna(inplace=True)
        historical_hightimeframe = (
            historical_data.Client.KLINE_INTERVAL_1DAY,
            historical_data.Client.KLINE_INTERVAL_3DAY,
            historical_data.Client.KLINE_INTERVAL_1WEEK,
        )
        historical_lowtimeframe = (
            historical_data.Client.KLINE_INTERVAL_1MINUTE,
            historical_data.Client.KLINE_INTERVAL_3MINUTE,
            historical_data.Client.KLINE_INTERVAL_5MINUTE,
            historical_data.Client.KLINE_INTERVAL_15MINUTE,
            historical_data.Client.KLINE_INTERVAL_30MINUTE,
            historical_data.Client.KLINE_INTERVAL_1HOUR,
            historical_data.Client.KLINE_INTERVAL_2HOUR,
            historical_data.Client.KLINE_INTERVAL_4HOUR,
            historical_data.Client.KLINE_INTERVAL_6HOUR,
            historical_data.Client.KLINE_INTERVAL_8HOUR,
            historical_data.Client.KLINE_INTERVAL_12HOUR,
        )
        sma_values = 20, 50, 100
        sma1, sma2, sma3, rsi = indicators_sma_rsi.indicators(df[:-1], *sma_values)
        (
            support_list,
            resistance_list,
            fibonacci_uptrend,
            fibonacci_downtrend,
            pattern_list,
            support_above,
            support_below,
            resistance_below,
            resistance_above,
            x_dat,
        ) = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            "",
        )

        fibonacci_multipliers = 0.236, 0.382, 0.500, 0.618, 0.705, 0.786, 0.886
        # Chart settings
        (
            legend_color,
            chart_color,
            background_color,
            support_line_color,
            resistance_line_color,
        ) = ("#D8D8D8", "#E7E7E7", "#E7E7E7", "LightSeaGreen", "MediumPurple")
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0,
            row_width=[0.1, 0.1, 0.8],
        )

        def fibonacci_pricelevels(
            high_price, low_price
        ) -> tuple[list[float], list[float]]:
            """
            Uptrend Fibonacci Retracement Formula =>
            Fibonacci Price Level = High Price - (High Price - Low Price)*Fibonacci Level
            :param high_price: High price for the period
            :param low_price: Low price for the period
            """
            for multiplier in fibonacci_multipliers:
                retracement_levels_uptrend = (
                    low_price + (high_price - low_price) * multiplier
                )
                fibonacci_uptrend.append(retracement_levels_uptrend)
                retracement_levels_downtrend = (
                    high_price - (high_price - low_price) * multiplier
                )
                fibonacci_downtrend.append(retracement_levels_downtrend)
            return fibonacci_uptrend, fibonacci_downtrend

        def sensitivity(sens=2) -> tuple[list, list]:
            """
            Find the support and resistance levels for a given asset.
            sensitivity:1 is recommended for daily charts or high frequency trade scalping.
            :param sens: sensitivity parameter default:2, level of detail 1-2-3 can be given to function
            """
            for sens_row in range(3, len(df) - 1):
                if support_resistance.support(df, sens_row, 3, sens):
                    support_list.append((sens_row, df.low[sens_row]))
                if support_resistance.resistance(df, sens_row, 3, sens):
                    resistance_list.append((sens_row, df.high[sens_row]))
            return support_list, resistance_list

        def chart_lines():
            """
            Check if the support and resistance lines are above or below the latest close price.
            """
            # Find support and resistance levels
            # Check if the support is below the latest close. If it is, it is appending it to the list
            # support_below. If it isn't, it is appending it to the list resistance_below.
            all_support_list = tuple(map(lambda sup1: sup1[1], support_list))
            all_resistance_list = tuple(map(lambda res1: res1[1], resistance_list))
            print(all_support_list, all_resistance_list)
            latest_close = df["close"].iloc[-1]
            for support_line in all_support_list:  # Find closes
                if support_line < latest_close:
                    support_below.append(support_line)
                else:
                    resistance_below.append(support_line)
            if len(support_below) == 0:
                support_below.append(min(df.low))
            # Check if the price is above the latest close price. If it is, it is appending it to the
            # resistance_above list. If it is not, it is appending it to the support_above list.
            for resistance_line in all_resistance_list:
                if resistance_line > latest_close:
                    resistance_above.append(resistance_line)
                else:
                    support_above.append(resistance_line)
            if len(resistance_above) == 0:
                resistance_above.append(max(df.high))
            return fibonacci_pricelevels(max(resistance_above), min(support_below))

        def candlestick_patterns() -> list:
            """
            Takes in a dataframe and returns a list of candlestick patterns found in the dataframe then returns
            pattern list.
            """
            from candlestick import candlestick as cd

            nonlocal df
            all_patterns = [
                cd.inverted_hammer,
                cd.hammer,
                cd.doji,
                cd.bearish_harami,
                cd.bearish_engulfing,
                cd.bullish_harami,
                cd.bullish_engulfing,
                cd.dark_cloud_cover,
                cd.dragonfly_doji,
                cd.hanging_man,
                cd.gravestone_doji,
                cd.morning_star,
                cd.morning_star_doji,
                cd.piercing_pattern,
                cd.star,
                cd.shooting_star,
            ]
            # Loop through the candlestick pattern functions
            for pattern in all_patterns:
                # Apply the candlestick pattern function to the data frame
                df = pattern(df)
            # Replace True values with 'pattern_found'
            df.replace({True: "pattern_found"}, inplace=True)

            def pattern_find_func(pattern_row) -> list:
                """
                The function takes in a dataframe and a list of column names. It then iterates through the
                list of column names and checks if the column name is in the dataframe. If it is, it adds
                the column name to a list and adds the date of the match to another list.
                """
                t = 0
                pattern_find = [col for col in df.columns]
                for pattern_f in pattern_row:
                    if pattern_f == "pattern_found":
                        pattern_list.append(
                            (pattern_find[t], pattern_row["date"].strftime("%b-%d-%y"))
                        )  # pattern, date
                    t += 1
                return pattern_list

            return df.iloc[-3:-30:-1].apply(pattern_find_func, axis=1)

        def legend_candle_patterns() -> None:
            """
            The function takes the list of candlestick patterns and adds them to the chart as a legend text.
            """
            fig.add_trace(
                go.Scatter(
                    y=[support_list[0]],
                    name="----------------------------------------",
                    mode="markers",
                    marker=dict(color=legend_color, size=14),
                )
            )
            fig.add_trace(
                go.Scatter(
                    y=[support_list[0]],
                    name="Latest Candlestick Patterns",
                    mode="markers",
                    marker=dict(color=legend_color, size=14),
                )
            )
            for pat1, count in enumerate(pattern_list):  # Candlestick patterns
                fig.add_trace(
                    go.Scatter(
                        y=[support_list[0]],
                        name=f"{pattern_list[pat1][1]} : {str(pattern_list[pat1][0]).capitalize()}",
                        mode="lines",
                        marker=dict(color=legend_color, size=10),
                    )
                )

        def create_candlestick_plot() -> None:
            """
            Creates a candlestick plot using the dataframe df, and adds it to the figure.
            """
            fig.add_trace(
                go.Candlestick(
                    x=df["date"][:-1].dt.strftime(x_date),
                    name="Candlestick",
                    text=df["date"].dt.strftime(x_date),
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                ),
                row=1,
                col=1,
            )

        def draw_support() -> None:
            """
            Draws the support lines and adds annotations to the chart.
            """
            for s in range(len(support_list)):
                # Support lines
                fig.add_shape(
                    type="line",
                    x0=support_list[s][0] - 1,
                    y0=support_list[s][1],
                    x1=len(df) + 25,
                    y1=support_list[s][1],
                    line=dict(color=support_line_color, width=2),
                )
                # Support annotations
                fig.add_annotation(
                    x=len(df) + 7,
                    y=support_list[s][1],
                    text=str(support_list[s][1]),
                    font=dict(size=15, color=support_line_color),
                )

        def draw_resistance() -> None:
            """
            Draws the resistance lines and adds annotations to the chart.
            """
            for r in range(len(resistance_list)):
                # Resistance lines
                fig.add_shape(
                    type="line",
                    x0=resistance_list[r][0] - 1,
                    y0=resistance_list[r][1],
                    x1=len(df) + 25,
                    y1=resistance_list[r][1],
                    line=dict(color=resistance_line_color, width=1),
                )
                # Resistance annotations
                fig.add_annotation(
                    x=len(df) + 20,
                    y=resistance_list[r][1],
                    text=str(resistance_list[r][1]),
                    font=dict(size=15, color=resistance_line_color),
                )

            legend_support_resistance_values()
            text_and_indicators()
            legend_fibonacci()
            # Candle patterns for HTF
            if selected_timeframe in historical_hightimeframe:
                legend_candle_patterns()

        def chart_updates() -> None:
            """
            Updates the chart's layout, background color, chart color, legend color, and margin.
            """
            fig.update_layout(
                title=str(
                    f"{historical_data.ticker} {selected_timeframe.upper()} Chart"
                ),
                hovermode="x",
                dragmode="zoom",
                paper_bgcolor=background_color,
                plot_bgcolor=chart_color,
                xaxis_rangeslider_visible=False,
                legend=dict(bgcolor=legend_color, font=dict(size=11)),
                margin=dict(t=30, l=0, b=0, r=0),
            )
            fig.update_xaxes(showspikes=True, spikecolor="green", spikethickness=2)
            fig.update_yaxes(showspikes=True, spikecolor="green", spikethickness=2)

        def save():
            """
            Saves the image and html file of the plotly chart, then it tweets the image and text
            """

            if not os.path.exists("../images"):
                os.mkdir("../images")

            image = (
                f"../images/"
                f"{df['date'].dt.strftime('%b-%d-%y')[candle_count]}"
                f"{historical_data.ticker + '-' + selected_timeframe}.jpeg"
            )
            fig.write_image(image, width=1920, height=1080)  # Save image for tweet
            fig.write_html(
                f"../images/"
                f"{df['date'].dt.strftime('%b-%d-%y')[candle_count]}{historical_data.ticker + selected_timeframe}.html",
                full_html=False,
                include_plotlyjs="cdn",
            )
            with open('../templates/all_levels.html', 'a') as f:
                f.write('''<button class="accordion">''' + historical_data.ticker + '''</button>''')
                f.write('''<div class="panel">''')
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write('''</div>''')

            text_image = (
                f"#{historical_data.ticker} "
                f"{selected_timeframe} Support and resistance levels \n "
                f"{df['date'].dt.strftime('%b-%d-%Y')[candle_count]}"
            )

        sensitivity()
        chart_lines()
        # # Checking if the selected timeframe is in the historical_hightimeframe list.
        if selected_timeframe in historical_hightimeframe:
            candlestick_patterns()
            x_date = "%b-%d-%y"
        elif selected_timeframe in historical_lowtimeframe:
            x_date = "%H:%M %d-%b"
        create_candlestick_plot()
        chart_updates()
        save()
        # pinescript_code(historical_data.ticker, selected_timeframe, f_res_above, f_sup_below)
        print(
            f"Completed sup-res execution in {time.perf_counter() - now_supres} seconds"
        )
        print(f"Completed execution in total {time.perf_counter() - perf} seconds")
        return fig.show(id="the_graph", config={"displaylogo": False})


if __name__ == "__main__":
    file_name = historical_data.user_ticker.file_name
    file_name_mtf = historical_data.user_ticker_mtf.file_name
    file_name_ltf = historical_data.user_ticker_ltf.file_name

    try:
        try:
            os.remove('../templates/all_levels.html')
        except OSError:
            pass
        perf = time.perf_counter()
        if os.path.isfile(file_name):  # Check .csv file exists
            print(f"{file_name} downloaded and created.")
            Supres.main(file_name, historical_data.time_frame)
            Supres.main(file_name_mtf, historical_data.med_time_frame)
            Supres.main(file_name_ltf, historical_data.low_time_frame)

            print("Data analysis is done. Browser opening.")

            os.remove(file_name)  # remove the .csv file
            print(f"{file_name} file deleted.")

            os.remove(file_name_mtf)  # remove the .csv file
            print(f"{file_name_mtf} file deleted.")

            os.remove(file_name_ltf)  # remove the .csv file
            print(f"{file_name_ltf} file deleted.")


        else:
            raise print(
                "One or more issues caused the download to fail. "
                "Make sure you typed the filename correctly."
            )
    except KeyError:
        os.remove(file_name)
        raise KeyError("Key error, algorithm issue")
