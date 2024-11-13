import sqlite3

from aiogram.filters import CommandStart
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
import aiosqlite
import base64
from dotenv import load_dotenv
import os
import keyboards as kb
import asyncio
import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from gigachat import GigaChat
from aiogram.filters import Command



load_dotenv()
TOKEN = os.getenv('TOKEN')

def decode_credentials(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str)
    decoded_str = decoded_bytes.decode('utf-8')
    client_id, client_secret = decoded_str.split(':')
    return client_id, client_secret


encoded_credentials = os.getenv('GIGA')
client_id, client_secret = decode_credentials(encoded_credentials)
GIGA = {
    'client_id': client_id,
    'client_secret': client_secret
}



credentials_str = f"{GIGA['client_id']}:{GIGA['client_secret']}"
credentials_base64 = base64.b64encode(credentials_str.encode("utf-8")).decode("utf-8")

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


conn = sqlite3.connect('pro3.db', check_same_thread=False)
cursor = conn.cursor()


class REG(StatesGroup):
    height = State()
    age = State()
    sex = State()
    want = State()
    weight = State()
    ais = State()


async def db_table_val(user_id: int, user_age: int, user_sex: str, user_weight: float, date: str, user_aim: str,
                       imt: float, imt_str: str, cal: float, user_height: int):
    async with aiosqlite.connect('pro3.db') as conn:
        await conn.execute(
            'INSERT INTO users (user_id, user_age, user_sex, user_weight, date, user_aim, imt, imt_str, cal, user_height) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, user_age, user_sex, user_weight, date, user_aim, imt, imt_str, cal, user_height)
        )
        await conn.commit()


async def get_user_data(user_id: int, date: str):
    async with aiosqlite.connect('pro3.db') as conn:
        cursor = await conn.execute(
            "SELECT user_age, user_height, user_sex, user_weight, user_aim, imt, imt_str, cal FROM users WHERE user_id = ? AND date = ?",
            (user_id, date)
        )
        return await cursor.fetchone()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        FSInputFile(path='new_logo.jpg'),
        caption=f'Привет, {message.from_user.first_name}! Бот PROпиташка поможет тебе вести индивидуальный расчет твоего питания и активности.',
        reply_markup=kb.startMenu
    )


@dp.message(F.text == "Вход")
async def entrance(message: Message, state: FSMContext):
    user_data = await get_user_data(message.from_user.id, datetime.datetime.now().strftime('%Y-%m-%d'))
    if user_data:
        height, weight, imt, imt_using_words = user_data[1], user_data[3], user_data[5], user_data[6]
        await state.set_state(REG.ais)
        await bot.send_message(
            message.chat.id,
            text=f'{message.from_user.first_name}, твой вес: {weight}, твой рост: {height}, твой ИМТ: {imt}, и твой вес - это {imt_using_words}.'
        )
        plan_pit, plan_train = await generate_nutrition_plan(message, bot)
        await state.set_state(REG.ais)

        try:
            if plan_pit and plan_train:
                # Разделяем длинные сообщения на части
                for part in split_message(plan_pit):
                    await bot.send_message(message.chat.id, text=part)
                for part in split_message(plan_train):
                    await bot.send_message(message.chat.id, text=part)
                await message.answer(
                    text='Выданные планы питания и тренировок являются лишь рекоменданиями, которые ты можешь выполнять по желанию. ',
                    reply_markup=kb.entranse)

            else:
                await bot.send_message(message.chat.id, text="Не удалось получить данные пользователя.")
        except Exception as e:
            print(f"Ошибка при генерации плана: {str(e)}")
            return f"Ошибка при генерации плана: {e}"
    else:
        await bot.send_message(message.chat.id, text='Твоих данных в базе нет 🙁 Для начала пройди регистрацию', reply_markup=kb.reRig)


@dp.message(F.text == 'Регистрация')
async def registration(message: Message, state: FSMContext):
    await db_table_val(
        user_id=message.from_user.id,
        date=datetime.datetime.now().strftime('%Y-%m-%d'),
        user_aim="",
        imt=0.0,
        imt_str="",
        cal=0.0,
        user_sex="",
        user_height=0,
        user_weight=0.0,
        user_age=0
    )
    await state.set_state(REG.height)
    await bot.send_message(message.chat.id, text='Введи свой рост в сантиметрах:')


@dp.message(REG.height)
async def height(message: Message, state: FSMContext):
    await state.update_data(height=int(message.text))
    await state.set_state(REG.age)
    await message.answer('Введи свой возраст:')

