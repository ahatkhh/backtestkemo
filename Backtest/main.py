import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)
from Backtest.backTrader import BackTrader
from Backtest.datareader import getBitcoinData, getAny
from Strategy.kemo_strategy import Kemo_Strategy
from Strategy.kemo_strategy2 import Kemo_Strategy2
from Strategy.dca_strategy1 import DCA_Strategy1
from Strategy.dca_strategy2 import DCA_Strategy2
from Strategy.dca_strategy3 import DCA_Strategy3
from Strategy.dca_strategy4 import DCA_Strategy4
from tqdm_multiprocess import TqdmMultiProcessPool
from tqdm import tqdm

import yfinance as yf


def trade(strategy, data, tqdm_func=None, global_tqdm=None):
    trader = BackTrader(data=data, cash=300, commission=0.001, strategy=strategy)
    trader.run(tqdm_func=tqdm_func, global_tqdm=global_tqdm)
    trader.plot()

def multiprocess(data, strategies):
    params = [(s, data) for s in strategies]

    def on_error(result):
        pass

    def on_done(result):
        pass

    pool = TqdmMultiProcessPool(4)
    with tqdm(total=len(data.index)*len(params), bar_format="{l_bar}{bar:35}{r_bar}{bar:-10b}") as global_progress:
        global_progress.set_description("total")
        pool.map(global_progress, [(trade, params[i]) for i in range(len(params))], on_error, on_done)

def test1():
    data = getAny("2019-08-10", "2020-12-20")
    # ticker = yf.Ticker('^IXIC')
    # data = ticker.history(start="2010-06-01", end="2012-04-01", interval="1h")
    # keys: Open, High, Low, Close, Volume, Dividends, Stork Splits

    strategies = [DCA_Strategy1(), DCA_Strategy2()]
    # , DCA_Strategy2(), DCA_Strategy3(), DCA_Strategy4()
    # strategy = DCA_Strategy()
    # strategy.trigPs = [pow(1.5, i)/100 for i in range(0, 6)]
    # strategy.invests = [i / 250 for i in [15, 15, 15, 15, 20, 20, 20]]
    # strategy.profitP = 0.03
    # strategy.trail_profit = 0.005
    # strategy.trail_dca = 0.005
    # strategy.stopLossP = 0.15
    # strategy.name = 'mydca'
    # strategies.append(strategy)

    multiprocess(data, strategies)

if __name__ == "__main__":
    os.system('cls')
    test1()

