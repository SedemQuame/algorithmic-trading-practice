Experiment Readme: Algo Trading using SMA for 15-minute timeframe for Volatility Indices on the Deriv Platform

Overview:
This experiment aims to implement an algorithmic trading strategy using the Simple Moving Average (SMA) indicator for volatility indices on the Deriv platform, for a 15-minute timeframe. The strategy involves buying and selling a volatility index based on the crossover of the 15-minute SMA and the price of the index. The experiment will be conducted using the Deriv API and Python as the programming language.

Data:
Data will be obtained through the Deriv API which provides real-time and historical data for various volatility indices, including the V10, V50, and V100. The data should include the open, high, low, and close prices of the volatility index for each 15-minute interval.

Dependencies:
Python 3.7 or higher
Pandas
Matplotlib
Deriv API


Strategy:
The strategy is to buy a volatility index when the 15-minute SMA crosses above the price of the index and sell the index when the 15-minute SMA crosses below the price of the index.
The strategy involves the following steps:
Connect to the Deriv API to retrieve real-time and historical data for the desired volatility index.
Calculate the 15-minute SMA using the close prices of the volatility index.
Buy the volatility index when the current price of the index is greater than the 15-minute SMA and the previous price of the index is less than or equal to the 15-minute SMA.
Sell the volatility index when the current price of the index is less than the 15-minute SMA and the previous price of the index is greater than or equal to the 15-minute SMA.
Monitor the performance of the strategy and adjust parameters such as the SMA period and trading threshold as necessary.

Note: Trading on volatility indices involves a high degree of risk and should only be attempted by experienced traders with a thorough understanding of the market and its volatility. It is important to practice proper risk management techniques and to never invest more than you can afford to lose.
