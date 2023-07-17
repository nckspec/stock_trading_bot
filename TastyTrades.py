import logging
import requests
import datetime
import pytz
LOGGER = logging.getLogger('logger')

API_URL = "https://api.tastyworks.com"
SANDBOX_API_URL = "https://api.cert.tastyworks.com"
USER_AGENT = {'User-agent': 'Mozilla/5.0'}

class TastyTrades:

    def __init__(self, username, password, account_id, debug=False):
        try:
            self._logger = logging.LoggerAdapter(LOGGER,
                                   {'class': "TastyTrades()",
                                    'username': username,
                                    'password': password,
                                    'account_id': account_id,
                                    'debug': str(debug)})

            if debug:
                self._api_url = SANDBOX_API_URL

            else:
                self._api_url = API_URL

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

            self._logger.debug("Attempting to connect to Tasty Trades with "
                              "username: {username}/account id: {self._account_id}")

            response = requests.post(self._api_url + endpoint, headers=USER_AGENT, json=json)

            #  If the request resulted in an error raise it
            if response.status_code != 201:
                message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                          f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                raise Exception(message)

            self._logger.debug(f"Connected to TastyTrades with username: {username}/account id: {self._account_id}")

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
            elif type == "delete":
                response = requests.delete(self._api_url + endpoint, headers=self._headers)
                if response.status_code != 200:
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

            self._logger.debug(f"Retrieved balance of ${balance} on account id: {self._account_id}")

            return balance

        except Exception as ex:
            message = f"Error in TastyTrades.get_balance(): {ex}"
            raise Exception(message)

    def create_order(self, type: str, symbol: str, expiration_date: datetime.date, limit: float, price_effect: str,
                 quantity: int, buy_strike_price: float, sell_strike_price: float):
        try:
            return VerticalSpread(
                type=type,
                exchange=self,
                symbol=symbol,
                expiration_date=expiration_date,
                limit=limit,
                price_effect=price_effect,
                quantity=quantity,
                buy_strike_price=buy_strike_price,
                sell_strike_price=sell_strike_price
            )
        except Exception as ex:
            message = f"Error in TastyTrades.create_order(): {ex}"
            raise Exception(message)

    def get_option_contract(self, symbol: str, type: str, strike_price: float, expiration_date: datetime.date):
        try:
            self._logger.debug("Entering TastyTrades.get_option_contract()\n"
                               f"symbol: {symbol}\n"
                               f"type: {type}\n"
                               f"strike_price: {strike_price}\n"
                               f"expiration_date: {expiration_date}")

            #  Check to make sure all variables were inputted as the correct type
            if not isinstance(symbol, str):
                raise Exception("Symbol was not inputted as a string!")
            if not isinstance(strike_price, float) and not isinstance(strike_price, int):
                raise Exception("Strike price was not inputted as an int/float")
            if not isinstance(expiration_date, datetime.date):
                raise Exception("Expiration date is not a datetime.date object!")

            #  Convert type to lowercase to make it easily compared
            type = type.lower()

            if type == "call" or type == 'c':
                type = 'C'
            elif type == "put" or type == 'p':
                type = 'P'
            else:
                raise Exception("The type parameter must be either 'call' or 'put'")

            #  Concatenate the symbol in ooc format yymmddTypeStrikePrice
            #  ex. 230717P10700000 - July 17, 2023, Put, Strike price
            ooc_symbol = symbol + "  " + self._convert_date_to_ooc(expiration_date) + type + self._convert_strike_price_to_ooc(strike_price)

            response = self._make_request(f"/instruments/equity-options/{ooc_symbol}", "get")

            self._logger.debug("Exiting TastyTrades.get_option_contract()\n"
                               f"ooc_symbol: {ooc_symbol}\n")

            return response.json()['data']['symbol']

        except Exception as ex:
            message = f"Error in TastyTrades.get_option_contract(): {ex}"
            raise Exception(message)

    #  Will convert the date to ooc format. Must input a date() object and
    #  will return a string in ooc format
    def _convert_date_to_ooc(self, date: datetime.date):
        try:
            self._logger.debug("Entering TastyTrades.convert_date_to_ooc()\n"
                               f"date: {date}")

            date_format = "%y%m%d"
            date = date.strftime(date_format)

            self._logger.debug("Exiting TastyTrades.convert_date_to_ooc()\n"
                               f"date: {date}")

            return date
        except Exception as ex:
            message = f"Error in TastyTrades._convert_date_to_ooc(): {ex}"
            raise Exception(message)

    #  Multiplies the price by 1000 and then pads the number with
    #  leading 0s
    def _convert_strike_price_to_ooc(self, strike_price: float):
        try:
            self._logger.debug("Entering TastyTrades.convert_strike_price_to_ooc()\n"
                               f"strike_price: {strike_price}")

            ooc_format = int(strike_price * 1000)
            ooc_format = f"{ooc_format:08}"

            self._logger.debug("Exiting TastyTrades.convert_strike_price_to_ooc()\n"
                               f"ooc_format: {ooc_format}")

            return ooc_format

        except Exception as ex:
            message = f"Error in TastyTrades._convert_strike_price_to_ooc(): {ex}"
            raise Exception(message)

    def get_account_id(self):
        return self._account_id

