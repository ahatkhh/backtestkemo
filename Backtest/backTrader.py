import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.dates as mdates

from Strategy.strategy import Broker


class BackTrader:
    def __init__(self, data, cash, commission, strategy):
        self.data = data
        self.cash = cash
        self.commission = commission
        self.strategy = strategy

        self.tradeData = pd.DataFrame(index=data.index, columns=['close', 'cash', 'total'])
        self.result = 0

    def run(self, tqdm_func, global_tqdm):
        broker = BackTraderBroker(self.cash, self.commission)
        self.strategy.broker = broker

        # print("MyBackTrader running..")
        # print(f"from: {self.data.index[0].date()}, to: {self.data.index[-1].date()}", flush=True)
        count = len(self.data.index)
        with tqdm_func(total=count, bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}") as progress:
            progress.set_description(str.rjust(self.strategy.name, 20))
            for i in range(count):
                broker.price = self.data['Close'][i]
                broker.time = self.data.index[i]
                self.strategy.next()

                row = self.tradeData.iloc[i]
                row['close'] = self.data['Close'][i]
                row['cash'] = broker.cash
                row['total'] = broker.total

                if (i+1) % 5000 == 0:
                    progress.update(5000)
                    global_tqdm.update(5000)

            remain = count % 5000
            progress.update(remain)
            global_tqdm.update(remain)

        self.strategy.end()
        self.result = broker.total

    def plot(self):
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 4])
        x = self.data.index

        max_draw = 2000
        step = 1
        if len(x) > max_draw:
            step = len(x) // max_draw + 1

        # 현재가와 거래량
        ax1 = plt.subplot(gs[1])
        ax1.plot(x[::step], self.data['Close'][::step], color='black', markersize=0, alpha=1, label='Close')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price ($)')
        ax1.tick_params(axis='y', direction='in')

        ax2 = ax1.twinx()
        ax2.bar(x[::step], self.data['Volume'][::step], color='deeppink', label='Volume', alpha=0.4, width=(x[0]-x[1])*step)
        ax2.set_ylabel('Volume')
        ax2.tick_params(axis='y', direction='in')

        ax1.set_zorder(ax2.get_zorder() + 10)
        ax1.patch.set_visible(False)

        # 현금과 총액, 최종가
        ax3 = plt.subplot(gs[0], sharex=ax1)
        ax3.get_shared_x_axes().join(ax1, ax3)
        ax3.plot(x[::step], self.tradeData['total'][::step], '-s', color='black', markersize=0, alpha=1, label='total')
        ax3.plot(x[::step], self.tradeData['cash'][::step], '-s', color='yellow', markersize=0, alpha=1, label='cash')
        ax3.text(x[-1], self.tradeData['total'][-1], round(self.tradeData['total'][-1]),
                 fontsize=10, horizontalalignment="left", verticalalignment="center")

        plt.setp(ax3.get_xticklabels(), visible=False)

        # strategy에서 직접 그리는 plot
        for pdict in self.strategy.plots:
            values = pdict["values"]
            params = pdict.get("params", {})

            if pdict.get("onCash", False) is True:
                ax = ax3
            else:
                ax = ax1

            if pdict.get("toBack", False) is True:
                ax_temp = ax.twinx()
                ax.get_shared_y_axes().join(ax, ax_temp)
                ax_temp.set_zorder(ax.get_zorder()-10)
                ax_temp.axis('off')
                ax = ax_temp

            if pdict.get("scatter", False) is True:
                x = pdict["x"]
                ax.scatter(x, values, **params)
            elif pdict.get("text", False) is True:
                x = pdict["x"]
                y = pdict["y"]
                for i, v in enumerate(x):
                    ax.text(v, y[i], values[i], **params)
            else:
                x = self.data.index
                step = 1
                if len(x) > max_draw:
                    step = len(x) // max_draw + 1
                ax.plot(x[::step], values[::step], **params)


        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # remove vertical gap between subplots
        plt.subplots_adjust(hspace=.0)

        # 제목
        label = self.strategy.name
        plt.title(label=label)

        plt.show()

class BackTraderBroker(Broker):
    def __init__(self, cash, commission):
        super().__init__()
        self.cash = cash
        self.commission = commission

    def buy(self, amount):
        self.cash -= amount * self.price * (1 + self.commission)
        self.boughtAmount += amount

    def sell(self, amount):
        self.cash += amount * self.price * (1 - self.commission)
        self.boughtAmount -= amount

    def close(self):
        self.sell(self.boughtAmount)

