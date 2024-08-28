import pandera as pa
import pandas as pd

schema = pa.DataFrameSchema({
    "asset_name": pa.Column(pa.String),
    "theta_value": pa.Column(pa.Float),
    "overshoot_value": pa.Column(pa.Float),
    "current_price": pa.Column(pa.Float),
    "current_run": pa.Column(pa.String),
    "last_high": pa.Column(pa.Float),
    "last_low": pa.Column(pa.Float)
})