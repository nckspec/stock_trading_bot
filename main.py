import logging
import TastyTrades
import datetime
import pytz
import requests
import time

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.DEBUG)


FORMAT = '%(asctime)s - %(levelname)s - %(message)s\n%(extra)s\n'
logging.basicConfig(format=FORMAT, datefmt='%m/%d/%Y %H:%M:%S')
# logging.disable(logging.DEBUG)

# LOGGER.debug('Hello Graylog.')

tasty = TastyTrades.TastyTrades(username="nckspec", password="1Success2015!", account_id="5WX92378")

print(tasty.get_balance())

#  Get the current date in Los Angeles time
# date = pytz.utc.localize(datetime.datetime.utcnow())
# date = date.astimezone(pytz.timezone("America/Los_Angeles"))

date = datetime.date(2023, 7, 17)

ooc, response = tasty.get_option_contract("NDXP", "Put", 10700, date)

print(ooc)
print(response.json())



# try:
#     response = tasty._make_request("/instruments/equity-options/NDXP  230714P15700000", "get")
#     print(response.json())
# except Exception as ex:
#     print(ex)

# response = tasty._make_request("/option-chains/NDX/compact", "get")
#
# for item in response.json()['data']['items']:
#     print(item)
#     time.sleep(3)




