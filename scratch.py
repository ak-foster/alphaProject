import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np


# Pre-processing for now, will include in __main__ later. Configure data source
today = datetime.date.today()
df = pd.read_csv('historicalPriceData.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
dfl = df['2016-01-01':today]

# dfl.to_csv('test.csv')