class Order:
    def __init__(self, exchange: TastyTrades, order_id=0):
        self._exchange = exchange
        self._order_id = order_id

    def cancel(self):
        endpoint = f"/accounts/{self.get_exchange().get_account_id()}/orders/{self._order_id}"
        return self.get_exchange()._make_request(endpoint, "delete")

    def get_exchange(self):
        return self._exchange

class VerticalSpread(Order):
    def __init__(self, exchange: TastyTrades, type: str, symbol: str, expiration_date: datetime.date, limit: float, price_effect: str,
                 quantity: int, buy_strike_price: float, sell_strike_price: float):
        try:
            if not isinstance(symbol, str):
                raise Exception("Symbol is not a str() object!")
            if not isinstance(expiration_date, datetime.date):
                raise Exception("Expiration date is not a datetime.date object!")
            if price_effect != "credit" and price_effect != "debit":
                raise Exception("Price effect must be set to either 'credit' or 'debit'")

            #  Initialize parent class
            Order.__init__(self, exchange)

            # Store price effect, expiration_date, and quantity
            self._symbol = str(symbol)
            self._price_effect = str(price_effect).lower()
            self._limit = float(limit)
            self._quantity = int(quantity)

            #  Store the buy/sell legs of the trade
            self._buy_leg = {
                "strike_price": float(buy_strike_price),
                "symbol": self._exchange.get_option_contract(self._symbol, type, float(buy_strike_price), expiration_date)
            }
            self._sell_leg = {
                "strike_price": float(sell_strike_price),
                "symbol": self._exchange.get_option_contract(self._symbol, type, float(sell_strike_price), expiration_date)
            }
        except Exception as ex:
            message = f"Error in VerticalSpread.__init__(): {ex}"
            raise Exception(message)

    #  Will send the order to Tasty Trades
    def send(self):
        try:
            #  POST order to Tasty Trades
            endpoint = f"/accounts/{self._exchange.get_account_id()}/orders"
            response = self._exchange._make_request(endpoint, "post", self._setup_order())
            #  Store the order id
            self._order_id = int(response.json()['data']['order']['id'])
            return response
        except Exception as ex:
            message = f"Error in VerticalSpread.send(): {ex}"
            raise Exception(message)

    #  Take all of the information on the trade and
    #  organize it into a dictionary to be transmitted to Tasty Trades
    def _setup_order(self):
        try:
            data = {
                "time-in-force": "Day",
                "order-type": "Limit",
                "price": self._limit,
                "price-effect": self._price_effect.capitalize(),
                "legs": [
                    self._create_leg(self._buy_leg['symbol'], "buy"),
                    self._create_leg(self._sell_leg['symbol'], "sell")
                ]
            }
            return data
        except Exception as ex:
            message = f"Error in VerticalSpread._setup_order(): {ex}"
            raise Exception(message)

    #  Will create a dictionary in the format 'leg' that will be added
    #  to the 'legs' key of the json to be transmitted to Tasty Trades
    def _create_leg(self, ooc_symbol: str, type: str):
        try:
            leg = dict()

            #  Setup a dictionary with the required values
            leg['instrument-type'] = "Equity Option"
            leg['symbol'] = ooc_symbol
            leg['quantity'] = self._quantity

            if type == "buy":
                leg['action'] = "Buy to Open"
            elif type == "sell":
                leg['action'] = "Sell to Open"
            else:
                raise Exception("type must be set to either 'buy' or 'sell'!")

            return leg
        except Exception as ex:
            message = f"Error in VerticalSpread.create_leg(): {ex}"
            raise Exception(message)


    def __str__(self):
        info = {
            "symbol": self._symbol,
            "price-effect": self._price_effect,
            "limit": self._limit,
            "quantity": self._quantity,
            "buy_leg": self._buy_leg,
            "sell_leg": self._sell_leg
        }

        return str(info)





