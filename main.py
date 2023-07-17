import logging
import TradingDiscord
import TastyTrades
import graypy
import datetime
import pytz

LOGGER_HOST = "3.86.80.122"
LOGGER_PORT = 12201

TASTY_TRADES_USERNAME = "nckspec"
TASTY_TRADES_PASSWORD = "1Success2015!"
TASTY_TRADES_ACCOUNT_ID = "5WX92378"
TASTY_TRADES_DEBUG = False

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.DEBUG)

handler = graypy.GELFTCPHandler(LOGGER_HOST, LOGGER_PORT)
LOGGER.addHandler(handler)


FORMAT = '%(asctime)s - %(levelname)s - %(message)s\n'
logging.basicConfig(format=FORMAT, datefmt='%m/%d/%Y %H:%M:%S')
# logging.disable(logging.DEBUG)

def get_current_date():
    date = pytz.utc.localize(datetime.datetime.utcnow())
    date = date.astimezone(pytz.timezone("America/Los_Angeles"))
    return date

#  Will round the price down to the nearest 10 to get the sell strike price and then
#  set the buy strike price $10 below
def get_strike_prices(price: float):
    sell_strike_price = round(price / 10) * 10
    buy_strike_price = sell_strike_price - 10

    return {
        "buy_strike_price": buy_strike_price,
        "sell_strike_price": sell_strike_price
    }

def main():
    try:
        discord = TradingDiscord.TradingDiscord()
        LOGGER.info("Initialized connection to Discord.")

        exchange = TastyTrades.TastyTrades(username=TASTY_TRADES_USERNAME, password=TASTY_TRADES_PASSWORD, account_id=TASTY_TRADES_ACCOUNT_ID, debug=TASTY_TRADES_DEBUG)
        LOGGER.info("Initialized connection to exchange: Tasty Trades")

        @discord.event
        def on_price_notification(price):
            LOGGER.info(f"Received price notification of {price}")

            strike_prices = get_strike_prices(price)
            LOGGER.info(f"Setting a vertical put spread of {strike_prices['buy_strike_price']}/{strike_prices['sell_strike_price']}")

            order = exchange.create_order(
                type="put",
                symbol="NDXP",
                expiration_date=datetime.date(2023, 7, 17),
                limit=5.0,
                price_effect="credit",
                quantity=1,
                buy_strike_price=strike_prices['buy_strike_price'],
                sell_strike_price=strike_prices['sell_strike_price']
            )

            order.send()
            LOGGER.info("Order sent.", extra={})

    except Exception as ex:
        LOGGER.error(f"Error in main(): {ex}")


main()
