from abc import ABCMeta, abstractmethod

class Broker(metaclass=ABCMeta):
    def __init__(self):
        self.cash = 0
        self.commission = 0
        self.boughtAmount = 0
        self.price = 0
        self.time = None

    @abstractmethod
    def buy(self, amount):
        pass

    @abstractmethod
    def sell(self, amount):
        pass

    @abstractmethod
    def close(self):
        pass

    @property
    def total(self):
        return self.cash + self.boughtTotal

    @property
    def boughtTotal(self):
        return self.price * self.boughtAmount * (1 - self.commission)

class Strategy:
    def __init__(self):
        self.tickCount = 0
        self.plots = []  # 그릴 그래프 목록: {"values":, "params": {plot parameters}}
        self.name = type(self).__name__
        self.broker = None

    def next(self):
        self.tickCount += 1

    def end(self):
        pass

    def buy(self, amount):
        self.broker.buy(amount)

    def sell(self, amount):
        self.broker.sell(amount)

    def close(self):
        self.broker.close()


# 현재가가 이동평균선 위로 올라갈 때 매수, 아래로 내려갈 때 매도
class MovingAverageStrategy(Strategy):
    def __init__(self, num):
        super().__init__()
        self.num = num
        self.prices = []
        self.averages = []

    def next(self):
        super().next()
        self.prices.append(self.broker.price)

        if len(self.prices) >= self.num:
            average = sum(self.prices[-self.num:]) / self.num
            self.averages.append(average)

            # 구매
            if self.broker.boughtAmount == 0:
                if self.prices[-2] < average < self.prices[-1]:
                    self.buy(int(self.broker.cash / self.broker.price))
            # 전부 판매
            else:
                if self.prices[-2] > average > self.prices[-1]:
                    self.close()
        else:
            self.averages.append(None)

    def end(self):
        self.plots.append({"values": self.averages, "color": "blue"})


