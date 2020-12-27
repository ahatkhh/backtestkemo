import pandas_datareader
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.parser import parse
import os

def getData(code, start_date, end_date):
    ticker = yf.Ticker(code)
    df = ticker.history(start=start_date, end=end_date)

    # type: dataframe
    # keys: Open, High, Low, Close, Volume, Dividends, Stork Splits
    return df

def getBitcoinData(start_date, end_date):
    print("Start reading bitcoin data..")
    path = os.path.dirname(os.path.abspath(__file__))
    data = pd.read_csv(path + "\\data\\bitstampUSD_1-min_data_2018-03-01_to_2020-09-14.csv")
    data['DateTime'] = [datetime.fromtimestamp(ts/1000) for ts in data["Timestamp"]]
    data = data.set_index('DateTime')
    data = data.rename(columns={'Volume_(BTC)': 'Volume'})
    data = data.dropna()
    data = data[parse(start_date): parse(end_date)]
    print("Reading complete")

    return data

def getAny(start_date, end_date):
    print("Start reading data..")
    path = os.path.dirname(os.path.abspath(__file__))
    data = pd.read_csv(path + "\\data\\FTX5BEARUSD.csv")
    data['DateTime'] = [datetime.fromtimestamp(ts) for ts in data["Timestamp"]]
    data = data.set_index('DateTime')
    data = data.dropna()
    data = data.sort_index()[parse(start_date): parse(end_date)]
    print("Reading complete")

    return data

if __name__ == "__main__":
    ticker = yf.Ticker("MNQ=F")
    df = ticker.history(period="max")
    print(type(df.index[0]))
    print(df.index[0])

