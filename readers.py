# import pandas_datareader as pd
# df = pd.DataReader("000540.KS", "yahoo")
# df = df[-10:-1].astype(int)
# print(df)
#
# ss = (sum(df["Close"])+36450) / 10
# ss = int(ss)
# print(ss)

#
# import yfinance as yf
#
# sample = yf.Ticker("000080.KS")
# df = sample.history(period="max")
# print(df)
#
# df = df[-10:-1].astype(int)
# print(df)