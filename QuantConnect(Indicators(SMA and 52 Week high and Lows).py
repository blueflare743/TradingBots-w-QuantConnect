# region imports
from AlgorithmImports import *
# endregion

class EnergeticAsparagusCormorant(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2022, 1,1)
        self.SetCash(100000)
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol
        self.sma = self.SMA(self.spy, 30, Resolution.Minute) # only can use higher reoslution
        #you can use history request to pump data into indicators so you don't have to wait for them to be ready
        closing_prices = self.History(self.spy, 30, Resolution.Minute)["close"]
        #returns a pandas dataframe
        for time, price in closing_prices.loc[self.spy].items(): 
            self.sma.Update(time, price)

        pass

    def OnData(self, data: Slice):
        if not self.sma.IsReady:
            return
        hist = self.History(self.spy, timedelta(365),Resolution.Minute)
        # timedelta represents preiod while an int represents bar count
        low = min(hist["low"])
        high = max(hist["high"])
        price = self.Securities["SPY"].Price
        if price  * 1.05 >= high and self.sma.Current.Value < price: 
            if not self.Portfolio["SPY"].IsLong:
                self.Debug("Purchaged SPY at: ", price)
                self.SetHoldings(self.spy, 1)
        elif price * .95 <= low and self.sma.Current.Value > price:
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy, -1)
                self.Debug("Short SPY at: ", price)
        else:
            self.Liquidate()
        self.Plot("BenchMarck", "52-Week-High", high)
        self.Plot("BenchMark", "52-Week-Low", low)
        self.Plot("BenchMark", "SMA", self.sma.Current.Value)
        