# class MyStrategy(Strategy):
#     """ MyStrategy(v2)
#         20.12.11 broker 구조 수정으로 동작하지 않음
#
#         v2 추가:
#         그래프가 한 방향으로 이동하는 추세일 때 trend following으로 전략 변경
#         기준: fma_tick 이평선이 sma_tick 이평선을 추월하고 sma_tick 평균 증감율이 avg_p*100% 이상
#
#         매수포지션과 매도포지션을 동시에 구매 -> 둘 다 구매하지 않음
#         그래프가 한 쪽으로 이동한 후 반대 방향으로 이동을 시작하면 해당 방향에서 손실이 나는 포지션을 매도 -> 다른 포지션을 매수
#         매수와 매도를 하는 가격 기준선을 일정한 간격으로 설정
#         진동에 의한 손해를 방지하기 위해 가격 기준선 위아래로 패딩을 추가해 매수기준선, 매도기준선을 설정
#         이미 이익을 본 구간은 재매수하지 않음
#     """
#
#     # critDistance: 기준선 간격
#     # paddingRatio: 기준선에 적용할 패딩 비율
#     # buyRatio: 총 현금 대비 구매할 비율
#     def __init__(self, *, critDistance, paddingRatio=0.1, buyRatio=0.8, fma_tick=5, sma_tick=30, avg_p=0.0011):
#         super().__init__()
#         self.BUY_RATIO = buyRatio
#         self.CRIT_DISTANCE = critDistance  # 기준선 간격
#         self.PADDING_RATIO = paddingRatio
#
#         self.boughtShortPositionAmount = 0
#         self.boughtShortPositionAt = 0
#
#         self.initialPrice = 0
#         self.started = False
#         self.afford = 0
#         self.buyAmount = 0
#
#         self.prices = []
#         self.highestPrice = 0
#         self.lowestPrice = 0
#
#         # trend following
#         self.FMA_DAY = fma_tick
#         self.SMA_DAY = sma_tick
#         self.AVG_P = avg_p
#         self.hands_off_ratio = 0.5
#
#         self.sma = None
#         self.fma = None
#
#         self.isTrendFollowing = False
#         self.inc_rates = []
#         self.trendFollowingInitialTotal = 0
#
#         # lists for plotting
#         self.longPositionTotal = []
#         self.shortPositionTotal = []
#
#         self.transactionDates = []
#         self.transactionPrices = []
#
#         self.systemResetDates = []
#         self.systemResetPrices = []
#         self.systemResetTotals = []
#
#         self.trendFollowingDates = []
#         self.trendFollowingPrices = []
#
#         self.smas = []
#         self.fmas = []
#
#     def next(self):
#         super().next()
#         initialCash = self.broker.cash
#         self.prices.append(self.price)
#
#         longPositionTotal = self.boughtAmount * self.price * (1 - self.broker.commission)
#         shortPositionTotal = self.boughtShortPositionAmount * (self.boughtShortPositionAt * 2 - self.price) * (
#                 1 - self.broker.commission)
#         self.broker.total = self.broker.cash + longPositionTotal + shortPositionTotal
#
#         if self.tickCount != 1:
#             self.inc_rates.append((self.price-self.prices[-2]) / self.prices[-2])
#         if self.tickCount >= self.SMA_DAY:
#             self.sma = sum(self.prices[-self.SMA_DAY:]) / self.SMA_DAY
#         if self.tickCount >= self.FMA_DAY:
#             self.fma = sum(self.prices[-self.FMA_DAY:]) / self.FMA_DAY
#
#         # 초기 구매
#         if not self.started:
#             self.afford = self.broker.cash * self.BUY_RATIO
#             self.buyAmount = int(self.afford / self.price)
#             self.started = True
#             self.initialPrice = self.price
#
#             self.systemResetDates.append(self.time)
#             self.systemResetPrices.append(self.price)
#             self.systemResetTotals.append(self.broker.total)
#         elif not self.isTrendFollowing:
#             # trend following 조건 체크
#             if self.canFollowTrend():
#                 self.isTrendFollowing = True
#                 self.trendFollowingDates.append(self.time)
#                 self.trendFollowingPrices.append(self.price)
#                 self.close()
#                 self.closeShortPosition()
#                 self.trendFollowingInitialTotal = self.broker.total
#
#                 if self.fma > self.sma:
#                     self.buy(self.buyAmount)
#                 else:
#                     self.buyShortPosition(self.buyAmount)
#             elif self.price > self.initialPrice:
#                 if self.boughtShortPositionAmount == 0:
#                     # 매도포지션 매수
#                     if self.price < self.getHighestSellLine(self.prices[-2]):
#                         if self.boughtAmount != 0:
#                             self.close()
#                             self.started = False
#                         else:
#                             self.buyShortPosition(self.buyAmount)
#                             self.highestPrice = self.getHighestSellLine(self.prices[-2])
#                 else:
#                     # 매도포지션 매도
#                     if self.price > self.getLowestBuyLine(self.prices[-2]) and self.price > self.highestPrice:
#                         self.closeShortPosition()
#             else:
#                 if self.boughtAmount == 0:
#                     # 매수포지션 매수
#                     if self.price > self.getLowestBuyLine(self.prices[-2]):
#                         if self.boughtShortPositionAmount != 0:
#                             self.closeShortPosition()
#                             self.started = False
#                         else:
#                             self.buy(self.buyAmount)
#                             self.lowestPrice = self.getLowestBuyLine(self.prices[-2])
#                 else:
#                     # 매수포지션 매도
#                     if self.price < self.getHighestSellLine(self.prices[-2]) and self.price < self.lowestPrice:
#                         self.close()
#         else: # trendfollowing
#             profit = (self.broker.total - self.trendFollowingInitialTotal) / self.trendFollowingInitialTotal
#             if not self.canFollowTrend(hands_off=False) or profit < -0.1:
#                 self.isTrendFollowing = False
#                 self.started = False
#                 self.close()
#                 self.closeShortPosition()
#
#         self.longPositionTotal.append(longPositionTotal)
#         self.shortPositionTotal.append(shortPositionTotal)
#
#         self.smas.append(self.sma)
#         self.fmas.append(self.fma)
#
#         if self.broker.cash != initialCash:
#             self.transactionDates.append(self.time)
#             self.transactionPrices.append(self.price)
#
#     def end(self):
#         miny = min(self.prices)
#         maxy = max(self.prices)
#
#         # draw crit lines
#         minCritLine = miny + self.CRIT_DISTANCE - (miny % self.CRIT_DISTANCE)
#         for y in range(int(minCritLine), int(maxy), self.CRIT_DISTANCE):
#             self.plots.append({"values": [y] * len(self.prices),
#                                "params": {"color": "green", "alpha": 0.3, "linewidth": 0.5, "markersize": 0}})
#
#         # draw positions' total
#         self.plots.append({"values": self.longPositionTotal, "params": {"color": "red"}, "onCash": True})
#         self.plots.append({"values": self.shortPositionTotal, "params": {"color": "blue"}, "onCash": True})
#
#         # draw transaction dates
#         self.plots.append({"values": self.transactionPrices, "scatter": True, "x": self.transactionDates,
#                            "params": {"color": "blue"}})
#
#         # draw system reset dates
#         self.plots.append({"values": self.systemResetPrices, "scatter": True, "x": self.systemResetDates,
#                            "params": {"color": "green"}})
#         self.plots.append({"values": self.systemResetTotals, "scatter": True, "x": self.systemResetDates,
#                            "params": {"color": "green"}, "onCash": True})
#         self.plots.append({"values": [round(n) for n in self.systemResetTotals], "text": True, "x": self.systemResetDates,
#                            "y": self.systemResetTotals,
#                            "params": {"fontsize": 7, "horizontalalignment": "center", "verticalalignment": "bottom"},
#                            "onCash": True})
#
#         # draw trend following dates
#         self.plots.append({"values": self.trendFollowingPrices, "scatter": True, "x": self.trendFollowingDates,
#                            "params": {"color": "purple"}})
#
#         # draw sma and fma
#         self.plots.append({"values": self.smas, "params": {"color": "blue", "linewidth": 0.5}})
#         self.plots.append({"values": self.fmas, "params": {"color": "red", "linewidth": 0.5}})
#
#         super().end()
#
#     def getHighestSellLine(self, price):
#         return ((price + self.CRIT_DISTANCE * self.PADDING_RATIO) // self.CRIT_DISTANCE) * self.CRIT_DISTANCE \
#                - self.CRIT_DISTANCE * self.PADDING_RATIO
#
#     def getLowestBuyLine(self, price):
#         return ((price - self.CRIT_DISTANCE * self.PADDING_RATIO) // self.CRIT_DISTANCE) * self.CRIT_DISTANCE \
#                + self.CRIT_DISTANCE * (self.PADDING_RATIO + 1)
#
#     def buyShortPosition(self, size):
#         self.broker.cash -= size * self.price * (1 + self.broker.commission)
#         self.boughtShortPositionAmount += size
#         self.boughtShortPositionAt = self.price
#
#     def sellShortPosition(self, size):
#         self.broker.cash += size * (self.boughtShortPositionAt * 2 - self.price) * (1 - self.broker.commission)
#         self.boughtShortPositionAmount -= size
#
#     def closeShortPosition(self):
#         self.sellShortPosition(self.boughtShortPositionAmount)
#
#     def canFollowTrend(self, hands_off=False):
#         if self.tickCount > self.SMA_DAY:
#             avg_inc_rate = sum(self.inc_rates[-self.SMA_DAY:]) / self.SMA_DAY
#
#             if hands_off:
#                 avg_p = self.AVG_P * self.hands_off_ratio
#             else:
#                 avg_p = self.AVG_P
#             if (self.fma - self.sma) * avg_inc_rate > 0 and abs(avg_inc_rate) > avg_p:
#                 return True
#         return False
