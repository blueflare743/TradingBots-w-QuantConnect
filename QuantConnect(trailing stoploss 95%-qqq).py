# region imports
from AlgorithmImports import *
# endregion

class UpgradedRedOrangeDogfish(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetEndDate(2022, 1, 1)
        self.SetCash(100000)
        self.qqq = self.AddEquity("QQQ", Resolution.Hour).Symbol
        self.entryTicket = None
        self.stopMarketTicket = None
        self.entryFillTime = datetime.min
        self.stopMarketFillTime = datetime.min
        self.highestPrice = 0
    def OnData(self, data):
        #on daata is used to process days over general time period 
        # wait 30 days once we close last position
        if(self.Time - self.stopMarketFillTime).days() < 30:
            return
        price = self.Securities["QQQ"].Price * .99
        #send entry limit order
            #Transactions.GetOpenOrders() returns a last of all open orders, if there are no open orders in the list then it returns false
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
            quantity = self.CalculateOrderQuantity(self.qqq, 0.5)
            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
            self.entryTime = self.Time
        if(self.Time - self.entryTime).days() >=1 and self.entryTicket.Status != OrderStatus.Filled:
            self.entryTime = self.Time;
            updateFields = UpdateOrderFields()
            updateFields.LimitPrice = price
            self.entryTicket.Update(updateFields)

            # this calculates the amount of shaes of qqq that would add to be exactly half of our portfolio value
        #if not filled after 1 day update limit price
        #move up trailing stop loss if necessary
        if(self.stopMarketTicket is not None and self.Portfolio.Invested):
            if price  > self.highestPrice:
                self.highestPrice = price
                updateFields = updateOrderFields()
                updateFields.StopPrice = price * .95;
                self.stopMarketTicket.Update(UpdateFields)
        pass
    def onOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.filled:
            return
        #ONLY LOOKED AT FILLED ORDERS(INCLUDING STOP LOSS AND LIMIT)
        #on order event specifically for time during orders

        # send stoploss order if limit order is filled
        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId:
            self.stopMarketTicket = self.StopMarketOrder(self.qqq, -self.entryTicket.Quantity, .95 * self.entryTicket.AverageFillPrice)
        if(self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.Id):
            self.stopMarketOrderFillTime = self.Time
            self.highestPrice = 0                                                               
        #save fill time of stoploss order
        pass