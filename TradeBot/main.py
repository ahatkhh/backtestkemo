import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)

try:
    from TradeBot.tradeBot import TradeBot
    from Strategy.dca_strategy import DCA_Strategy
    from Strategy.test_strategy import Test_Strategy
except ModuleNotFoundError:
    raise

if __name__ == "__main__":
    strategy = DCA_Strategy(isRealTime=True)
    strategy.trigPs = [pow(1.5, i) / 100 for i in range(0, 6)]
    strategy.invests = [i / 250 for i in [15, 15, 15, 15, 20, 20, 20]]
    strategy.profitP = 0.03
    strategy.trail_profit = 0.005
    strategy.trail_dca = 0.005
    strategy.stopLossP = 0.15
    strategy.name = 'mydca'
    bot = TradeBot(strategy=strategy, requestInterval=0.5)
    bot.run()