from telebot import TeleBot
import json

bot = TeleBot("8073615695:AAHvd85d4P7xOl6hezoQ93n-XuYoW5WuuXI")

users = {}
try:
    with open("users.json","r") as file:
        users = json.load(file)
except:
    users = {}

@bot.message_handler(commands=["start"])
def start(message):
    users[message.from_user.id] = []
    with open("users.json",'w') as file:
        json.dump(users,file)


@bot.message_handler(commands=["simple"])
def add_task(message):
    bot.send_message(message.chat.id,f"hello {message.from_user.first_name}")
    with open("my_image.webp",'rb') as file:
        bot.send_photo(message.chat.id,file)

@bot.message_handler(commands=['add_task'])
def add_task(message):
    try:
        if message.from_user.id not in users:
            users[message.from_user.id] = []
        text = ' '.join(message.text.split(' ')[1:])

        if len(text.strip().replace(' ',''))!=0 :
            users[message.from_user.id].append(text)
        else:
            bot.reply_to(message,'неверное название задачи')
            return

        with open("users.json",'w') as file:
            json.dump(users,file)
        bot.send_message(message.chat.id,'задача сохранена')
    except:
        bot.reply_to(message,"задача не была сохранена, обратитесь в тех поддержку")


@bot.message_handler(commands=['get_tasks'])
def get_tasks(message):
    try:
        with open("users.json",'w') as file:
            json.dump(users,file)
            bot.send_message(message.chat.id,'\n'.join(users[message.from_user.id]))
    except:
        bot.reply_to(message,"у вас ещё нет никаких задач")


bot.polling()