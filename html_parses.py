import requests

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from telegram.constants import ChatAction
from bs4 import BeautifulSoup

async def search_afisha(update: Update, context: CallbackContext):

  date = context.args
  # URL веб-страницы с афишей кино
  url = f'https://afisha.yandex.ru/kemerovo/cinema?date={date}&period=1'

  # Получение содержимого веб-страницы
  response = requests.get(url)
  response.raise_for_status()

  # Парсинг содержимого веб-страницы с помощью BeautifulSoup
  soup = BeautifulSoup(response.text, 'html.parser')

  # Найти все элементы, содержащие информацию о фильмах
  movies = soup.find_all('div', attrs={'data-component':'EventCard'})
  # Словарь для хранения названий фильмов и ссылок на страницы с сеансами
  movies_dict = dict()
  for movie in movies:
    movie_title = movie.find('h2').get_text()
    movie_link = movie.find('a')
    movies_dict[movie_title] = "https://afisha.yandex.ru" + movie_link['href']
  
  keyboard = []
  for movie, link in movies_dict.items():
    keyboard.append([InlineKeyboardButton(movie, callback_data=link)])

  markup = InlineKeyboardMarkup(keyboard)

  message = f'Кино в Кемерове на {date}:\n\n'

  period = 1
  for movie in movies_dict.keys():
    message += str(period) + movie + '\n'
    period += 1

  update.message.reply_text(text=message, reply_markup=markup)

    