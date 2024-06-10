import requests

from telegram import (
  Update, InlineKeyboardMarkup, InlineKeyboardButton,
  ReplyKeyboardMarkup, KeyboardButton
  )
from telegram.ext import CallbackContext, ConversationHandler
from telegram.constants import ChatAction
from bs4 import BeautifulSoup

CHOOSE_MOVIE, MOVIE = range(0, 2)

async def search_afisha(update: Update, context: CallbackContext):

  date = context.args
  # URL веб-страницы с афишей кино
  url = f'https://kemerovo.kinoafisha.info/movies/?date={date[0]}'

  # Получение содержимого веб-страницы
  response = requests.get(url)
  response.raise_for_status()

  # Парсинг содержимого веб-страницы с помощью BeautifulSoup
  soup = BeautifulSoup(response.text, 'html.parser')

  # Найти все элементы, содержащие информацию о фильмах
  movies = soup.find_all('div', class_='movieItem_info')
  # Словарь для хранения названий фильмов и ссылок на страницы с сеансами
  movies_dict = dict()
  for movie in movies:
    movie_title = movie.find('a').get_text()
    movie_link = movie.find('a')['href']
    index = movie_link[35:-1]
    movies_dict[movie_title] = index
  
  message = f'Кино в Кемерове на {date[0]}:\n\n'
  keyboard = []
  period = 0
  for movie in movies_dict.keys():
    message += str(period+1) + '. ' + movie + '\n'
    if period % 6 == 0:
      keyboard.append([InlineKeyboardButton(period+1, callback_data=movies_dict[movie])])
    else:
      keyboard[period // 6].append(InlineKeyboardButton(period+1, callback_data=movies_dict[movie]))
    # keyboard.append([KeyboardButton(movie)])
    period += 1

  markup = InlineKeyboardMarkup(keyboard)
  # markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

  await update.message.reply_text(text=message, reply_markup=markup)

  return CHOOSE_MOVIE

async def handle_movie(update: Update, context: CallbackContext):
  query = update.callback_query
  movie = query.data

  url = f'https://kemerovo.kinoafisha.info/movies/{movie}/#submenu'
  
  response = requests.get(url)
  response.raise_for_status()

  soup = BeautifulSoup(response.text, 'html.parser')

  cinemas = soup.find_all('div', class_='showtimes_item')
  for cinema in cinemas:
    print(cinema.prettify())
  
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

  return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
  await update.message.reply_text('Query cancelled.')

  return ConversationHandler.END