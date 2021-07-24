from mocobot.application.market import Market
from mocobot.application.order import Order, Single, Mode, Command
from mocobot.application.ui import Ui, AddOrderEvent
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from uuid import uuid4


BUILD_PATH = "/build_order"
ADD_PATH = "/add_order"

BUILD_TEXT = f"""
<form action={ADD_PATH} name="order_form" id="order_form">
    <div class="entry">
        <label for="symbol">Symbol: </label> <br>
        <input type="text" name="symbol" id="symbol" required>
    </div>
    <div class="entry">
        <label for="quantity">Quantity: </label> <br>
        <input type="number" step=0.0001 name="quantity" id="quantity" required>
    </div>
    <div class="entry">
        <label for="price">Price: </label> <br>
        <input type="number" step=0.0001 name="price" id="price" required>
    </div>
    <div class="entry_hidden" style="display: none;">
        <input type="text" name="nonce" id="nonce">
    </div>
    <div class="entry">
        <input type="submit" value="Add order">
    </div>
</form>
<script>
let params = new URLSearchParams(window.location.search);
document.forms["order_form"]["nonce"].value = params.get("nonce")
</script> 
"""


class TelegramUi(Ui):

    def post_init(self) -> None:
        self.nonce = None
        self.url = self.config["url"]
        self.port = int(self.config["port"])
        self.token = self.config["token"]
        self.user = self.config["user"]

    def pre_run(self) -> None:
        self.updater = Updater(self.token)
        self.updater.dispatcher.add_handler(CommandHandler("add", self._telegram_handler))
        self.updater.start_polling()

    def _telegram_handler(self, update: Update, context: CallbackContext) -> None:
        user = update.message.from_user.username
        if not user == self.user: return
        chat_id = update.message.chat_id
        self.nonce = uuid4().hex
        url = f"{self.url}:{self.port}{BUILD_PATH}?nonce={self.nonce}"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add order", url=url)]
        ])
        self.updater.bot.send_message(chat_id, "sending game", reply_markup=reply_markup)

    async def on_run(self) -> None:
        runner = web.ServerRunner(web.Server(self._web_handle))
        await runner.setup()
        self.site = web.TCPSite(runner, port=self.port)
        await self.site.start()

    async def _web_handle(self, request):
        if "nonce" not in request.query or not request.query["nonce"] == self.nonce:
            return web.HTTPUnauthorized()
        if request.path == BUILD_PATH:
            return web.Response(text=BUILD_TEXT, content_type='text/html')
        elif request.path == ADD_PATH:
            symbol = request.query["symbol"]
            quote = float(request.query["quantity"])
            price = float(request.query["price"])
            self.emit(AddOrderEvent(
                Single(command=Command.BUY, exchange="binance", symbol=symbol, quote=quote, price=price),
                mode=Mode.SEQUENT
            ))
            return web.Response(text="Ok")
        return web.HTTPNotFound()

    async def on_stop(self) -> None:
        await self.site.stop()

    def post_run(self) -> None:
        self.updater.stop()

    def update(self, order: Order, market: Market):
        pass
