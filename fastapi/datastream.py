import asyncio
import pandas as pd

# Load the data into a Pandas dataframe
df = pd.read_csv('dax_tick_data.csv', sep=";")  # Replace with the actual path to your CSV file

# Ensure the dataframe is sorted by the timestamp
df = df.sort_values(by='Date')


# Asynchronous generator to simulate data stream
async def stream_data():
    for index, row in df.iterrows():
        await asyncio.sleep(0.1)  # Simulate a delay for live streaming
        yield row
