from Gemini import AsyncChatbot
from aiogram import Bot, types
from aiogram.dispatcher import dispatcher
from aiogram.utils import executor


secure_1PSID = 'g.a000nwizOO2TDmpyJqCPwhvbNGvwFY_iCf6Qerqt-PwlFjJLIo3cJTSUs5cmZB2TDtZmKSDsqwACgYKAWcSARUSFQHGX2Mi-g1VJ7JXjGnZzl8hijh4fhoVAUF8yKrDcz1gErLgkd1qW_Orla6w0076'
secure_1PSIDTS = 'sidts-CjIBUFGohwFSm3uP-7IfPrL7mWHfKGY4D5tJjgQvwI0ENWvTidS3pHOE6flU5f0b45JcIhAA'
telegram_token = '7422598373:AAGg3ZjZqx4tLkDwipqMxg9ejX050xl5m1E'

bot = Bot(token=telegram_token)
dp = dispatcher(bot)


@dp.message_handler()
async def send(message: types.Message):
    try:
        chatbot = await AsyncChatbot.create(secure_1PSID, secure_1PSIDTS) 
        await message.answer('Google Bard начинает думать...')
        await message.answer_chat_action('typing')
        answer = await chatbot.ask(message.text)
        await message.answer(answer.get('content'), parse_mode="markdown")
    except Exception as ex:
        await message.answer(str(ex))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)