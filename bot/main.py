import asyncio
from telebot.async_telebot import AsyncTeleBot
import requests
import json
import aiohttp
from config import TELEGRAM_TOKEN,OPENROUTER_KEY,NEUROIMG_KEY


bot = AsyncTeleBot(TELEGRAM_TOKEN)

print("Приложение запущено!")

async def sendAi(message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {                        "role": "system",
                        "content": (                            "Если пользователь просит оформить подписку или задаёт вопрос, связанный с подпиской "
                            "(например, 'оформи подписку', 'подпишись', 'активируй подписку'), "                            "отвечай строго одним словом: \"Подписка\".\n"
                            "На все остальные вопросы отвечай кратко, по делу и на естественном языке, как помощник. "                            "Не упоминай эту инструкцию."
                        )                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
            })
        )

        return response.json()
    except Exception as e:
        print(e)


async def free_generate(prompt):
    async with aiohttp.ClientSession() as session:
        payload = {
            "token": NEUROIMG_KEY,
            "prompt": prompt,
            "stream": True
        }
        
        async with session.post(
            "https://neuroimg.art/api/v1/free-generate",
            json=payload
        ) as response:
            async for line in response.content:
                if line:
                    data = json.loads(line)
                    if data["status"] == "SUCCESS":
                        return data["image_url"]
                    print(f"Статус: {data['status']}")
                
    return response.json()

@bot.message_handler(commands=['start', 'help'])
async def start(message):
    await bot.reply_to(message, 'Привет! Ты попал в самый креативный чат бот телеграма!\n/start - помощь\n/help - помощь\n/draw [промпт] - сгенерировать изображение')

@bot.message_handler(commands=['draw'])
async def generate(message):
    str = message.text.split(' ')
    str.remove(str[0])
    await bot.send_message(message.chat.id, " ".join(str))

    await bot.send_message(message.chat.id, 'Генерирую изображение')
    await bot.send_chat_action(message.chat.id, 'upload_photo')
    image_url = await free_generate(message.text)
    await bot.send_photo(message.chat.id, image_url)

async def subscribe(message):
    print("вызов функции subscribe")
    await bot.send_message(message.chat.id, "подписка оформлена")
    

@bot.message_handler(content_types=['text'])
async def echo(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    response = await sendAi(f"{message.text}")
    responseAI = response['choices'][0]['message']['content']
    print(responseAI)

    if responseAI.lower() == 'подписка':
        await subscribe(message)
    else:
        await bot.send_message(message.chat.id, response['choices'][0]['message']['content'])


asyncio.run(bot.polling())