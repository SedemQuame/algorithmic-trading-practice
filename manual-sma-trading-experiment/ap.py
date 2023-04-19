import pandas as pd
import matplotlib.pyplot as plt

# Read CSV data
df = pd.read_csv('vix50_1s.csv')

# Convert date and time columns to datetime format
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Set datetime column as index
df.set_index('Datetime', inplace=True)

# Calculate SMA20
sma20 = df['Close'].rolling(window=20).mean()

# Resample to 15-minute timeframe
sma20_15min = sma20.resample('15T').last()

# Plot SMA20 on 15-minute timeframe
plt.plot(sma20_15min.index, sma20_15min.values)
plt.show()
