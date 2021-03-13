from cihatbot.app import Application
import asyncio


print("Starting Cihat-traders")

application = Application("cli", "binance", "cihatbot.cfg")
application.run()


