import asyncio
from telebot.async_telebot import AsyncTeleBot
import requests
import json
from collections import defaultdict
import aiohttp

TELEGRAM_TOKEN = "7823426557:AAGpWbX8pNhR2_yPKGW8vKdksVKOLNXrmSw"
OPENROUTER_KEY = "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"
OPENROUTER_MODEL = "moonshotai/kimi-k2:free"
IMAGE_API_URL = "https://api.openrouter.ai/v1/images/generations"  # URL для генерации изображений

bot = AsyncTeleBot(TELEGRAM_TOKEN)

# Хранилище для истории сообщений каждого пользователя
user_message_history = defaultdict(list)
MAX_HISTORY_LENGTH = 10

print("Бот запущен и готов к работе!")

async def get_ai_response(user_id, message_text):
    """Получение ответа от нейросети с учетом истории сообщений"""
    try:
        history = user_message_history.get(user_id, [])
        history.append({"role": "user", "content": message_text})
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps({
                "model": OPENROUTER_MODEL,
                "messages": history,
            })
        )
        response.raise_for_status()
        response_data = response.json()
        
        if 'choices' in response_data and response_data['choices']:
            assistant_message = response_data['choices'][0]['message']
            history.append(assistant_message)
            
            if len(history) > MAX_HISTORY_LENGTH:
                history = history[-MAX_HISTORY_LENGTH:]
            
            user_message_history[user_id] = history
            
            return assistant_message['content']
        
        return "Не удалось получить ответ от нейросети"
    except Exception as e:
        print(f"Ошибка при запросе к нейросети: {e}")
        return "Произошла ошибка при обработке вашего запроса"

async def generate_image(prompt):
    """Генерация изображения по промпту"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "stability-ai/sdxl",  # Модель для генерации изображений
            "prompt": prompt,
            "n": 1,  # Количество изображений
            "size": "1024x1024"  # Размер изображения
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                IMAGE_API_URL,
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data'][0]['url']  # URL сгенерированного изображения
                else:
                    error = await response.text()
                    print(f"Ошибка генерации изображения: {error}")
                    return None
    except Exception as e:
        print(f"Ошибка в generate_image: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    """Обработка команд /start и /help"""
    welcome_text = (
        "🤖 Привет! Я умный бот с нейросетью и памятью.\n\n"
        "Я могу:\n"
        "- Вести осмысленный диалог\n"
        "- Запоминать контекст разговора\n"
        "- Генерировать изображения по запросу\n\n"
        "Просто напиши мне что-нибудь, и я отвечу!\n"
        "Команды:\n"
        "/draw [описание] - сгенерировать изображение\n"
        "/clear - очистить историю сообщений\n"
        "/model - узнать текущую модель нейросети"
    )
    await bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['clear'])
async def clear_history(message):
    """Очистка истории сообщений"""
    user_id = message.from_user.id
    user_message_history[user_id] = []
    await bot.reply_to(message, "🗑️ История сообщений очищена. Я всё забыл!")

@bot.message_handler(commands=['model'])
async def show_model(message):
    """Показ используемой модели нейросети"""
    await bot.reply_to(message, f"🛠️ Текущая модель нейросети: {OPENROUTER_MODEL}")

@bot.message_handler(commands=['draw'])
async def draw_image(message):
    """Генерация изображения по команде /draw"""
    try:
        # Извлекаем промпт из сообщения
        prompt = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
        
        if not prompt:
            await bot.reply_to(message, "Пожалуйста, укажите описание изображения после команды /draw")
            return
        
        await bot.send_chat_action(message.chat.id, 'upload_photo')
        await bot.reply_to(message, f"🖌️ Генерирую изображение по запросу: {prompt}")
        
        # Генерируем изображение
        image_url = await generate_image(prompt)
        
        if image_url:
            await bot.send_photo(message.chat.id, image_url)
        else:
            await bot.reply_to(message, "⚠️ Не удалось сгенерировать изображение. Попробуйте другой запрос.")
    except Exception as e:
        print(f"Ошибка в draw_image: {e}")
        await bot.reply_to(message, "⚠️ Произошла ошибка при генерации изображения")

@bot.message_handler(content_types=['text'])
async def handle_text(message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    await bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response_text = await get_ai_response(user_id, message.text)
        await bot.reply_to(message, response_text)
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        await bot.reply_to(message, "⚠️ Произошла ошибка при обработке вашего сообщения")

if __name__ == '__main__':
    print("Бот запускается...")
    asyncio.run(bot.polling())