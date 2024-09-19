import json
import telebot
from telebot import *
import sqlite3
from gigachat import GigaChat
import datetime
from translate import Translator
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
import PIL # type: ignore
import tensorflow as tf # type: ignore
from tensorflow import keras # type: ignore
from tensorflow.keras import layers # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
import pathlib


bot = telebot.TeleBot('7239777184:AAEJCJcJx4_c9fuj9pIFKT3RlofrcnVV9Nk', threaded=True)

class person:
  

global alfamarkup
alfamarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

conn = sqlite3.connect('pro3.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(user_id: int , user_age: int,  user_height: int, user_sex: str, user_weight: float, date:str, user_aim:str, imt:float, imt_str:str, cal:float):
  cursor.execute('INSERT INTO users (user_id, user_age, user_height,  user_sex, user_weight, date, user_aim, imt, imt_str, cal) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (user_id,  user_age, user_height,user_sex, user_weight, date, user_aim, imt, imt_str, cal))
  conn.commit()

def wat_co(count: int,user_id: int , date:str):
  cursor.execute('INSERT INTO water (count, user_id,  date) VALUES (?, ?, ?)', (count,user_id,  date))
  conn.commit()

def counting_users_cal_after_train( user_id: int ,date: str, user_train_cal: float, tren_time: int):
  cursor.execute('INSERT INTO user_training_cal (user_id, date, user_train_cal, tren_time) VALUES (?, ?, ?, ?)', (user_id, date, user_train_cal, tren_time))
  conn.commit()

def counting_users_pit( user_id: int ,date: str, user_name_of_food:str, b:float, g:float, u:float, food_cal:float ):
  cursor.execute('INSERT INTO user_pit (user_id, date, user_name_of_food, b, g, u, food_cal) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, date, user_name_of_food, b, g, u, food_cal))
  conn.commit()


dataset_dir = pathlib.Path("food-101")
batch_size = 32
img_width = 180
img_height = 180
train_ds = tf.keras.utils.image_dataset_from_directory(
	dataset_dir,
	validation_split=0.2,
	subset="training",
	seed=123,
	image_size=(img_height, img_width),
	batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
	dataset_dir,
	validation_split=0.2,
	subset="validation",
	seed=123,
	image_size=(img_height, img_width),
	batch_size=batch_size)

class_names = train_ds.class_names
print(f"Class names: {class_names}")


num_classes = len(class_names)
model = Sequential([
	tf.keras.layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),

	tf.keras.layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
	tf.keras.layers.RandomRotation(0.1),
	tf.keras.layers.RandomZoom(0.1),
	tf.keras.layers.RandomContrast(0.2),

	layers.Conv2D(16, 3, padding='same', activation='relu'),
	layers.MaxPooling2D(),

	layers.Conv2D(32, 3, padding='same', activation='relu'),
	layers.MaxPooling2D(),

	layers.Conv2D(64, 3, padding='same', activation='relu'),
	layers.MaxPooling2D(),

	layers.Dropout(0.2),

	layers.Flatten(),
	layers.Dense(128, activation='relu'),
	layers.Dense(num_classes)
])

model.compile(
    optimizer='adam',
 	loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy'])

model.load_weights("Foood.weights.h5")

loss, acc = model.evaluate(train_ds, verbose=2)
print("Restored model, accuracy: {:5.2f}%".format(100 * acc))



def message_input_step(message):
  global height
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
  sex = message.text
  ma = bot.send_message(message.chat.id, text='Введи свой вес', reply_markup=telebot.types.ReplyKeyboardRemove())
  bot.register_next_step_handler(ma, choise_of_mass)


def choise_of_mass(message):
  global weight
  weight = message.text
  if "," in weight:
    we1 = message.text.split(",")
    weight = int(we1[0]) + int(we1[1])/10**len(we1[1])
  else:
    weight = float(message.text)
  count_imt(message)

def count_imt(message):
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
  if round(imt) in range(25, 30):
    imt_using_words = 'Предожирение'
  if round(imt) > 30:
    imt_using_words = 'Ожирение'
  global cal
  cal = 0
  if sex == 'Мужчина':
    cal = (10 * weight) + (6.25 * height) - (5 * age) + 5
  if sex == 'Женщина':
    cal = (10 * weight) + (6.25 * height) - (5 * age) - 161
  giving_data(message)



def giving_data(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = 'Сброс веса'
  btn2 = 'Удержание массы'
  btn3 = 'Набор массы'
  markup.add(btn1, btn2, btn3)
  po = bot.send_message(message.chat.id, text = '{}, твой вес: {}, твой рост: {}, твой индекс массы тела:{}, и твой вес - это {}. Сечас ты сможешь выбрать свою цель, чтобы я смог помочь тебе с твоим персональным планом питания:'.format(message.from_user.first_name, weight, height, imt, imt_using_words), reply_markup= markup)
  bot.register_next_step_handler(po, aim)



def aim(message):
  global aim
  aim = message.text
  db_table_val(user_id=message.from_user.id, user_height=height, user_age=age, user_sex=sex, user_weight=weight, date = datetime.datetime.now().strftime('%Y-%m-%d'), user_aim=aim, imt = imt, imt_str = imt_using_words, cal = cal)
  aim_work(message)



def aim_work(message):
  cursor.execute("SELECT user_aim, cal,user_sex, user_age, imt FROM users WHERE date = ? AND user_id = ?",
                 (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
  aim, cal, sex, age, imt = cursor.fetchone()
  if aim == 'Сброс веса':
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 35/15/50, и в день вы должны потреблять {} килокалорий'.format(cal - cal/5), reply_markup= telebot.types.ReplyKeyboardRemove())
  if aim == 'Удержание массы':
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(cal), reply_markup= telebot.types.ReplyKeyboardRemove())
  if aim == 'Набор массы':
    bot.send_message(message.chat.id, text = 'Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(cal + 450), reply_markup= telebot.types.ReplyKeyboardRemove())
  bot.send_message(message.chat.id, text = 'Для того, чтобы тебе осуществить {}, тебе стоит наладить твоё питание и тренировки.  Этот мегабот тебе с этим поможет)) Сейчас сюда придут сообщения с твоими недельными планами тренировок и питания,которые ты так-же сможешь найти в закреплённых сообщениях'.format(message.text))
  with GigaChat(
        credentials='YzY3ZWQ3MmMtN2ZlOC00ZGQzLWE5OGEtOTBjMjdlMGZjMDJiOjQ4NTI4MDM1LTliNjgtNGIwOS1hZjk3LTFkNjU1MDk2NDM4Ng==',
       verify_ssl_certs=False) as giga:
          global plan_train, plan_pit
          plan_pit= giga.chat(
    f"Придумай индивидуальный план разнообразного питания на неделю для {sex},чей рост равен {height}, возраст равен {age}, имт равен {imt} и цель {aim}")
          plan_train = giga.chat(
        f"Придумай индивидуальный план тренировок на неделю для {sex}, чей рост равен {height}, возраст равен {age},  чей имт равен {imt} , чья цель {aim} и чей индивидуальный план питания {plan_pit.choices[0].message.content}")
          plan_pit_mes = bot.send_message(message.chat.id, text = plan_pit.choices[0].message.content, reply_markup=telebot.types.ReplyKeyboardRemove()).message_id
          plan_train_mes = bot.send_message(message.chat.id, text = plan_train.choices[0].message.content, reply_markup=telebot.types.ReplyKeyboardRemove()).message_id
          bot.pin_chat_message(chat_id=message.chat.id, message_id= plan_pit_mes)
          bot.pin_chat_message(chat_id=message.chat.id, message_id= plan_train_mes)

  btn1 = 'Добавить тренировки'
  btn2 = 'Ввести еду за день'
  btn3 = 'Сводка'
  btn4 = 'Помочь с рецептом'
  btn7 = 'Помочь с тренировкой'
  btn5 = 'Добавить выпитый стаканчик воды'
  btn6 = 'Присоедениться к чату '
  alfamarkup.add(btn1, btn2, btn3)
  alfamarkup.row(btn4)
  alfamarkup.row(btn7)
  alfamarkup.row(btn5)
  alfamarkup.row(btn6)
  mes = bot.send_message(message.chat.id,
                   text='Выданные планы питания и тренировок являются лишь рекоменданиями, которые ты можешь выполнять по желанию. Теперь ты можешь вводить продукты, которые ты сегодня употребил и тренировки, которые ты сегодня прошёл, а в конце дня ты будешь получать отчёт по твоим Б/Ж/У за день и затраченным калориям',
                   reply_markup=alfamarkup)
  bot.register_next_step_handler(mes, account)
def ai_rec(message):
  meal = message.text
  with GigaChat(
        credentials='YzY3ZWQ3MmMtN2ZlOC00ZGQzLWE5OGEtOTBjMjdlMGZjMDJiOjQ4NTI4MDM1LTliNjgtNGIwOS1hZjk3LTFkNjU1MDk2NDM4Ng==',
       verify_ssl_certs=False) as giga:
          global rec
          rec= giga.chat(
    f"Придумай новый рецепт {meal} с рекомендациями по готовке")
          bot.send_message(message.chat.id, text = rec.choices[0].message.content, reply_markup=alfamarkup)



def intensiv(message):
  global intensivity
  if message.text == 'Лёгкая':
    intensivity = 2.5
  if message.text == 'Умеренная':
    intensivity = 3
  if message.text == 'Тяжёлая':
    intensivity = 3.5
  mes = bot.send_message(message.chat.id, text='Хорошо, а теперь введи,сколько минут длилась твоя тренировка:',
                   reply_markup=telebot.types.ReplyKeyboardRemove())
  bot.register_next_step_handler(mes, ttime)



def ttime(message):
  cursor.execute("SELECT user_weight FROM users WHERE date = ? AND user_id = ?",
                 (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
  weight = float(cursor.fetchone()[-1])

  time = int(message.text)
  tren_cal = round((weight * intensivity * time / 24), 3)
  bot.send_message(message.chat.id, text=f'Прекрасно! Ты за тренировку сжёг {tren_cal} килокалорий. Так держать!!',
                   reply_markup=alfamarkup)
  counting_users_cal_after_train(user_id=message.from_user.id, date = datetime.datetime.now().strftime('%Y-%m-%d') ,user_train_cal = tren_cal , tren_time = time)
  global col_cal_tren, data, itog_cal
  cursor.execute("SELECT SUM(user_train_cal) FROM user_training_cal WHERE date = ? AND user_id = ?",
                 (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
  result = cursor.fetchone()
  col_cal_tren = result[0]
  bot.send_message(message.chat.id, text = f'{message.from_user.first_name}, за сегодня ты сжёг {col_cal_tren} килокалорий. Так держать!!')



def is_not_none(item):
  return item is not None



def upd_svo(message):
  new_weight = float(message.text)
  db_table_val(user_id=message.from_user.id, user_height=height, user_age=age, user_sex=sex, user_weight=new_weight, date = datetime.datetime.now().strftime('%Y-%m-%d'), user_aim=aim, imt = imt, imt_str = imt_using_words, cal = cal)
  bef_svo(message)



def bef_svo(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = 'За день'
  btn2 = 'За месяц'
  btn3 = 'За год'
  markup.add(btn1, btn2, btn3)
  que = bot.send_message(message.chat.id, text='За какой период ты хочешь увидеть сводку?', reply_markup=markup)
  bot.register_next_step_handler(que, svodka)



def svodka(message):
  global weight_data
  if message.text == 'За день':
    cursor.execute("SELECT SUM(user_train_cal) FROM user_training_cal WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    result_tren = cursor.fetchone()
    col_call_tren = result_tren[0]
    cursor.execute("SELECT SUM(food_cal) FROM user_pit WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    result_cal_food= cursor.fetchone()
    col_cal_food=result_cal_food[0]
    cursor.execute("SELECT SUM(b) FROM user_pit WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    result_b = cursor.fetchone()
    col_b=result_b[0]
    cursor.execute("SELECT SUM(g) FROM user_pit WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    result_g = cursor.fetchone()
    col_g=result_g[0]
    cursor.execute("SELECT SUM(u) FROM user_pit WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    result_u = cursor.fetchone()
    col_u=result_u[0]
    cursor.execute("SELECT SUM(count) FROM water WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    result_wat = cursor.fetchone()
    col_wat = result_wat[0]
    cursor.execute("SELECT user_name_of_food FROM user_pit WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    ff = ''
    result_ff = cursor.fetchall()
    for i in result_ff:
      ff += str(i[0])
      ff += ', '

    bot.send_message(message.chat.id, text = f"""
{message.from_user.first_name}, 
за {datetime.datetime.now().strftime('%Y-%m-%d')} у тебя такие результаты:
во время тренировок ты сбросил {round(col_call_tren, 3) if col_call_tren else 0} килокалорий, 
сегодняшний твой рацион состоял из {ff} калорийность рациона составила {round(col_cal_food, 3) if col_cal_food else 0}, 
за день было употреблено Б/Ж/У в соотношении {col_b if col_b else 0}/{col_g if col_g else 0}/{col_u if col_u else 0} и выпито {col_wat * 300 if col_wat else 0} милилитров воды. Я верю в твой успех!!""", reply_markup=alfamarkup)
  elif message.text == 'За месяц':
    weight_month = []
    sr_b = []
    sr_g = []
    sr_u = []
    sr_cal = []
    sr_w = []
    sr_tren = []
    for i in range(1, 32):
      datee = f'{str(datetime.datetime.now().year)}-{str(datetime.datetime.now().month).zfill(2)}-{str(i).zfill(2)}'
      cursor.execute("SELECT user_weight FROM users WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      weight_data = cursor.fetchall()
      if weight_data:
        weight_month.append(weight_data)
      cursor.execute("SELECT sum(b) FROM user_pit WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      b_data = cursor.fetchone()
      if b_data:
        sr_b.append(b_data[0])
      cursor.execute("SELECT sum(g) FROM user_pit WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      g_data = cursor.fetchone()
      if g_data:
        sr_g.append(g_data[0])
      cursor.execute("SELECT sum(u) FROM user_pit WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      u_data = cursor.fetchone()
      if u_data:
        sr_u.append(u_data[0])
      cursor.execute("SELECT sum(count) FROM water WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      w_data = cursor.fetchone()
      if w_data:
        sr_w.append(w_data[0])
      cursor.execute("SELECT sum(user_train_cal) FROM user_training_cal WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      cal_data = cursor.fetchone()
      if cal_data:
        sr_cal.append(cal_data[0])
      cursor.execute("SELECT sum(tren_time) FROM user_training_cal WHERE user_id = ? AND date = ?",
                     (message.from_user.id, datee))
      time_data = cursor.fetchone()
      if time_data:
        sr_tren.append(time_data[0])
    if weight_month and sr_b and sr_g and sr_u and sr_cal and sr_tren and sr_w:
      weig_1 = weight_month[0][0]
      weig_2 = weight_month[-1][-1]
      new_sr_b = list(filter(is_not_none, sr_b))
      new_sr_g = list(filter(is_not_none, sr_g))
      new_sr_u = list(filter(is_not_none, sr_u))
      new_sr_w = list(filter(is_not_none, sr_w))
      new_sr_cal = list(filter(is_not_none, sr_cal))
      new_sr_tren = list(filter(is_not_none, sr_tren))
      avg_b = round(sum(new_sr_b) / len(new_sr_b), 3)
      avg_g = round(sum(new_sr_g) / len(new_sr_g), 3)
      avg_u = round(sum(new_sr_u) / len(new_sr_u), 3)
      avg_training_time = round(sum(new_sr_tren) / len(new_sr_tren), 3)  # Расчет среднего времени тренировок
      avg_calories_burned = round(sum(new_sr_cal) / len(new_sr_cal), 3)  # Расчет среднего числа сожжённых калорий
      bot.send_message(message.chat.id, text=f"""
  {message.from_user.first_name}, за месяц произошли такие изменения:
  твой вес изменился с {weig_1[0]} на {weig_2[0]}, 
  в день ты тренировался {avg_training_time} минут каждый день, сжигая при этом в среднем {avg_calories_burned} килокалорий,
  в день твои Б/Ж/У были в соотношении {avg_b}/{avg_g}/{avg_u} и выпивалось около {sum(new_sr_w)/len(new_sr_w) * 300} милилитров воды.Я в тебя верю!""",
                       reply_markup=alfamarkup)
    else:
      bot.send_message(message.chat.id, "Нет данных за этот месяц.")
  elif message.text == 'За год':
    all_data = []
    total_food_cal = 0
    total_b = 0
    total_g = 0
    total_u = 0
    total_w = 0
    weight_data_all = []
    food_months_with_data = set()

    current_date = datetime.datetime.now()

    for i in range(12):
      current_month = current_date.month - i
      current_year = current_date.year

      if current_month <= 0:
        current_year -= 1
        current_month += 12

      first_day_of_month = datetime.date(current_year, current_month, 1)
      if current_month == 12:
        last_day_of_month = datetime.date(current_year + 1, 1, 1) - datetime.timedelta(days=1)
      else:
        last_day_of_month = datetime.date(current_year, current_month + 1, 1) - datetime.timedelta(days=1)

      cursor.execute("""
                SELECT SUM(food_cal), SUM(b), SUM(g), SUM(u)
                FROM user_pit 
                WHERE date >= ? AND date <= ? AND user_id = ?
                GROUP BY strftime('%Y-%m', date)
            """, (first_day_of_month.strftime('%Y-%m-%d'), last_day_of_month.strftime('%Y-%m-%d'), message.from_user.id))
      result_food = cursor.fetchone()
      cursor.execute("""
                      SELECT SUM(count)
                      FROM water
                      WHERE date >= ? AND date <= ? AND user_id = ?
                      GROUP BY strftime('%Y-%m', date)
                  """, (first_day_of_month.strftime('%Y-%m-%d'), last_day_of_month.strftime('%Y-%m-%d'), message.from_user.id))
      result_wat = cursor.fetchone()
      if result_food and result_food[0]:
        all_data.append(result_food)
        total_food_cal += result_food[0]
        total_b += result_food[1]
        total_g += result_food[2]
        total_u += result_food[3]
        food_months_with_data.add((current_year, current_month))
      if result_wat and result_wat[0]:
        total_w += result_wat[0]
      cursor.execute("""
                SELECT date, user_weight 
                FROM users 
                WHERE date >= ? AND date <= ? AND user_id = ?
                ORDER BY date ASC
            """, (first_day_of_month.strftime('%Y-%m-%d'), last_day_of_month.strftime('%Y-%m-%d'), message.from_user.id))
      weight_data = cursor.fetchall()

      if weight_data:
        weight_data_all.extend(weight_data)


    if weight_data_all:
      weight_data_all.sort(key=lambda x: x[0])
      start_weight = weight_data_all[0][1]
      end_weight = weight_data_all[-1][1]
    else:
      start_weight = 'нет данных'
      end_weight = 'нет данных'

    cursor.execute("""
            SELECT AVG(user_train_cal) 
            FROM user_training_cal 
            WHERE user_id = ?
        """, (message.from_user.id,))
    result_train = cursor.fetchone()
    avg_train_cal = result_train[0] if result_train and result_train[0] else 0

    avg_food_cal = total_food_cal / len(food_months_with_data) if food_months_with_data else 0
    avg_b = round(total_b / len(food_months_with_data), 3) if food_months_with_data else 0
    avg_g = round(total_g / len(food_months_with_data), 3) if food_months_with_data else 0
    avg_u = round(total_u / len(food_months_with_data), 3) if food_months_with_data else 0
    all_data = list(filter(is_not_none, all_data))
    bot.send_message(message.chat.id, text = f"""
За последние 12 месяцев:
твой вес изменился с {start_weight} на {end_weight};
в среднем за месяц ты сжигал {avg_train_cal:.1f} килокалорий на тренировках;
в  среднем твой рацион составлял {avg_food_cal:.2f} килокалорий
в начале года твой рацион составлял {all_data[-1][0]} килокаларий , а конечное значение {all_data[0][0]} килокалорий,
соотношение Б/Ж/У в среднем: {avg_b:.2f}/{avg_g:.2f}/{avg_u:.2f}, 
в начале года твои Б/Ж/У составляли соотношение {round(all_data[-1][1], 3)}/{round(all_data[-1][2], 3)}/{round(all_data[-1][3], 3)} , а конечное значение {round(all_data[0][1], 3)}/{round(all_data[0][2], 3)}/{round(all_data[0][3], 3)},
и было выпито в среднем {total_w/len(food_months_with_data) * 300} воды каждый день.""",reply_markup=alfamarkup)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
  global name_a
  name_a = []
  photo = message.photo[-1]
  file_info = bot.get_file(photo.file_id)
  downloaded_file = bot.download_file(file_info.file_path)
  save_path = 'photo.jpg'
  with open(save_path, 'wb') as new_file:
      new_file.write(downloaded_file)
  bot.send_message(message.chat.id, 'фото схранено')
  img = tf.keras.utils.load_img( "photo.jpg", target_size=(img_height, img_width))
  img_array = tf.keras.utils.img_to_array(img)
  img_array = tf.expand_dims(img_array, 0)
  predictions = model.predict(img_array)
  score = tf.nn.softmax(predictions[0])
  lol =str(class_names[np.argmax(score)])
  translator = Translator(from_lang="en", to_lang="ru")
  name_a.append(translator.translate(lol).title())
  mes = bot.send_message(message.chat.id, text = "Введи, сколько грамм было в этом блюде")
  bot.register_next_step_handler(mes, food_sql)



def new_tren(message):
  global tren_aim
  global tr
  cursor.execute("SELECT user_aim, cal,user_sex,user_weight, user_age, imt FROM users WHERE date = ? AND user_id = ?",
                 (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
  aim, cal, sex, user_weight, age, imt = cursor.fetchone()
  tren_aim = message.text
  with GigaChat(credentials='YzY3ZWQ3MmMtN2ZlOC00ZGQzLWE5OGEtOTBjMjdlMGZjMDJiOjQ4NTI4MDM1LTliNjgtNGIwOS1hZjk3LTFkNjU1MDk2NDM4Ng==',verify_ssl_certs=False) as giga:
    tr = giga.chat(f"Придумай идеальный план на одну тренировку для {sex} {age} лет весом {weight}, который хотел бы сейчас {tren_aim}")
    bot.send_message(message.chat.id, text = tr.choices[0].message.content, reply_markup=alfamarkup)





@bot.message_handler(commands = ['start'])
def start(message):
  p = open('new_logo.jpg', 'rb')
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton("Регистрация")
  btn2 = types.KeyboardButton("Вход")
  markup.add(btn1, btn2)
  bot.send_photo(message.chat.id, photo = p, caption = 'Привет, {}! Бот PROпиташка поможет тебе вести индивидуальный расчет твоего питания и активности, опираясь на твои персональные параметры)'.format(message.from_user.first_name), reply_markup=markup)


def choiser(message):
  if message.text == 'Ввести названия блюд':
    mes = bot.send_message(message.chat.id, text = 'Перечисли через запятую названия блюд:', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(mes,work_with_food)
  if message.text == 'Сфотографировать блюдо':
    bot.send_message(message.chat.id, text = 'Отправь фото блюда, чтобы система её распознала:', reply_markup=telebot.types.ReplyKeyboardRemove())

def work_with_food(message):
  global name_a
  name_a = message.text.replace(" ", "").split(",")
  if len(name_a) == 1:
    mes = bot.send_message(message.chat.id, text = 'Введи, сколько грамов было в этом блюде:')
    bot.register_next_step_handler(mes, food_sql)
  else:
    mes = bot.send_message(message.chat.id, text='Введи, сколько грамов было в этих блюдах:')
    bot.register_next_step_handler(mes, food_sql)



def food_sql(message):
    global gram
    gram = message.text.replace(" ", "").split(",")
    for m in range(len(name_a)):
      with open('products.json') as f:
        file_content = f.read()
        foods = json.loads(file_content)
        for i in range(len(foods)):
          if foods[i]["name"] == name_a[m].title():
            b = round(float(foods[i]["bgu"].split(',')[0]) * float(gram[m]) / 100, 3)
            g = round(float(foods[i]["bgu"].split(',')[1])* float(gram[m]) / 100, 3)
            u = round(float(foods[i]["bgu"].split(',')[2])* float(gram[m]) / 100, 3)
            food_cal = float(foods[i]["kcal"])*float(gram[m]) / 100
            counting_users_pit(user_id=message.from_user.id, date = datetime.datetime.now().strftime('%Y-%m-%d'), user_name_of_food= name_a[m].title(), b=b, g=g, u=u, food_cal = food_cal)
    bot.send_message(message.chat.id, text = 'Данные записаны)',reply_markup=alfamarkup)

def registr(message):
  hei = bot.send_message(message.chat.id, text='Введи свой рост в сантиметрах:',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
  bot.register_next_step_handler(hei, message_input_step)



def log_in(message):
  cursor.execute("SELECT user_age, user_height,  user_sex, user_weight, user_aim, imt, imt_str, cal FROM users WHERE user_id = ? AND date = ?",
                 (message.from_user.id, datetime.datetime.now().strftime('%Y-%m-%d') ))
  if cursor.fetchone():
    global weight, height, imt, imt_using_words
    cursor.execute("SELECT user_weight, user_height, imt, imt_str FROM users WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    weight, height, imt, imt_using_words = cursor.fetchone()
    aim_work(message)
  else:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = 'Регистрация'
    markup.add(btn)
    bot.send_message(message.chat.id, text = 'Твоих данных в базе нету :( Для начала пройди регистрацию', reply_markup=markup)





@bot.message_handler(content_types=['text'])
def account(message):
  if message.text == 'Добавить тренировки':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = 'Лёгкая'
    btn2 = 'Умеренная'
    btn3 = 'Тяжёлая'
    markup.add(btn1, btn2, btn3)
    mes = bot.send_message(message.chat.id, text = 'Какая была тренировка:', reply_markup= markup)
    bot.register_next_step_handler(mes, intensiv)
  if message.text == 'Ввести еду за день':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = 'Сфотографировать блюдо'
    btn2 = 'Ввести названия блюд'
    markup.add(btn1, btn2)
    mes = bot.send_message(message.chat.id, text = 'Выбери способ, как добавить еду за день:',  reply_markup=markup)
    bot.register_next_step_handler(mes,choiser)
  if message.text == 'Сводка':
    cursor.execute("SELECT user_weight FROM users WHERE date = ? AND user_id = ?",
                   (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    weight = cursor.fetchone()
    if weight:
      bef_svo(message)

    else:
      mes = bot.send_message(message.chat.id, text = 'Для обновления данных введи свой вес в формате килограмм.грамм')
      bot.register_next_step_handler(mes, upd_svo)
  if message.text == 'Помочь с рецептом':
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = 'На завтрак'
    btn2 = 'На обед'
    btn3 = 'На ужин'
    markup.add(btn1, btn2, btn3)
    mes = bot.send_message(message.chat.id, text = 'На какой приём пищи выбираем рецепт?', reply_markup=markup)
    bot.register_next_step_handler(mes, ai_rec)
  if message.text == 'Добавить выпитый стаканчик воды':
    wat_co(user_id=message.from_user.id, count = 1, date = datetime.datetime.now().strftime('%Y-%m-%d'))
    bot.send_message(message.chat.id, text = 'Стакан добавлен)',reply_markup=alfamarkup)
  if message.text == 'Присоедениться к чату':
    bot.send_message(message.chat.id, text = 'https://t.me/+QVhMA2topDgzOWVi')
  if message.text == 'Помочь с тренировкой':
    markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = 'Кардио'
    btn2 = 'Силовая'
    btn3 = 'Растяжка'
    markup1.add(btn1, btn2, btn3)
    mes = bot.send_message(message.chat.id, text = 'Выбери тип желаемой тренировки:', reply_markup=markup1)
    bot.register_next_step_handler(mes, new_tren)
  if (message.text == 'Регистрация'):
    registr(message)
  if message.text ==  'Вход' :
    log_in(message)


bot.polling(none_stop=True)

