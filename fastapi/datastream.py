import asyncio
import pandas as pd
import numpy as np

# Load the data into a Pandas dataframe
df = pd.read_csv('dax_tick_data.csv', sep=";")  # Replace with the actual path to your CSV file

# Ensure the dataframe is sorted by the timestamp
df = df.sort_values(by='Date')


# Asynchronous generator to simulate data stream
async def stream_data():
    for index, row in df.iterrows():
        await asyncio.sleep(0.1)  # Simulate a delay for live streaming
        yield row


async def stream_artificial_data():
    df = create_artificial_data()
    for index, row in df.iterrows():
        await asyncio.sleep(.1)
        yield row


def create_artificial_data() -> pd.DataFrame:
    # np.random.seed(42)
    periods = 100000
    sigma = 1
    mean = 100
    dates = pd.date_range("2024-01-01", periods=periods, freq="s")
    values = sigma * np.random.randn(periods).cumsum() + mean

    # Create a DataFrame from the generated data
    data = pd.DataFrame({'date': dates, 'Midprice': values})

    # Set the 'date' column as the index
    data.set_index('date', inplace=True)

    return data
