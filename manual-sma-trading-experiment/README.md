Experiment Readme: Manual Export of Volatility Index Data

Overview:
This experiment aims to analyze the historical data of a volatility index manually exported from the Deriv platform. The experiment will involve exporting the data from the Deriv platform and analyzing it using Python as the programming language.

Data:
Data will be obtained by manually exporting the historical data for a desired volatility index from the Deriv platform. The data should include the open, high, low, and close prices of the volatility index for each 15-minute interval. The exported data should be in a CSV format.

Dependencies:

Python 3.7 or higher
Pandas
Matplotlib
Steps:

Log in to your Deriv account and navigate to the desired volatility index.
Set the timeframe to 15 minutes and select the desired date range for the historical data.
Click on the "Export" button and select the CSV format.
Save the CSV file to your local computer.
Data Analysis:

Load the exported data into a Pandas DataFrame using Python.
Calculate the 15-minute SMA using the close prices of the volatility index.
Plot the volatility index and the 15-minute SMA on a Matplotlib chart to visualize the crossover points.
Analyze the performance of the strategy based on the crossover points and adjust the parameters such as the SMA period and trading threshold as necessary.
Note: Manual exporting of historical data can be time-consuming and may not be suitable for traders who require real-time data. Using the Deriv API, as described in the previous experiment readme, can provide a more efficient and automated solution for accessing historical and real-time data.
