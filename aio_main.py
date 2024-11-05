import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import types
import sqlite3
import datetime
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from gigachat import GigaChat



import keyboards as kb

from dotenv import load_dotenv
import os

class REG(StatesGroup):
    height = State()
    age = State()
    sex = State()
    want = State()
    weight = State()
    ais = State()

conn = sqlite3.connect('pro3.db', check_same_thread=False)
cursor = conn.cursor()

response = None

def db_table_val(user_id: int, user_age: int, user_sex: str, user_weight: float, date: str, user_aim: str, imt: float,
                 imt_str: str, cal: float, user_height: int):
    cursor.execute(
        'INSERT INTO users (user_id, user_age,  user_sex, user_weight, date, user_aim, imt, imt_str, cal, user_height) VALUES (?, ?, ?, ?, ?, ?, ?, ?,  ?, ?)',
        (user_id, user_age, user_sex, user_weight, date, user_aim, imt, imt_str, cal, user_height))
    conn.commit()


def wat_co(count: int, user_id: int, date: str):
    cursor.execute('INSERT INTO water (count, user_id,  date) VALUES (?, ?, ?)', (count, user_id, date))
    conn.commit()


def counting_users_cal_after_train(user_id: int, date: str, user_train_cal: float, tren_time: int):
    cursor.execute('INSERT INTO user_training_cal (user_id, date, user_train_cal, tren_time) VALUES (?, ?, ?, ?)',
                   (user_id, date, user_train_cal, tren_time))
    conn.commit()

load_dotenv()
bot = Bot(os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        types.FSInputFile(path='new_logo.jpg'),caption='Привет, {}! Бот PROпиташка поможет тебе вести индивидуальный расчет твоего питания и активности, опираясь на твои персональные параметры)'.format(message.from_user.first_name), reply_markup= kb.startMenu

    )
@dp.message(F.text == "Вход")
async def entrance(message: Message, state: FSMContext):
    cursor.execute(
        "SELECT user_age, user_height,  user_sex, user_weight, user_aim, imt, imt_str, cal FROM users WHERE user_id = ? AND date = ?",
        (message.from_user.id, datetime.datetime.now().strftime('%Y-%m-%d')))
    if cursor.fetchone():
        cursor.execute(
            "SELECT user_height, user_weight,imt, imt_str FROM users WHERE user_id = ? AND date = ?",
            (message.from_user.id, datetime.datetime.now().strftime('%Y-%m-%d')))
        height, weight, imt, imt_using_words = cursor.fetchone()
        await state.set_state(REG.ais)
        await bot.send_message(message.chat.id,
                         text='{}, твой вес: {}, твой рост: {}, твой индекс массы тела:{}, и твой вес - это {}. '.format(
                             message.from_user.first_name, weight, height, imt, imt_using_words))

    else:
        await bot.send_message(message.chat.id, text='Твоих данных в базе нету :( Для начала пройди регистрацию',
                         reply_markup=kb.reRig)


@dp.message(F.text == 'Регистрация')
async def registration(message: Message, state = FSMContext ):
    db_table_val(user_id=message.from_user.id, date=datetime.datetime.now().strftime('%Y-%m-%d'), user_aim=str(),
                 imt=float(), imt_str=str(), cal=float(), user_sex=str(), user_height=int(), user_weight=float(),
                 user_age=int())
    await state.set_state(REG.height)
    await bot.send_message(message.chat.id, text = 'Введи свой рост в сантиметрах:')

@dp.message(REG.height)
async def height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(REG.age)
    await message.answer('Введи свой возраст:')
