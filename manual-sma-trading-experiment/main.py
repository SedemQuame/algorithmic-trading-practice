#!/usr/bin/python3

import pandas as pd
import numpy as np
import pprint
import matplotlib.pyplot as plt

symbols = ["vix10_1s.csv", "vix10.csv", "vix25_1s.csv", "vix25.csv", "vix50.csv", "vix50_1s.csv", "vix75_1s.csv", "vix75.csv", "vix100_1s.csv", , "vix75_1s.csv"]


def main(symbol):
    historical_data = f"./{symbol}"
    data = pd.read_csv(historical_data)

    # add new column with 8-hour intervals
    data["Datetime"] = pd.to_datetime(data["Date"] + " " + data["Time"])
    # data['Datetime'] = data['Datetime'].apply(lambda x: x.replace(minute=(x.minute // 15) * 15, second=0))
    data.set_index("Datetime", inplace=True)

    # print data info
    pprint.pprint(f"Data info.\n {data.info()}")

    # print data tail()
    pprint.pprint(f"Data tail.\n {data.tail()}")

    # get VOLATILITY 10(1s) asset price.
    data = pd.DataFrame(data["Open"])
    # replace comma with empty string and convert to numeric values
    # data['Price'] = pd.to_numeric(data['Price'].str.replace(',', ''))

    print(f"{symbol} Price")

    # using the simple moving average strategy.
    data["SMA1"] = data["Open"].rolling(window=10).mean()
    data["SMA2"] = data["Open"].rolling(window=30).mean()
    data.dropna(inplace=True)

    # create a subplot for price data and SMA strategy
    fig, axs1 = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True)

    axs1[0].plot(data["Open"], label="Price")
    axs1[0].plot(data["SMA1"], label="SMA1")
    axs1[0].plot(data["SMA2"], label="SMA2")
    axs1[0].set_title(f"{symbol} price, with SMA 10 and 30")
    axs1[0].legend()

    # Generating market positioning, based on relationship between the SMAs.
    data["position"] = np.where(data["SMA1"] > data["SMA2"], 1, -1)
    data.dropna(inplace=True)

    # plot the market positioning on the second subplot
    axs1[1].plot(data["position"], color="green")
    axs1[1].set_title("Market Positioning")
    axs1[1].set_ylim([-1.1, 1.1])
    plt.show()

    # create a plot for returns of the given strategy
    data["returns"] = np.log(data["Open"] / data["Open"].shift(1))
    data["returns"].hist(bins=35, figsize=(10, 6))
    data.dropna(inplace=True)
    plt.show()

    # create a plot for price strategy.
    # derive the log returns of the strategy given the positionings and the market returns.
    data["strategy"] = data["position"].shift(1) * data["returns"]
    pprint.pprint(f"Data tail with strategy.\n {data.tail()}")

    # sums up the single log return values for both the stock and the strategy.
    data[["returns", "strategy"]].sum()
    pprint.pprint(f"Sum of returns and strategy.\n{data}")

    # applies the exponential function of the sum of the log returns to calculate
    # gross performance
    data[["returns", "strategy"]].sum().apply(np.exp)
    pprint.pprint(f"Sum of returns and strategy.\n{data}")

    data[["returns", "strategy"]].cumsum().apply(np.exp).plot(figsize=(10, 6))
    plt.show()


if __name__ == "__main__":
    for symbol in symbols:
        main(symbol)
