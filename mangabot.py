from telebot import *
from manga import get_manga_from_vol_num

bot = telebot.TeleBot('')

@bot.message_handler(commands=["start", "help"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Пришлите ссылку на главную страницу манги с readmanga.io. Дополнительно можно указать том и главу манги')

@bot.message_handler(regexp=r'https://readmanga.io/')
def get_manga(message):
    # try:
    data = message.text.split()
    # except Exception:
    #     bot.send_message(message.chat.id, 'Недостаточно данных')
    #     return  

    manga_list = get_manga_from_vol_num(len(data), *data)

    if not manga_list:
        bot.send_message(message.chat.id, 'Несуществующий номер манги')
        return 

    for manga in manga_list:
        bot.send_document(message.chat.id, document=open(manga, 'rb'))


bot.polling(none_stop=True, interval=0)