@dp.message(REG.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await state.set_state(REG.sex)
    await message.answer('Выбери свой пол:', reply_markup=kb.sex)

@dp.message(REG.sex)
async def sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(REG.want)
    await message.answer('Выбери, как хочешь измениться', reply_markup=kb.want)

@dp.message(REG.want)
async def want(message: Message, state: FSMContext):
    await state.update_data(want=message.text)
    await state.set_state(REG.weight)
    await message.answer('Введи свой вес в килограммах', reply_markup=types.ReplyKeyboardRemove())

@dp.message(REG.weight)
async def wei(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    height, sex, age, weight, aim = data['height'], data['sex'], data['age'], data['weight'], data['want']
    await state.set_state(REG.ais)


    if "," in weight:
        we1 = message.text.split(",")
        weight = int(we1[0]) + int(we1[1]) / 10 ** len(we1[1])
    else:
        weight = float(message.text)


    height, sex, age = int(height), str(sex), int(age)
    imt = round(weight / ((height / 100) ** 2), 3)
    imt_using_words = calculate_imt_description(imt)
    cal = calculate_calories(sex, weight, height, age)


    cursor.execute(
        f"UPDATE users SET user_weight = ?, imt = ?, imt_str = ?, cal = ?, user_sex = ?, user_age = ?, user_height = ?, user_aim = ? WHERE user_id = ? AND date = ?",
        (weight, imt, imt_using_words, cal, sex, age, height, aim, message.from_user.id, datetime.datetime.now().strftime('%Y-%m-%d'))
    )
    conn.commit()
    await state.set_state(REG.ais)

    try:
        await bot.send_message(
            message.chat.id,
            text=f'{message.from_user.first_name}, твой вес: {weight}, твой рост: {height}, твой индекс массы тела: {imt}, и твой вес - это {imt_using_words}.'
        )
        plan_pit, plan_train = await generate_nutrition_plan(message, bot)
        if plan_pit and plan_train:
            # Разделяем длинные сообщения на части
            for part in split_message(plan_pit):
                await bot.send_message(message.chat.id, text=part)
            for part in split_message(plan_train):
                await bot.send_message(message.chat.id, text=part)
            await message.answer(
                text='Выданные планы питания и тренировок являются лишь рекоменданиями, которые ты можешь выполнять по желанию. ',
                reply_markup=kb.entranse)

        else:
            await bot.send_message(message.chat.id, text="Не удалось получить данные пользователя.")
    except Exception as e:
        print(f"Ошибка при генерации плана: {str(e)}")
        return f"Ошибка при генерации плана: {e}"


def calculate_imt_description(imt):
    if round(imt) < 15:
        return 'сильно меньше нормы'
    elif round(imt) in range(14, 18):
        return 'Недостаточная масса'
    elif round(imt) in range(18, 25):
        return 'Норма'
    elif round(imt) in range(25, 30):
        return 'Предожирение'
    else:
        return 'Ожирение'

def calculate_calories(sex, weight, height, age):
    if sex == 'Мужчина':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif sex == 'Женщина':
        return (10 * weight) + (6.25 * height) - (5 * age) - 161
    return 0

def split_message(text, max_length=4096):
    """Разделяем текст на части не более max_length символов."""
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]




async def generate_nutrition_plan(message, bot):
    try:
        cursor.execute(
            "SELECT user_aim, cal, user_sex, user_age, imt, user_weight, user_height FROM users WHERE date = ? AND user_id = ?",
            (datetime.datetime.now().strftime('%Y-%m-%d'), message.from_user.id)
        )
        aim, cal, sex, age, imt, weight, height = cursor.fetchone()
        async with GigaChat(
            credentials='YzY3ZWQ3MmMtN2ZlOC00ZGQzLWE5OGEtOTBjMjdlMGZjMDJiOjQ4NTI4MDM1LTliNjgtNGIwOS1hZjk3LTFkNjU1MDk2NDM4Ng==',
            verify_ssl_certs=False) as giga:
              global plan_train, plan_pit
              plan_pit= giga.chat(
        f"Придумай индивидуальный план разнообразного питания на неделю для {sex},чей рост равен {height}, возраст равен {age}, имт равен {imt} и цель {aim}")
              plan_train = giga.chat(
           f"Придумай индивидуальный план тренировок на неделю для {sex}, чей рост равен {height}, возраст равен {age},  чей имт равен {imt} , чья цель {aim} и чей индивидуальный план питания {plan_pit.choices[0].message.content}")


              return plan_pit.choices[0].message.content, plan_train.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при генерации плана: {str(e)}")
        return f"Ошибка при генерации плана: {e}"

@dp.message(F.text == 'Вход в програму')
async def ais(message: Message, state: FSMContext):
    await message.answer( text='Теперь ты можешь вводить продукты, которые ты сегодня употребил и тренировки, которые ты сегодня прошёл, а в конце дня ты будешь получать отчёт по твоим Б/Ж/У за день и затраченным калориям',reply_markup=kb.main_menu
)

async def main():

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
