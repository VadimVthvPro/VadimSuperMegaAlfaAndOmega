import telebot
from telebot import *
import sqlite3
from gigachat import *
from gigachat import GigaChat
import requests



conn = sqlite3.connect('pro3.db', check_same_thread=False)
cursor = conn.cursor()

def db_table_val(user_id: int , user_age: int,  user_height: int, user_sex: str, user_weight: float):
  cursor.execute('INSERT INTO users (user_id, user_height, user_age, user_sex, user_weight) VALUES (?, ?, ?, ?, ?)', (user_id, user_height, user_age, user_sex, user_weight))
  conn.commit()

token = '7239777184:AAEJCJcJx4_c9fuj9pIFKT3RlofrcnVV9Nk'

bot = telebot.TeleBot(token)


def message_input_step(message):
  global height  # объявляем глобальную переменную
  height = int(message.text)
  ye = bot.send_message(message.chat.id, text='Введи свой возраст')
  bot.register_next_step_handler(ye, choise_of_age)


def choise_of_age(message):
  global age
  age = int(message.text)
  btn1 = types.KeyboardButton("Мужчина")
  btn2 = types.KeyboardButton("Женщина")
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.add(btn1, btn2)
  se = bot.send_message(message.chat.id, text='Выбери свой пол:', reply_markup=markup)
  bot.register_next_step_handler(se, choise_of_sex)


def choise_of_sex(message):
  global sex
  if (message.text == 'Мужчина'):
    sex = 'man'
  else:
    sex = 'woman'
  ma = bot.send_message(message.chat.id, text='Введи свой вес:', reply_markup=telebot.types.ReplyKeyboardRemove())
  bot.register_next_step_handler(ma, choise_of_mass)


def choise_of_mass(message):
  global weight
  weight = float(message.text)
  db_table_val(user_id=message.from_user.id, user_height=height, user_age=age, user_sex=sex, user_weight=weight)
  count_imt(message)
def count_imt(message):
  btn = 'Рассчитать ИМТ'
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.add(btn)
  bot.send_message(message.chat.id, text='Далее стоит рассичтать ваш имт. ...', reply_markup=markup)
  global imt
  global imt_using_words
  imt = round(weight / ((height / 100) ** 2), 3)
  imt_using_words = str()
  if round(imt) < 15:
    imt_using_words = 'сильно меньше нормы'
  if round(imt) in range(15, 18):
    imt_using_words = 'Недостаточная масса '
  if round(imt) in range(18, 25):
    imt_using_words = 'Норма'
  if round(imt) in range(25 - 30):
    imt_using_words = 'Предожирение'
  if round(imt) in range(30-35):
    imt_using_words = 'Jжирение'
  global cal
  cal = 0
  if sex == 'man':
    cal = (10 * weight) + (6.25 * height) - (5 * age) + 5
  if sex == 'woman':
    cal = (10 * weight) + (6.25 * height) - (5 * age) - 161
  next_step(message)
def next_step(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = 'Сброс веса'
  btn2 = 'Удержание массы'
  btn3 = 'Набор массы'
  markup.add(btn1, btn2, btn3)
  po = bot.send_message(message.chat.id, text = '{}, твой вес: {}, твой рост: {}, твой индекс массы тела:{}, и твой вес - это {}. Сечас ты сможешь выбрать свою цель, чтобы я смог помочь тебе с твоим персональным планом питания:'.format(message.from_user.first_name, weight, height, imt, imt_using_words), reply_markup= markup)
  bot.register_next_step_handler(po, pohelan)

def pohelan(message):
  markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = 'Подсказка по рецепту'
  btn2 = 'Помощь с треней'
  markup1.add(btn1, btn2)
  global aim
  aim = message.text
  if aim == 'Сброс веса':
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 35/15/50, и в день вы должны потреблять {} килокалорий'.format(cal - cal/5), reply_markup= telebot.types.ReplyKeyboardRemove())
  if aim == 'Удержание массы':
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(cal), reply_markup= telebot.types.ReplyKeyboardRemove())
  if aim == 'Набор массы':
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(cal + 450), reply_markup= telebot.types.ReplyKeyboardRemove())
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = 'Недельный план питания'
  btn2 = 'Помощь с треней'
  markup.add(btn1, btn2)
  ans = bot.send_message(message.chat.id, text = 'Для того, чтобы тебе осуществить {}, тебе стоит наладить твоё питание и тренировки.  Этот мегабот тебе с этим поможет))'.format(message.text), reply_markup = markup)
  bot.register_next_step_handler(ans, ai)

def ai(message):
  with GigaChat(
        credentials='YzY3ZWQ3MmMtN2ZlOC00ZGQzLWE5OGEtOTBjMjdlMGZjMDJiOjQ4NTI4MDM1LTliNjgtNGIwOS1hZjk3LTFkNjU1MDk2NDM4Ng==',
        verify_ssl_certs=False) as giga:
    global response
    if message.text == 'Недельный план питания':
      response = giga.chat(
    f"Придумай индивидуальный план питания на неделю для человека, чей имт равен {imt} и чья цель {aim}")
    if message.text == 'Помощь с треней':
      response = giga.chat(
        f"Придумай индивидуальный план тренировок на неделю для человека, чей имт равен {imt} и чья цель {aim}")
  bot.send_message(message.chat.id, text = response.choices[0].message.content)



logo = open('logo.jpg', 'rb')

@bot.message_handler(commands = ['start'])
def start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  bot.send_photo(message.chat.id, logo)
  btn1 = types.KeyboardButton("Заполнить свои персональные данные")
  btn2 = types.KeyboardButton("Я уже активный пользователь")
  markup.add(btn1, btn2)
  bot.send_message(message.chat.id, 'Привет, {}! Бот PROпиташка поможет тебе вести индивидуальный расчет твоего питания и активности, опираясь на твои персональные параметры)'.format(message.from_user.first_name), reply_markup=markup)
@bot.message_handler(content_types=['text'])
def func(message):
  if (message.text == 'Заполнить свои персональные данные'):
    hei = bot.send_message(message.chat.id, text='Введи свой рост в сантиметрах:',
                           reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(hei, message_input_step)


  if message.text ==  'Я уже активный пользователь':
    global height, age, sex, weight
    cursor.execute(f"SELECT user_height, user_age, user_sex, user_weight FROM users WHERE user_id={message.from_user.id}")
    height, age,sex, weight = cursor.fetchone()
    count_imt(message)



bot.polling(none_stop=True)