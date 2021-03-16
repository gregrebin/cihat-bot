from cihatbot.app import Application
import asyncio


print("Starting Cihat-traders")

application = Application("telegram", "binance", "cihatbot.cfg")
application.run()


