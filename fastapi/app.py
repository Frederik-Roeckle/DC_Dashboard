import pandas as pd
import pandera as pa
from pandera.typing import DataFrame
import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn

import datastream

app = FastAPI()

result_df = pd.DataFrame()

lock = asyncio.Lock()

# @pa.check_types
def initialize_result_dataframe() -> pd.DataFrame:
    # Read .env with the theta values, asset_classes, etc
    datastructure = {
        "asset_name": ["DAX","DAX", "DAX"],
        "theta_value": [0.003, 0.005, 0.01],
        "overshoot_value": [-1.0, -1.0, -1.0],
        "current_run": [None, None, None],
        "current_price": [None, None, None],
        "last_high_price": [-1.0, -1.0, -1.0],
        "last_low_price": [-1.0, -1.0, -1.0],
        "current_price_timestamp": [None, None, None],
        "last_low_price_timestamp": [None, None, None],
        "last_high_price_timestamp": [None, None, None]
    }
    return pd.DataFrame(datastructure)


def update_last_high_and_last_low_price(last_high_price, last_low_price, current_price, current_run) -> tuple:
    if current_run == "Downward":
        last_low_price = min(last_low_price, current_price)
    if current_run == "Upward":
        last_high_price = max(last_high_price, current_price)
    return last_high_price, last_low_price

# Function to detect directional changes
def detect_directional_change(last_high_price, last_low_price, current_price, theta_value, current_run) -> tuple:
    """

    :param last_high_price:
    :param last_low_price:
    :param current_price:
    :param theta_value:
    :param current_run:
    :return:
    """

    if current_run is None:
        current_run = "Upward"

    # Update the high and low prices during a respective Upward or Downward run
    last_high_price, last_low_price = update_last_high_and_last_low_price(last_high_price, last_low_price, current_price, current_run)


    # Detect Downturn event
    if current_run == "Upward":
        if current_price <= last_high_price * (1 - theta_value):
            # Downturn event
            print(f"Downturn event registered! Current price: {current_price} and last high price: {last_high_price} for"
                  f" theta value: {theta_value}.")
            current_run = "Downward"
            # reset low price away from global extrema
            last_low_price = current_price

    # Detect Upward event
    elif current_run == "Downward":
        if current_price >= last_low_price * (1 + theta_value):
            print(
                f"Upturn event registered! Current price: {current_price} and last low price: {last_low_price} for"
                f" theta value: {theta_value}.")
            current_run = "Upward"
            last_high_price = current_price


    return current_run, last_high_price, last_low_price

def calculate_overshoot_value(current_price, current_run, last_high_price, last_low_price, theta) -> float:
    if current_run == "Upward":
        overshoot_value = abs(current_price - last_low_price) / (last_low_price * theta)
        return overshoot_value
    if current_run == "Downward":
        overshoot_value = abs(current_price - last_high_price) / (last_high_price * theta)
        return overshoot_value
    return -1.0


# Main function to process data and detect directional changes
async def process_data():
    global result_df
    data_stream = datastream.stream_data()

    async for row in data_stream:
        async with lock:
            for i, row_df in result_df.iterrows():

                df_last_high_price = row_df["last_high_price"]
                df_last_low_price = row_df["last_low_price"]
                df_theta_value = row_df["theta_value"]
                df_current_run = row_df["current_run"]


                current_price = row["Midprice"]

                # print(f"last_price {df_last_price}, current_price: {current_price}, theta_value: {df_theta_value}")

                # Init last_high_price and last_low_price
                if df_last_high_price == -1.0 or df_last_low_price == -1.0:
                    df_last_high_price = df_last_low_price = current_price

                # Detect directional changes
                df_current_run, df_last_high_price, df_last_low_price = detect_directional_change(
                    df_last_high_price, df_last_low_price, current_price, df_theta_value, df_current_run)

                # Compute overshoot value
                overshoot_values = calculate_overshoot_value(current_price, df_current_run, df_last_high_price,
                                                             df_last_low_price, df_theta_value)


                result_df.at[i, "last_high_price"] = df_last_high_price
                result_df.at[i, "last_low_price"] = df_last_low_price
                result_df.at[i, "theta_value"] = df_theta_value
                result_df.at[i, "current_run"] = df_current_run

                result_df.at[i, "overshoot_value"] = overshoot_values
                result_df.at[i, "current_price"] = current_price



# Endpoint to get the current run and price
@app.get("/data")
async def get_current_run():
    return result_df


# Start the processing coroutine
@app.on_event("startup")
async def startup_event():
    global result_df
    result_df = initialize_result_dataframe()
    asyncio.create_task(process_data())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
