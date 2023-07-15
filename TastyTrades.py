import logging
import requests
import datetime
import pytz
LOGGER = logging.getLogger('logger')

API_URL = "https://api.tastyworks.com"
SANDBOX_API_URL = "https://api.tastyworks.com"
USER_AGENT = {'User-agent': 'Mozilla/5.0'}

class TastyTrades:

    def __init__(self, username, password, account_id, debug=False):
        try:
            self._logger = logging.LoggerAdapter(LOGGER,
                                   {"extra":
                                    {'username': username,
                                    'password': password,
                                    'account_id': account_id,
                                    'debug': str(debug)}})

            if debug:
                self._api_url = API_URL
            else:
                self._api_url = SANDBOX_API_URL

            self._account_id = account_id

            #  Connect to Tasty Trades and get a session token to be used
            #  with all future requests
            self._session_token = self._connect(username, password)

            self._logger.debug(f"Received session token = {self._session_token}", extra={"session_token": self._session_token})

            self._headers = {
                'User-agent': 'Mozilla/5.0',
                'Authorization': self._session_token
            }

            self._logger.debug("Initiated TastyTrades() object")

        except Exception as ex:
            message = f"Error in TastyTrades.__init__(): {ex}"
            raise Exception(message)

    #  Connect to Tasty Trades using the username and password of the account
    #  Return: session token that is valid for 24 hours to be used with future requests
    def _connect(self, username, password):
        try:
            endpoint = "/sessions"
            json = {
                "login": username,
                "password": password
            }

            self._logger.info("Attempting to connect to Tasty Trades with "
                              "username: {username}/account id: {self._account_id}")

            response = requests.post(self._api_url + endpoint, headers=USER_AGENT, json=json)

            #  If the request resulted in an error raise it
            if response.status_code != 201:
                message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                          f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                raise Exception(message)

            self._logger.info(f"Connected to TastyTrades with username: {username}/account id: {self._account_id}")

            #  Return the session token to be used with future connections
            return response.json()['data']['session-token']

        except Exception as ex:
            message = f"Error in TastyTrades._connect(): {ex}"
            raise Exception(message)

    def _make_request(self, endpoint, type="get", data=dict()):
        try:
            self._logger.debug(f"Entering TastyTrades._make_request()\n"
                               f"endpoint: {endpoint}\n"
                               f"type: {type}\n"
                               f"data: {data}", extra={"endpoint": endpoint,
                                                       "type": type,
                                                       "data": data})

            type = type.lower()

            if type == "get":
                response = requests.get(self._api_url + endpoint, headers=self._headers)
                if response.status_code != 200:
                    message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                              f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                    raise Exception(message)
            elif type == "post":
                response = requests.post(self._api_url + endpoint, headers=self._headers, json=data)
                if response.status_code != 201:
                    message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                              f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                    raise Exception(message)

            self._logger.debug(f"Exiting TastyTrades._make_request()\n"
                               f"status code: {response.status_code}\n"
                               f"json: {response.json()}", extra={"endpoint": endpoint,
                                                       "type": type,
                                                       "data": data})

            return response



        except Exception as ex:
            message = f"Error in TastyTrades._make_request(): {ex}"
            raise Exception(message)

    #  Retrieves the current balance of the account
    #  Return: Float with the current balance
    def get_balance(self):
        try:
            endpoint = f"/accounts/{self._account_id}/balances"

            response = self._make_request(endpoint, "get")

            balance = float(response.json()['data']['cash-balance'])

            self._logger.info(f"Retrieved balance of ${balance} on account id: {self._account_id}")

            return balance

        except Exception as ex:
            message = f"Error in TastyTrades.get_balance(): {ex}"
            raise Exception(message)

    def get_option_contract(self, symbol: str, type: str, strike_price: float, expiration_date: datetime.date):
        try:
            self._logger.debug("Entering TastyTrades.get_option_contract()\n"
                               f"symbol: {symbol}\n"
                               f"type: {type}\n"
                               f"strike_price: {strike_price}\n"
                               f"expiration_date: {expiration_date}")

            type = type.lower()

            if type == "call" or type == 'c':
                type = 'C'
            elif type == "put" or type == 'p':
                type = 'P'
            else:
                raise Exception("The type parameter must be either 'call' or 'put'")

            #  Concatenate the symbol in ooc format yymmddTypeStrikePrice
            #  ex. 230717P10700000 - July 17, 2023, Put, Strike price
            ooc_symbol = symbol + "  " + self.convert_date_to_ooc(expiration_date) + type + self.convert_strike_price_to_ooc(strike_price)

            response = self._make_request(f"/instruments/equity-options/{ooc_symbol}", "get")

            self._logger.debug("Exiting TastyTrades.get_option_contract()\n"
                               f"ooc_symbol: {ooc_symbol}\n")

            return ooc_symbol, response

        except Exception as ex:
            message = f"Error in TastyTrades.get_option_contract(): {ex}"
            raise Exception(message)

    #  Will convert the date to ooc format. Must input a date() object and
    #  will return a string in ooc format
    def convert_date_to_ooc(self, date: datetime.date):
        self._logger.debug("Entering TastyTrades.convert_date_to_ooc()\n"
                           f"date: {date}")

        date_format = "%y%m%d"
        date = date.strftime(date_format)

        self._logger.debug("Exiting TastyTrades.convert_date_to_ooc()\n"
                           f"date: {date}")

        return date

    #  Multiplies the price by 1000 and then pads the number with
    #  leading 0s
    def convert_strike_price_to_ooc(self, strike_price: float):
        self._logger.debug("Entering TastyTrades.convert_strike_price_to_ooc()\n"
                           f"strike_price: {strike_price}")

        ooc_format = int(strike_price * 1000)
        ooc_format = f"{ooc_format:08}"

        self._logger.debug("Exiting TastyTrades.convert_strike_price_to_ooc()\n"
                           f"ooc_format: {ooc_format}")

        return ooc_format

