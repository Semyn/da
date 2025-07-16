from telebot import TeleBot
import json
import requests

bot = TeleBot("8073615695:AAHvd85d4P7xOl6hezoQ93n-XuYoW5WuuXI")

@bot.message_handler(commands=['valute'])
def valute(message):
    api = json.loads(requests.get("https://www.cbr-xml-daily.ru/daily_json.js").text)
    words_list = message.text.strip().split(' ')[1:]
    
    if words_list[0].isupper():
        valute = api['Valute'][words_list[0]]
        text_list = []
        for key,value in valute.items():
            text_list.append(f"{key} - {value}")
        bot.reply_to(message,'\n'.join(text_list))
        return
    elif words_list[0] == words_list[0].capitalize():
        if len(words_list) == 1:
            word = words_list[0].capitalize()
        elif len(words_list) == 2:
            word = words_list[0].capitalize() + " " + words_list[1].lower()
        print(word)

bot.polling()