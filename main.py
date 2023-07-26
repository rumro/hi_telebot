import os
import subprocess
from urllib.parse import urlencode

import requests
import speech_recognition as sr
import telebot
from dotenv import load_dotenv
from requests import exceptions as ex
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from secret import *

load_dotenv()
api_tg_token = os.getenv('TG_TOKEN')

base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
photo = {
    'selfie': selfie_url,
    'school': school_url
}

voice = {
    'gpt': os.path.join("source", "gpt.ogg"),
    'sql': os.path.join("source", "sql.ogg"),
    'love': os.path.join("source", "love.ogg")
}

bot = telebot.TeleBot(api_tg_token)


def download_resp(url):
    """Запрос на Яндекс Диск"""
    final_url = base_url + urlencode(dict(public_key=url))
    response = requests.get(final_url)
    download_url = response.json()['href']
    return requests.get(download_url)


def build_menu(buttons=None, n_cols=3, footer_button=None):
    menu = []
    if buttons:
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if footer_button:
        menu.append([InlineKeyboardButton(text='Назад', callback_data='back')])
    return menu


def choice(message):
    try:
        message.text = message.text.lower()
        if any(word in message.text for word in (
                'селф', 'self', 'последн', 'last'
        )):
            mes = 'selfie'
            keyboard = InlineKeyboardMarkup(build_menu(footer_button=True))
            bot.send_photo(message.chat.id,
                           photo[mes],
                           reply_markup=keyboard)
        elif 'школ' in message.text:
            mes = 'school'
            keyboard = InlineKeyboardMarkup(build_menu(footer_button=True))
            bot.send_photo(message.chat.id,
                           photo[mes],
                           reply_markup=keyboard)
        elif any(git in message.text for git in ('git', 'гит', 'гид', 'реп')):
            mes = "Вот ссылка на github"
            button_list = [
                InlineKeyboardButton(text='bot на github',
                                     url=git_url)
            ]
            keyboard = InlineKeyboardMarkup(build_menu(buttons=button_list,
                                                       footer_button=True))
            bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)
        elif any(hob in message.text for hob in (
                'хоб]', 'hob', 'любим', 'себ', 'своё'
        )):
            mes = 'hobby'
            with open('downloaded_file.txt', 'wb') as f:
                f.write(download_resp(text_url).content)
            with open('downloaded_file.txt', 'r', encoding='utf-8') as f:
                text = f.read()
            keyboard = InlineKeyboardMarkup(build_menu(footer_button=True))
            bot.send_message(message.chat.id,
                             text=text,
                             reply_markup=keyboard)
        print('Ok:', message.text)
    except KeyError:
        print(message.text)


@bot.message_handler(commands=['start', 'git'])
def handle_start(message):
    if message.text == '/start':
        text = 'Что ты хочешь обо мне узнать?'
        button_list = [
            InlineKeyboardButton(text='Фото', callback_data='photo'),
            InlineKeyboardButton(text='О себе', callback_data='post'),
            InlineKeyboardButton(text='Болтовня', callback_data='voice')
        ]
        keyboard = InlineKeyboardMarkup(build_menu(button_list, 2))
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard)
    elif message.text == '/git':
        mes = "Вот ссылка на github"
        button_list = [
            InlineKeyboardButton(text='bot на github',
                                 url=git_url)
        ]
        keyboard = InlineKeyboardMarkup(build_menu(buttons=button_list,
                                                   footer_button=True))
        bot.send_message(message.chat.id, text=mes, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    if callback.data == 'photo':
        text = 'Какое фото хочешь посмотреть?'
        button_list = [
            InlineKeyboardButton(text='Последнее селфи',
                                 callback_data='selfie'),
            InlineKeyboardButton(text='Школьное фото',
                                 callback_data='school')
        ]
        keyboard = InlineKeyboardMarkup(build_menu(buttons=button_list,
                                                   footer_button=True))
        bot.send_message(callback.message.chat.id,
                         text=text,
                         reply_markup=keyboard)
    elif callback.data == 'post':
        with open('downloaded_file.txt', 'wb') as f:
            f.write(download_resp(text_url).content)
        with open('downloaded_file.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        keyboard = InlineKeyboardMarkup(build_menu(footer_button=True))
        bot.send_message(callback.message.chat.id,
                         text=text,
                         reply_markup=keyboard)
    elif callback.data == 'voice':
        text = 'О чём хочешь послушать?'
        button_list = [
            InlineKeyboardButton(text='О GPT',
                                 callback_data='gpt'),
            InlineKeyboardButton(text='Об SQL',
                                 callback_data='sql'),
            InlineKeyboardButton(text='О любви',
                                 callback_data='love')
        ]
        keyboard = InlineKeyboardMarkup(build_menu(buttons=button_list,
                                                   footer_button=True))
        bot.send_message(callback.message.chat.id,
                         text=text,
                         reply_markup=keyboard)
    elif callback.data in ('selfie', 'school'):
        keyboard = InlineKeyboardMarkup(build_menu(footer_button=True))
        bot.send_photo(callback.message.chat.id,
                       photo[callback.data],
                       reply_markup=keyboard)
    elif callback.data in ('gpt', 'sql', 'love'):
        keyboard = InlineKeyboardMarkup(build_menu(footer_button=True))
        bot.send_voice(callback.message.chat.id,
                       open(voice[callback.data], 'rb'),
                       reply_markup=keyboard)
    elif callback.data == 'back':
        text = 'Что ты хочешь обо мне узнать?'
        button_list = [
            InlineKeyboardButton(text='Фото', callback_data='photo'),
            InlineKeyboardButton(text='О себе', callback_data='post'),
            InlineKeyboardButton(text='Болтовня', callback_data='voice')
        ]
        keyboard = InlineKeyboardMarkup(build_menu(button_list, 2))
        bot.send_message(callback.message.chat.id,
                         text=text,
                         reply_markup=keyboard)


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('new_file.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    process = subprocess.run(['ffmpeg', '-i', 'new_file.ogg', 'new_file.wav'])
    if process.returncode != 0:
        raise Exception("Something went wrong")
    recognize = sr.Recognizer()
    file = sr.AudioFile('new_file.wav')
    try:
        with file as source:
            recognize.adjust_for_ambient_noise(source)
            audio = recognize.record(source)
        result = recognize.recognize_google(audio, language="ru-RU").lower()
        message.text = result
        bot.send_message(message.chat.id, text=message.text)
        choice(message)
    except sr.UnknownValueError:
        bot.send_message(message.chat.id, text='Google твоя не алё')
        print('Google твоя не алё')
    except ex.RequestException:
        print('requests')
    except ex.ReadTimeout:
        print('requests')
    except Exception as er:
        print(str(er))
    finally:
        os.remove("new_file.wav")


bot.infinity_polling()
