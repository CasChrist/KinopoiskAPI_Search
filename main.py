from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackContext, ConversationHandler,
    CallbackQueryHandler
)
from bot_token import TOKEN
import api_requests
import html_parses

# Define start command handler
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Привет! Я — бот, предоставляющий информацию о фильмах. Я беру данные с API Кинопоиска. Вот список того, что я могу делать:\n\n/movie <название фильма> — выдам краткую информацию о фильме с таким названием\n\n/tickets <дата> — выдам информацию обо всех сеансах, которые идут в кинотеатрах. Если ввести команду без указания даты, выдам информацию по сеансам за текущий день.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    sbn_handler = CommandHandler('movie', api_requests.search_by_name)
    sa_handler = ConversationHandler(
        entry_points = [CommandHandler('tickets', html_parses.search_afisha)],
        states = {
            html_parses.CHOOSE_MOVIE: [
                CallbackQueryHandler(html_parses.handle_movie)
            ]
        },
        fallbacks= [CommandHandler('cancel', html_parses.cancel)]
    )

    app.add_handler(start_handler)
    app.add_handler(sbn_handler)
    app.add_handler(sa_handler)

    app.run_polling()