@dp.message(REG.age)
async def age(message:Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(REG.sex)
    await message.answer('Выбери свой пол:', reply_markup=kb.sex)


@dp.message(REG.sex)
async def sex(message:Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(REG.want)
    await message.answer('Выбери, как хочешь измениться', reply_markup=kb.want)


@dp.message(REG.want)
async def want(message:Message, state: FSMContext):
    await state.update_data(want=message.text)
    await state.set_state(REG.weight)
    await message.answer('Введи свой вес в килограммах', reply_markup=types.ReplyKeyboardRemove())


@dp.message(REG.weight)
async def wei(message:Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    height, sex, age, weight, aim = data['height'], data['sex'], data['age'], data['weight'], data['want']
    if "," in weight:
        we1 = message.text.split(",")
        weight = int(we1[0]) + int(we1[1]) / 10 ** len(we1[1])
    else:
        weight = float(message.text)
    height, sex, age = int(height), str(sex), int(age)
    imt = round(weight / ((height / 100) ** 2), 3)
    imt_using_words = str()
    if round(imt) < 15:
        imt_using_words = 'сильно меньше нормы'
    if round(imt) in range(14, 18):
        imt_using_words = 'Недостаточная масса '
    if round(imt) in range(18, 25):
        imt_using_words = 'Норма'
    if round(imt) in range(25, 30):
        imt_using_words = 'Предожирение'
    if round(imt) > 30:
        imt_using_words = 'Ожирение'
    cal = 0
    if sex == 'Мужчина':
        cal = (10 * weight) + (6.25 * height) - (5 * age) + 5
    if sex == 'Женщина':
        cal = (10 * weight) + (6.25 * height) - (5 * age) - 161
    cursor.execute(f"UPDATE users SET user_weight = ?, imt = ?, imt_str = ?, cal = ?, user_sex = ?, user_age = ?, user_height = ?, user_aim = ?WHERE user_id = ? AND date = ?",
                   (weight, imt, imt_using_words, cal, sex, age, height, aim, message.from_user.id,
                    datetime.datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    await state.set_state(REG.ais)
    await bot.send_message(message.chat.id,
                     text='{}, твой вес: {}, твой рост: {}, твой индекс массы тела:{}, и твой вес - это {}. '.format(
                         message.from_user.first_name, weight, height, imt, imt_using_words))
    await state.clear()
@dp.message(REG.ais)
async def ai(message: Message, state: FSMContext):
    await state.update_data(ais=message.text)

    cursor.execute(
        "SELECT user_aim, cal ,user_sex, user_age, imt, user_weight, user_height FROM users WHERE date = ? AND user_id = ?",
        (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id))
    aim, cal, sex, age, imt, weight, height = cursor.fetchone()
    if aim == 'Сброс веса':
        await message.answer(
            'Ваши Б/Ж/У должны быть в соотношении 35/15/50, и в день вы должны потреблять {} килокалорий'.format(
                             cal - cal / 5))
    if aim == 'Удержание массы':
        await message.answer('Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(
                             cal))
    if aim == 'Набор массы':
        await message.answer('Ваши Б/Ж/У должны быть в соотношении 30/20-25/50-55, и в день вы должны потреблять {} килокалорий'.format(
                             cal + 450))
    await message.answer('Для того, чтобы тебе осуществить {}, тебе стоит наладить твоё питание и тренировки.  Бот PROпиташка тебе с этим поможет)) Сейчас сюда придут сообщения с твоими недельными планами тренировок и питания,которые ты так-же сможешь найти в закреплённых сообщениях'.format(
                         aim))
    with GigaChat(
            credentials=os.getenv('GIGA'),
            verify_ssl_certs=False) as giga:
        global plan_train, plan_pit
        plan_pit = giga.chat(
            f"Придумай индивидуальный план разнообразного питания на неделю для {sex},чей рост равен {height}, возраст равен {age}, имт равен {imt} и цель {aim}")
        plan_train = giga.chat(
            f"Придумай индивидуальный план тренировок на неделю для {sex}, чей рост равен {height}, возраст равен {age},  чей имт равен {imt} , чья цель {aim} и чей индивидуальный план питания {plan_pit.choices[0].message.content}")
        await bot.send_message(message.chat.id, text=plan_pit.choices[0].message.content,
                                        reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.chat.id, text=plan_train.choices[0].message.content,
                                          reply_markup=types.ReplyKeyboardRemove())


    await bot.send_message(message.chat.id,
                           text='Выданные планы питания и тренировок являются лишь рекоменданиями, которые ты можешь выполнять по желанию. Теперь ты можешь вводить продукты, которые ты сегодня употребил и тренировки, которые ты сегодня прошёл, а в конце дня ты будешь получать отчёт по твоим Б/Ж/У за день и затраченным калориям')




async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
