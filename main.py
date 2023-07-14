import logging
import TastyTrades
import requests
import time

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
LOGGER.addHandler(console_handler)

LOGGER.debug('Hello Graylog.')

tasty = TastyTrades.TastyTrades(username="nckspec", password="1Success2015!", account_id="5WX92378")

print(tasty.get_balance())

try:
    response = tasty._make_request("/instruments/equity-options/NDXP  230714P15700000", "get")
    print(response.json())
except Exception as ex:
    print(ex)

# response = tasty._make_request("/option-chains/NDX/compact", "get")
#
# for item in response.json()['data']['items']:
#     print(item)
#     time.sleep(3)




