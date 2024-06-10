import requests

from telegram import (
  Update, InlineKeyboardMarkup, InlineKeyboardButton
  )
from telegram.ext import CallbackContext, ConversationHandler
from telegram.constants import ChatAction
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime

CHOOSE_MOVIE, MOVIE = range(0, 2)

months = {
    "01": "января", "02": "февраля", "03": "марта", "04": "апреля",
    "05": "мая", "06": "июня", "07": "июля", "08": "августа",
    "09": "сентября", "10": "октября", "11": "ноября", "12": "декабря"
}

async def search_afisha(update: Update, context: CallbackContext):
  await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
  if len(context.args) == 0:
    date = parser.parse(datetime.today().strftime('%Y-%m-%d')).strftime('%Y-%m-%d')
  else:
    if parser.parse(context.args[0]) < datetime.today():
      text = '❌ *Запрос отклонён*: Укажите дату не ранее текущей.'
      await update.message.reply_text(text=text, parse_mode='Markdown')
      return ConversationHandler.END
    date = parser.parse(context.args[0]).strftime('%Y-%m-%d')  
    
  # URL веб-страницы с афишей кино
  url = f'https://kemerovo.kinoafisha.info/movies/?date={date}'

  # Получение содержимого веб-страницы
  response = requests.get(url)
  response.raise_for_status()

  # Парсинг содержимого веб-страницы с помощью BeautifulSoup
  soup = BeautifulSoup(response.text, 'html.parser')

  # Найти все элементы, содержащие информацию о фильмах
  movies = soup.find_all('div', class_='movieItem_info')
  if len(movies) == 0:
    text = '❌ *Запрос отклонён*: На эту дату ещё нет сеансов.'
    await update.message.reply_text(text=text, parse_mode='Markdown')
    return ConversationHandler.END

  # Словарь для хранения названий фильмов и ссылок на страницы с сеансами
  movies_dict = dict()
  for movie in movies:
    movie_title = movie.find('a').get_text()
    movie_link = movie.find('a')['href']
    index = movie_link[35:-1]
    movies_dict[movie_title] = index
  
  parsed_back_date = parser.parse(date)
  formatted_back_date = parsed_back_date.strftime('%d') + \
    f' {months[date[5:7]]} ' + parsed_back_date.strftime('%Y') + ' года'
  message = f'Кино в `Кемерове` на *{formatted_back_date}*:\n\n'
  keyboard = []
  period = 0
  for movie in movies_dict.keys():
    message += str(period+1) + '. ' + movie + '\n'
    if period % 6 == 0:
      keyboard.append([InlineKeyboardButton(
        period + 1,
        callback_data = movies_dict[movie] + '$' + date
        )])
    else:
      keyboard[period // 6].append(InlineKeyboardButton(
        period + 1,
        callback_data = movies_dict[movie] + '$' + date
        ))
    period += 1

  markup = InlineKeyboardMarkup(keyboard)

  await update.message.reply_text(text=message, reply_markup=markup, parse_mode='Markdown')

  return CHOOSE_MOVIE

async def handle_movie(update: Update, context: CallbackContext):
  await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
  query = update.callback_query
  data = query.data.split('$')
  movie_id = data[0]

  url = f'https://kemerovo.kinoafisha.info/movies/{movie_id}' + \
    f'/?date={''.join(data[1].split('-'))}#submenu'
  
  response = requests.get(url)
  response.raise_for_status()

  soup = BeautifulSoup(response.text, 'html.parser')

  cinemas = soup.find_all('div', class_='showtimes_item')
  
  cinemas_dict = dict()
  for cinema in cinemas:
    try:
      cinema_title = cinema.find('span', class_='showtimesCinema_name').get_text().strip()
    except:
      continue
    sessions_dict = dict()
    session_time = cinema.find_all('span', class_='session_time')
    session_price = cinema.find_all('span', class_='session_price')
    for time in session_time:
      if len(session_price) != 0:
        for price in session_price:
          sessions_dict[time.get_text().strip()] = price.get_text().strip()
      else:
        sessions_dict[time.get_text().strip()] = None
    cinemas_dict[cinema_title] = sessions_dict
  print(cinemas_dict)

  movie_title = soup.find('span', class_='trailer_title').get_text()
  parsed_back_date = parser.parse(data[1])
  formatted_back_date = parsed_back_date.strftime('%d') + \
    f' {months[data[1][5:7]]} ' + parsed_back_date.strftime('%Y') + ' года'
  message = 'Расписание сеансов *' + movie_title.upper() + \
    f'* на *{formatted_back_date}*:\n\n'
  for cinema, session in cinemas_dict.items():
    message += '*' + cinema + '*: '
    for time, price in session.items():
      temp = list(session.items())[-1]
      if price is not None:
        if len(session) > 1 and (time, price) != temp:
          message += '`' + time + '` | ' + price + ', '
        elif len(session) == 1 or len(session) > 1 and (time, price) == temp:
          message += '`' + time + '` | ' + price + '\n'
      else:
        if len(session) > 1 and (time, price) != temp:
          message += '`' + time + '`, '
        elif len(session) == 1 or len(session) > 1 and (time, price) == temp:
          message += '`' + time + '`' + '\n'

  message = message[:-1]

  await query.edit_message_text(text=message, parse_mode='Markdown')

  return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
  await update.message.reply_text('Query cancelled.')

  return ConversationHandler.END