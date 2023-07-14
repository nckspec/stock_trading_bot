import logging
import requests
my_logger = logging.getLogger('logger')

API_URL = "https://api.tastyworks.com"
SANDBOX_API_URL = "https://api.tastyworks.com"
USER_AGENT = {'User-agent': 'Mozilla/5.0'}

class TastyTrades:

    def __init__(self, username, password, account_id, debug=False):
        try:
            if debug:
                self._api_url = API_URL
            else:
                self._api_url = SANDBOX_API_URL

            self._account_id = account_id

            #  Connect to Tasty Trades and get a session token to be used
            #  with all future requests
            self._session_token = self._connect(username, password)

            self._headers = {
                'User-agent': 'Mozilla/5.0',
                'Authorization': self._session_token
            }

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
            response = requests.post(self._api_url + endpoint, headers=USER_AGENT, json=json)

            #  If the request resulted in an error raise it
            if response.status_code != 201:
                message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                          f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                raise Exception(message)

            #  Return the session token to be used with future connections
            return response.json()['data']['session-token']

        except Exception as ex:
            message = f"Error in TastyTrades._connect(): {ex}"
            raise Exception(message)

    def _make_request(self, endpoint, type="get", data=dict()):
        try:
            if type is "get":
                response = requests.get(self._api_url + endpoint, headers=self._headers)
                if response.status_code != 200:
                    message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                              f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                    raise Exception(message)
            elif type is "post":
                response = requests.post(self._api_url + endpoint, headers=self._headers, json=data)
                if response.status_code != 201:
                    message = f"Error connecting to Tasty Trades: status code ({response.status_code}): " \
                              f"{response.json() if response.headers.get('content-type') == 'application/json' else 'no response'}"
                    raise Exception(message)

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

            return response.json()['data']['cash-balance']

        except Exception as ex:
            message = f"Error in TastyTrades.get_balance(): {ex}"
            raise Exception(message)

