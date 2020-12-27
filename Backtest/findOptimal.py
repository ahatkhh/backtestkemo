import itertools
import numpy as np
from Backtest.backTrader import BackTrader
from Backtest.datareader import getData
from tqdm import tqdm


if __name__ == "__main__":
    critDistances = itertools.chain(range(10, 100, 10), range(100, 500, 50), range(500, 1500, 100))
    paddingRatios = np.arange(0.05, 0.3, 0.05)
    avg_ps = np.arange(0.0003, 0.003 , 0.0003)
    fma_days = np.arange(1, 10, 2)
    sma_days = itertools.chain(np.arange(10, 30, 5), np.arange(30, 60, 10))

    data = getData("^IXIC", "2015-01-01", "2016-11-30")  # NASDAQ

    max_result = 0
    progress = 0
    f = open("data.txt", 'w')

    for critDistance in tqdm(critDistances):
        for paddingRatio in tqdm(paddingRatios):
            for avg_p in tqdm(avg_ps):
                for fma_day in fma_days:
                    for sma_day in sma_days:
                        myStrategy = MyStrategy(critDistance=critDistance, paddingRatio=paddingRatio, buyRatio=0.8, avg_p=avg_p,
                                                fma_tick=fma_day, sma_tick=sma_day)
                        trader = BackTrader(data=data, cash=1000000, commission=0.00015, strategy=myStrategy)
                        trader.run()

                        parameters = (trader.result, critDistance, paddingRatio, avg_p, fma_day, sma_day)
                        f.write(f"{trader.result} {critDistance} {paddingRatio} {avg_p} {fma_day} {sma_day}")
                        f.write("\n")
                        f.flush()

                        if trader.result > max_result:
                            print(parameters)
                            max_result = trader.result


