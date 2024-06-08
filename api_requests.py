import requests

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ChatAction

from bot_token import KINOPOISK_TOKEN

async def search_by_name(update: Update, context: CallbackContext):
  await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
  movie_name = ' '.join(context.args)
  if not movie_name:
    await update.message.reply_text("Пожалуйста, введите название фильма после команды /movie")
    return 0

  url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=10&query={movie_name}"

  headers = {
      "accept": "application/json",
      "X-API-KEY": KINOPOISK_TOKEN
  }

  response = requests.get(url, headers=headers)
  data = response.json()

  if data['total'] != 0:
    pull_data = dict()
    for movie in range(1): # range(len(data['docs'])):
      pull_data['Название'] = data['docs'][movie]['name']
      pull_data['Оригинальное название'] = data['docs'][movie]['alternativeName']
      if len(data['docs'][movie]['enName']) != 0:
        pull_data['Английское название'] = data['docs'][movie]['enName']

      pull_data['Рейтинг'] = {
        'Кинопоиск': str(data['docs'][movie]['rating']['kp']),
        'IMDb': str(data['docs'][movie]['rating']['imdb'])
      }
      if pull_data['Рейтинг']['Кинопоиск'] == '0':
        pull_data['Рейтинг']['Кинопоиск'] = 'N/A'
      if pull_data['Рейтинг']['IMDb'] == '0':
        pull_data['Рейтинг']['IMDb'] = 'N/A'

      if data['docs'][movie]['ageRating'] is None:
        pull_data['Возраст'] = 'N/A'
      else:
        pull_data['Возраст'] = str(data['docs'][movie]['ageRating']) + '+'
      pull_data['Тип'] = data['docs'][movie]['type']
      pull_data['Год производства'] = str(data['docs'][movie]['year'])

      pull_data['Страна'] = [country['name'] for country in data['docs'][movie]['countries']]
      pull_data['Жанр'] = [genre['name'] for genre in data['docs'][movie]['genres']]

      pull_data['Время'] = str(data['docs'][movie]['movieLength'])
      if data['docs'][movie]['seriesLength'] is not None:
        pull_data['Количество эпизодов'] = str(data['docs'][movie]['seriesLength'])
      if data['docs'][movie]['status'] is not None:
        pull_data['Статус'] = data['docs'][movie]['status']

      if len(data['docs'][movie]['releaseYears']) != 0:
        pull_data['Годы выпуска'] = [
          str(data['docs'][movie]['releaseYears'][0]['start']),
          str(data['docs'][movie]['releaseYears'][0]['end'])
          ]
        
      pull_data['Описание'] = data['docs'][movie]['description']

      pull_data['poster'] = data['docs'][movie]['poster']['url']
      pull_data['ID'] = str(data['docs'][movie]['id'])
  
      message = '*' + pull_data['Название'].upper() + '*\n'
      if pull_data['Тип'] == 'movie':
        message += f'[Посмотреть на Кинопоиске](https://www.kinopoisk.ru/film/{pull_data['ID']}/)\n'
      else:
        message += f'[Посмотреть на Кинопоиске](https://www.kinopoisk.ru/series/{pull_data['ID']}/)\n'
      message += 'ID: `' + pull_data['ID'] + '`\n\n'

      for key, value in pull_data.items():
        if key == 'Рейтинг':
          message += '*' + key + ' Кинопоиск:* ' + pull_data[key]['Кинопоиск'] + '\n*' + key + ' IMDb:* ' + pull_data[key]['IMDb'] + '\n'
        elif key == 'Страна' or key == 'Жанр':
          message += '*' + key + ':* '
          items = ""
          for item in value:
            items += item + ', '
          items = items[:-2]
          message += items + '\n'
        elif key == 'Тип':
          message += '*' + key + ':* '
          if value == 'movie':
            message += 'Фильм\n'
          else:
            message += 'Сериал\n'
        elif key == 'Годы выпуска':
          message += '*' + key + ':* '
          if value[0] == value[1]:
            message += value[0] + '\n'
          else:
            message += value[0] + '–' + value[1] + '\n'
        elif key == 'Время':
          if int(value) > 59:
            message += '*' + key + ':* ' + value + ' мин. / 0'
            time = (int(value) // 60, int(value) % 60)
            message += str(time[0]) + ':' + str(time[1]) + '\n\n'
          elif int(value) == 0:
            continue
          else:
            message += '*' + key + ':* ' + value + 'мин. / ' + '00:' + value + '\n\n'
        elif any([key == 'Название', key == 'poster', key == 'ID']):
          continue
        else:
          message += '*' + key + ':* ' + value + '\n'

    if pull_data['poster'] is None:
      await update.message.reply_text(
        text=message,
        parse_mode="Markdown",
        disable_web_page_preview=True)
    else:
      await update.message.reply_photo(
        photo=pull_data['poster'],
        caption=message,
        parse_mode="Markdown")
  else:
    await update.message.reply_text("Фильм не найден")

  return response.json()