from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

startMenu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text = 'Вход'),
            KeyboardButton(text='Регистрация'),

        ]

    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Вход или Регистрация'
)
reRig = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Регистрация'),

        ]

    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Регистрация'
)
sex = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Мужчина'),
            KeyboardButton(text='Женщина'),

        ]

    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выбор пола:'
)
want = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Сброс веса'),
            KeyboardButton(text='Удержание массы'),
            KeyboardButton(text='Набор веса'),

        ]

    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выбор веса:'
)
main_menu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Добавить тренировки'),
            KeyboardButton(text='Ввести еду за день'),
            KeyboardButton(text='Сводка'),
            KeyboardButton(text='Помочь с рецептом'),
            KeyboardButton(text='Помочь с тренировкой'),
            KeyboardButton(text='Добавить выпитый стаканчик воды'),
            KeyboardButton(text='Присоедениться к чату'),

        ]

    ],
    resize_keyboard=False,
    one_time_keyboard=True,
    input_field_placeholder='Выбор веса:'
)