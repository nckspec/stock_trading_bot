import discord
import re
import threading
import logging

LOGGER = logging.getLogger('logger')

TRADE_NOTIFICATIONS_CHANNEL = "general"
TRADE_NOTIFICATIONS_BOT = "bignick123#2012"
DISCORD_TOKEN = "MTEzMDIwOTEwNzMyMDc3ODc4Mw.GgfPsY.OklXdmPiFdURMxa_0BjSj1a80d226DLRpKIQlo"

class TradingDiscord:
    def __init__(self):
        try:
            self._logger = logging.LoggerAdapter(LOGGER,
                                                 {
                                                     "class": "TradingDiscord()"
                                                 })

            self._logger.debug("Initializing TradingDiscord()")

            #  Setup the Discord client. Pass 'self' into the
            #  client Class so that we can call our own version
            #  of on message
            class MyClient(discord.Client):
                def __init__(self, trading_discord, intents):
                    discord.Client.__init__(self, intents=intents)
                    self._trading_discord = trading_discord

                async def on_ready(self):
                    await self._trading_discord.on_ready()

                async def on_message(self, message):
                    await self._trading_discord.on_message(message)

            #  Set default message intents and run client
            intents = discord.Intents.default()
            intents.message_content = True
            client = MyClient(self, intents=intents)
            self._discord_client = client

            #  Start Discord client in a separate thread since it isn't natively
            #  multithreaded
            x = threading.Thread(target=self._discord_client.run, args=(DISCORD_TOKEN,))
            x.start()

            self._logger.debug("Initialized TradingDiscord()")

        except Exception as ex:
            message = f"Error in TradingDiscord.__init__(): {ex}"
            raise Exception(message)


    def event(self, callback_func):
        self._callback_func = callback_func

    async def on_message(self, message):
        try:
            #  Verify that the message is from the notifications channel
            #  and from the right author (bot). Then call the callback function
            #  that we set
            if self._verify_message(message):
                self._callback_func(self._get_price_from_message(message))
        except Exception as ex:
            message = f"Error in TradingDiscord.on_message(): {ex}"
            raise Exception(message)


    async def on_ready(self):
        self._logger.debug("Connected to Discord bot.")

    def _get_price_from_message(self, message):
        try:
            self._logger.debug("Entering TradingDiscord._get_price_from_message()", extra={"discord_message": message})

            price = re.findall(r"[-+]?(?:\d*\.*\d+)", f"{message.content}")
            if len(price) > 0:
                return float(price[0])
        except Exception as ex:
            message = f"Error in TradingDiscord._get_price_from_message(): {ex}"
            raise Exception(message)



    def _verify_message(self, message):
        try:
            self._logger.debug("Entering TradingDiscord._verify_message()", extra={"discord_message": message})

            channel = str(message.channel)
            author = str(message.author)
            content = str(message.content)
            #  Check if the message came from the notifications channel
            if channel == TRADE_NOTIFICATIONS_CHANNEL and author == TRADE_NOTIFICATIONS_BOT:
                #  Check if the bot is giving a valid trade notification
                if "NDX" in content:
                    return True

            return False
        except Exception as ex:
            message = f"Error in TradingDiscord._verify_message(): {ex}"
            raise Exception(message)













