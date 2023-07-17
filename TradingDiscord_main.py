import TradingDiscord

trade = TradingDiscord.TradingDiscord()

@trade.event
def on_price_notification(price):
    print(price)

