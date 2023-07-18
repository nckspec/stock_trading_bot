import logging
from fastapi import FastAPI, Request
import uvicorn
import TastyTrades
import graypy
import datetime
import pytz
import os
import math

LOGGER_HOST = str(os.environ['LOGGER_HOST'])
LOGGER_PORT = int(os.environ['LOGGER_PORT'])

TASTY_TRADES_USERNAME = str(os.environ['TASTY_TRADES_USERNAME'])
TASTY_TRADES_PASSWORD = str(os.environ['TASTY_TRADES_PASSWORD'])
TASTY_TRADES_ACCOUNT_ID = str(os.environ['TASTY_TRADES_ACCOUNT_ID'])
TASTY_TRADES_DEBUG = bool(int(os.environ['TASTY_TRADES_DEBUG']))

API_PORT = 5555

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.DEBUG)

handler = graypy.GELFTCPHandler(LOGGER_HOST, LOGGER_PORT)
LOGGER.addHandler(handler)


FORMAT = '%(asctime)s - %(levelname)s - %(message)s\n'
logging.basicConfig(format=FORMAT, datefmt='%m/%d/%Y %H:%M:%S')
# logging.disable(logging.DEBUG)

app = FastAPI()

def get_current_date():
    date = pytz.utc.localize(datetime.datetime.utcnow())
    date = date.astimezone(pytz.timezone("America/Los_Angeles"))
    return date

#  Will round the price down to the nearest 10 to get the sell strike price and then
#  set the buy strike price $10 below
def get_strike_prices(price: float):
    sell_strike_price = math.ceil(price / 10) * 10
    buy_strike_price = sell_strike_price - 10

    return {
        "buy_strike_price": buy_strike_price,
        "sell_strike_price": sell_strike_price
    }

@app.post("/notify")
async def on_price_notification(request: Request, price: float):
    try:
        LOGGER.debug(f"Entering on_price_notification()\n"
                     f"price: {price}")
        LOGGER.info(f"Received price notification of {price}")

        price = float(price)

        exchange = TastyTrades.TastyTrades(username=TASTY_TRADES_USERNAME, password=TASTY_TRADES_PASSWORD,
                                           account_id=TASTY_TRADES_ACCOUNT_ID, debug=TASTY_TRADES_DEBUG)
        LOGGER.info("Initialized connection to exchange: Tasty Trades")

        strike_prices = get_strike_prices(price)
        LOGGER.info(
            f"Setting a vertical put spread of {strike_prices['buy_strike_price']}/{strike_prices['sell_strike_price']}")

        order = exchange.create_order(
            type="put",
            symbol="NDXP",
            expiration_date=get_current_date(),
            limit=5.0,
            price_effect="credit",
            quantity=1,
            buy_strike_price=strike_prices['buy_strike_price'],
            sell_strike_price=strike_prices['sell_strike_price']
        )

        order.send()
        LOGGER.info("Order sent.", extra={})
    except Exception as ex:
        message = f"Error in on_price_notification(): {ex}"
        raise Exception(message)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=API_PORT)