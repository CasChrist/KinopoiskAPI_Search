from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from bot_token import TOKEN
import api_requests

# Define start command handler
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Привет! Я — бот, предоставляющий информацию о фильмах. Я беру данные с API Кинопоиска. Вот список того, что я могу делать:\n\n/movie <\"Название фильма\"> — выдам краткую информацию обо всех фильмах с таким названием (не более 10-ти)\n")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    sbn_handler = CommandHandler('movie', api_requests.search_by_name)

    app.add_handler(start_handler)
    app.add_handler(sbn_handler)

    app.run_polling()