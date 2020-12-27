from Strategy.strategy import Strategy
import pandas as pd
from datetime import datetime

class Kemo_Strategy2(Strategy):
    STATE_REV = 1
    STATE_PRO = 2

    def __init__(self, isRealTime=False):
        super().__init__()
        self.isRealTime = isRealTime

        # parameters
        self.rev_sellTrigP = 0.015
        self.rev_rebuyTrigP = 0.035
        self.rev_sellP = 0.4
        self.rev_aboveAverage = 0.05
        self.rev_invests = [100/1500, 25/1500, 25/1500, 25/1500, 50/1500, 50/1500, 50/1500, 0, 100/1500, 0, 125/1500, 0, 150/1500, 0, 200/1500, 0, 300/1500, 0, 300/1500]
        self.rev_maxInvestInterval = 20

        self.pro_maxProfit = 1
        self.pro_sellP_total = 1
        self.pro_sellNum = 10

        self.trail_back = 0.01

        # inner values
        self.initialCash = 0
        self.initialPrice = 0
        self.initialBought = 0

        self.rev_average = 0
        self.rev_intervals = []
        self.rev_intervalNum = 0

        self.rev_in = True # my money is in? or sold?
        self.rev_soldValue = 0 # latest sell value

        self.rev_trailHighest = 0
        self.rev_trailLowest = 100000000000

        self.pro_sellP = self.pro_sellP_total / self.pro_sellNum
        self.pro_intervals = [1 + self.pro_maxProfit / self.pro_sellNum * i for i in range(0, self.pro_sellNum + 1)]
        self.pro_intervalNum = 0
        self.pro_trailHighest = 0
        self.pro_trailLowest = 100000000000
        self.pro_initialAmount = 0

        self.state = 0

        # for plotting
        self.events = [] # [{"type": "REV Sell", "time":, "price":, "average":, "total":,}, ...]
        self.boughtTotal = []
        self.averages = []

    def next(self):
        super().next()

        # initial buy
        if self.initialPrice == 0:
            self.initialCash = self.broker.cash
            self.initialPrice = self.broker.price

            self.rev_average = self.broker.price
            self.rev_intervals = [self.broker.price * (1 - self.rev_sellTrigP)]
            self.rev_intervalNum = 0
            self.rev_in = True
            self.rev_trailHighest = 0
            self.rev_trailLowest = 100000000000

            self.pro_intervalNum = 0

            self.state = Kemo_Strategy2.STATE_REV

            afford = self.initialCash * self.rev_invests[0]
            self.initialBought = afford / self.broker.price

            self.buy(self.initialBought)
            self._handleEvent({"type": "Start", "time": self.broker.time, "price": self.broker.price, "average": self.rev_average,
                               "total": self.broker.total})
        # rev zone
        elif self.broker.price < self.rev_average:
            # in sell position
            if self.rev_in:
                if self.broker.price < self.rev_intervals[-1]:
                    cash = self.broker.cash
                    self.sell(self.broker.boughtAmount * self.rev_sellP)
                    self.rev_soldValue = self.broker.cash - cash
                    self.rev_intervalNum += 1
                    self.rev_in = False
                    self.rev_average = (self.initialCash - self.broker.cash) / self.broker.boughtAmount
                    self.state = Kemo_Strategy2.STATE_REV
                    self._handleEvent(
                        {"type": "Rev Sell", "time": self.broker.time, "price": self.broker.price, "average": self.rev_average,
                         "total": self.broker.total})
            # in rebuy position
            else:
                self.rev_trailLowest = min(self.rev_trailLowest, self.broker.price)
                if self.rev_trailLowest < self.broker.price < self.rev_intervals[-1] * (1 - self.rev_rebuyTrigP):
                    if self.broker.price > self.rev_trailLowest * (1 + self.trail_back):      # rebuy
                        investRatio = self.rev_invests[self.rev_intervalNum] if self.rev_intervalNum < len(self.rev_invests) else 0
                        invest = self.initialCash * investRatio
                        self.buy((invest + self.rev_soldValue) / self.broker.price / (1+self.broker.commission))
                        self.rev_in = True
                        self.rev_average = (self.initialCash - self.broker.cash) / self.broker.boughtAmount
                        self.rev_intervals.append(self.broker.price * (1 - self.rev_sellTrigP))
                        self.rev_trailLowest = self.broker.price
                        self.state = Kemo_Strategy2.STATE_REV
                        self._handleEvent(
                            {"type": "Rev Rebuy", "time": self.broker.time, "price": self.broker.price, "average": self.rev_average,
                             "total": self.broker.total})
        # profit zone
        else:
            if self.state == Kemo_Strategy2.STATE_REV:
                self.state = Kemo_Strategy2.STATE_PRO
                self.pro_initialAmount = self.broker.boughtAmount

            self.pro_trailLowest = min(self.pro_trailLowest, self.broker.price)
            self.pro_trailHighest = max(self.pro_trailHighest, self.broker.price)

            # selling position
            intervalNum = self.pro_intervalNum
            while intervalNum < self.pro_sellNum and\
                    self.pro_trailHighest > self.broker.price > self.pro_intervals[intervalNum + 1] * self.rev_average:
                intervalNum += 1

            if intervalNum > self.pro_intervalNum and self.broker.price < self.pro_trailHighest * (1 - self.trail_back):
                self.sell(self.pro_sellP * self.pro_initialAmount * (intervalNum - self.pro_intervalNum))
                self.pro_intervalNum = intervalNum
                self.pro_trailLowest = self.broker.price
                self._handleEvent(
                    {"type": "Pro Sell", "time": self.broker.time, "price": self.broker.price, "average": self.rev_average,
                     "total": self.broker.total})
                if intervalNum >= self.pro_sellNum:
                    self.close()
                    self._handleEvent(
                        {"type": "Reset", "time": self.broker.time, "price": self.broker.price, "average": self.rev_average,
                         "total": self.broker.total})
                    self.initialPrice = 0

            # rebuying position
            intervalNum = self.pro_intervalNum
            while intervalNum > 0 and\
                    self.pro_trailLowest < self.broker.price < self.pro_intervals[intervalNum - 1] * self.rev_average:
                intervalNum -= 1

            if intervalNum < self.pro_intervalNum and self.broker.price > self.pro_trailLowest * (1 + self.trail_back):
                self.buy(self.pro_sellP * self.pro_initialAmount * (self.pro_intervalNum - intervalNum))
                self.pro_intervalNum = intervalNum
                self.pro_trailHighest = self.broker.price
                self._handleEvent(
                    {"type": "Pro Rebuy", "time": self.broker.time, "price": self.broker.price, "average": self.rev_average,
                     "total": self.broker.total})

        if not self.isRealTime:
            self.boughtTotal.append(self.broker.boughtTotal)
            self.averages.append(self.rev_average)

    def end(self):
        super().end()
        df = pd.DataFrame(self.events)
        if len(df) == 0:
            return

        df = df.set_index("time")
        # print(df)

        # log df
        f = open("log.txt", "a+")
        f.write("\n")
        f.write(str(datetime.now()) + "\n")
        f.write(self.name + "\n")
        f.write(df.to_string())
        f.write("\n")

        # draw bought total and average
        self.plots.append({"values": self.boughtTotal, "params": {"color": "blue"}, "onCash": True})
        self.plots.append({"values": self.averages, "params": {"color": "orange", "linewidth": 0.5}, "toBack": True})

        # draw selling and rebuying dates
        df_rev_sell = df.loc[df["type"] == "Rev Sell"]
        self.plots.append({"values": df_rev_sell["price"], "scatter": True,
                           "x": df_rev_sell.index, "params": {"color": "blue"}})

        df_rev_rebuy = df.loc[df["type"] == "Rev Rebuy"]
        self.plots.append({"values": df_rev_rebuy["price"], "scatter": True,
                           "x": df_rev_rebuy.index, "params": {"color": "red"}})

        df_pro_sell = df.loc[df["type"] == "Pro Sell"]
        self.plots.append({"values": df_pro_sell["price"], "scatter": True,
                           "x": df_pro_sell.index, "params": {"color": "cyan"}})

        df_pro_rebuy = df.loc[df["type"] == "Pro Rebuy"]
        self.plots.append({"values": df_pro_rebuy["price"], "scatter": True,
                           "x": df_pro_rebuy.index, "params": {"color": "yellow"}})

        # draw system reset dates
        df_reset = df.loc[df["type"] == "Reset"]

        self.plots.append({"values": df_reset["price"], "scatter": True, "x": df_reset.index,
                           "params": {"color": "green"}})
        self.plots.append({"values": df_reset["total"], "scatter": True, "x": df_reset.index,
                           "params": {"color": "green"}, "onCash": True})
        self.plots.append(
            {"values": [round(n) for n in df_reset["total"]], "text": True, "x": df_reset.index,
             "y": df_reset["total"],
             "params": {"fontsize": 7, "horizontalalignment": "center", "verticalalignment": "bottom"},
             "onCash": True})

    def _handleEvent(self, event):
        if self.isRealTime:
            print(f"{event}")
        else:
            self.events.append(event)