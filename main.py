import telebot
from telebot import *
#from aiogram import *
#from aiogram.types import *
#from ChatGPT import *
#import sql
#import threading



token = '7342509477:AAHKGhqdN0ZXbmEnAYLcR7uuhhSy4sB7dd8'

bot = telebot.TeleBot(token)

logo = open('logo.jpg', 'rb')

@bot.message_handler(commands = ['start'])
def start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  bot.send_photo(message.chat.id, logo)
  btn1 = types.KeyboardButton("Заполнить свои персональные данные")
  markup.add(btn1)
  bot.send_message(message.chat.id, 'Привет, {}! Бот PROпиташка поможет тебе вести индивидуальный расчет твоего питания и активности, опираясь на твои персональные параметры)'.format(message.from_user.first_name), reply_markup=markup)
@bot.message_handler(content_types=['text'])
def func(message):
  if (message.text == 'Заполнить свои персональные данные'):
    hei = bot.send_message(message.chat.id, text = 'Введи свой рост в сантиметрах:', reply_markup= telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(hei, message_input_step)
def message_input_step(message):
  global length  # объявляем глобальную переменную
  length = int(message.text)
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
  else :
    sex = 'woman'
  ma = bot.send_message(message.chat.id, text='Введи свой вес:', reply_markup=telebot.types.ReplyKeyboardRemove())
  bot.register_next_step_handler(ma, choise_of_mass)
def choise_of_mass(message):
  global mass
  mass = int(message.text)
  mess_before_imt = bot.send_message(message.chat.id, text = 'Начинаю вычисление вашего индекса массы тела...')
  imt = round(mass / ((length/100) ** 2), 3)
  imt_using_words = str()
  if round(imt) < 15:
    imt_using_words = 'сильно меньше нормы'
  if round(imt) in range(16, 18):
    imt_using_words = 'Недостаточная масса '
  if round(imt) in range(18, 25):
    imt_using_words = 'Норма'
  if round(imt) > 26:
    imt_using_words = 'Ожирение'
  global cal
  if sex == 'man':
    cal = (10 * mass) + (6.25 * length) - (5 * age) + 5
  if sex == 'woman':
    cal = (10 * mass) + (6.25 * length) - (5 * age) - 161
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = 'Сброс веса'
  btn2 = 'Удержание массы'
  btn3 = 'Набор массы'
  markup.add(btn1, btn2, btn3)
  mes = bot.send_message(message.chat.id, text = '{}, твой вес: {}, твой рост: {}, твой индекс массы тела:{}, и твой вес - это {}. Сечас ты сможешь выбрать свою цель, чтобы я смог помочь тебе с твоим персональным планом питания:'.format(message.from_user.first_name, mass, length, imt, imt_using_words), reply_markup= markup)
  bot.register_next_step_handler(mes, quest)



@bot.message_handler(content_types=['text'])
def quest(message):
  global ans
  ans = message.text
  if (ans == 'Сброс веса'):
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 35/15/50, и в день вы должны потреблять {} килокалорий'.format(cal - cal/5))
  if (ans == 'Удержание веса'):
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(cal))
  if (ans == 'Набор массы'):
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(cal + 450))

bot.polling(none_stop=True)