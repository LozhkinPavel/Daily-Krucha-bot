import schedule
import time
import telebot
import redis
from threading import Thread

bot = telebot.TeleBot(TOKEN)

r = redis.Redis(host='redis', port=6379)
def register_new_photo(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = '/data/Pictures/icon' + str(r.scard('photos') + 1)
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        r.sadd('photos', src)
        bot.reply_to(message, "Фото добавлено")
    except Exception as e:
        bot.reply_to(message, 'Братан, ты чет не то сделал')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Вас приветствует бот <b>Daily Krucha</b>.\n'
                                      'Напишите команду \help, чтобы увидеть функционал бота.', parse_mode='html')


@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, 'В боте присутствуют следующие команды: \n\\start - получить приветственное сообщение'
                                      ' \n\\subscribe - подписаться на ежедневную рассылку фотографий \n'
                                      '\\unsubscribe - отписаться от рассылки \n\\get - получить одну случайную фотографию \n'
                                      '\\add - добавить новую фотографию в базу')


@bot.message_handler(commands=['get'])
def get(message):
    try:
        photo = open(r.srandmember('photos'), 'rb')
        bot.send_photo(message.chat.id, photo)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так')

@bot.message_handler(commands=['add'])
def add(message):
    try:
        msg = bot.send_message(message.chat.id, 'Отправьте мне фотографию Кручи чтобы добавить ее в базу. Пожалуйста не присылайте никакие другие картинки.')
        bot.register_next_step_handler(msg, register_new_photo)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так')


@bot.message_handler(commands=['subscribe'])
def sub(message):
    try:
        if r.exists('subscribers', str(message.chat.id)):
            bot.send_message(message.chat.id, 'Вы уже подписаны на ежедневного Кручу')
            return
        r.sadd('subscribers', str(message.chat.id))
        bot.send_message(message.chat.id, 'Вы были подписаны на ежедневного Кручу')
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так')


@bot.message_handler(commands=['unsubscribe'])
def unsub(message):
    try:
        if not r.exists('subscribers', str(message.chat.id)):
            bot.send_message(message.chat.id, 'Вы не подписаны на ежедневного Кручу')
            return
        r.srem('subscribers', str(message.chat.id))
        bot.send_message(message.chat.id, 'Вы были отписаны от ежедневного Кручи')
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так')


def send_photo_to_subs():
    for sub in r.smembers('subscribers'):
        try:
            photo = open(r.srandmember('photos'), 'rb')
            bot.send_photo(int(sub), photo)
        except Exception as e:
            bot.send_message(int(sub), 'Не получилось отправить ежедневного Кручу')


def loop():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule.every(24).hours.at("00:00").do(send_photo_to_subs)
    p1 = Thread(target=loop)
    p1.start()
    bot.polling()
