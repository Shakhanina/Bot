import telebot
import datetime
import threading
import random
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
from telebot.types import Message
import telebot, wikipedia, re

bot = telebot.TeleBot("6045443280:AAFb5E1_CE1Rb_PMSrAaUrUYrc1_qoBz0Ic")
wikipedia.set_lang("ru")


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Я бот-напоминалка. Чтобы создать напоминание, введите /reminder.\n'
                                      'Чтобы начать мини  диалог нажмите /say_standup_speech \n'
                                      'Cовет дня /advice \n'
                                      'Факты /fact \n'
                                      'Cоветы дня /advice \n'
                                      'Найти в Wikipedia /find \n'
                                      'Угадай число /play\n'
                                      'Стоп /stop')


@bot.message_handler(commands=['reminder'])
def reminder_message(message):
    bot.send_message(message.chat.id, 'Введите название напоминания:')
    bot.register_next_step_handler(message, set_reminder_name)


def handle_standup_speech(message):
    bot.reply_to(message, "Спасибо большое! Желаю успехов и хорошего дня!")


@bot.message_handler(commands=["say_standup_speech"])
def say_standup_speech(message: Message):
    bot.reply_to(message, text="Привет! Чем ты занимался вчера?"
                               "Что будешь делать сегодня?"
                               "Какие есть трудности?")
    bot.register_next_step_handler(message, handle_standup_speech)


@bot.message_handler(commands=['advice'])
def covet(message: Message):
    f = open('covet.txt', 'r', encoding='UTF-8')
    covet_dna = f.read().split('/')
    answer = random.choice(covet_dna)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['fact'])
def fact_fync(message: Message):
    f = open('fact.txt', 'r', encoding='UTF-8')
    fact_dna = f.read().split('/')
    answer = random.choice(fact_dna)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['play'])
def newgame(message):
    # message.text
    global HiddenNumber
    global UserNumber
    HiddenNumber = random.randint(1, 100)
    print(message.text)
    print(HiddenNumber)
    text = message.text
    msg = bot.send_message(message.chat.id, 'Введи число от 1 до 100:')
    bot.register_next_step_handler(msg, GuessNumber)


def GuessNumber(message):
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(message.chat.id, 'Вводить нужно число!')
        bot.register_next_step_handler(msg, GuessNumber)
        return

    if text != HiddenNumber:
        print(message.text)
        UserNumber = int(message.text)
        if UserNumber > HiddenNumber:
            msg = bot.send_message(message.chat.id, 'Число должно быть меньше!')
            bot.register_next_step_handler(msg, GuessNumber)
        elif UserNumber < HiddenNumber:
            msg = bot.send_message(message.chat.id, 'Число должно быть больше!')
            bot.register_next_step_handler(msg, GuessNumber)
        else:
            bot.send_message(message.chat.id, 'Ты угадал, это число: ' + str(HiddenNumber))


@bot.message_handler(commands=['stop'])
def bye(message):
    bot.send_message(message.chat.id, text="Досвидания!\n"
                                           " ^ ^             \n"
                                           "( . .)  < Чмок!!> \n"
                                           "<( )>            \n"
                                           "  ! !")

def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not('==' in x):
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break

        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Отправьте мне любое слово, и я найду его значение на Wikipedia')


@bot.message_handler(commands=["find"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Отправьте мне любое слово, и я найду его значение на Wikipedia')


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, getwiki(message.text))


def set_reminder_name(message):
    user_data = {}
    user_data[message.chat.id] = {'reminder_name': message.text}
    bot.send_message(message.chat.id,
                     'Введите дату и время, когда вы хотите получить напоминание в формате ГГГГ-ММ-ДД чч:мм:сс.')
    bot.register_next_step_handler(message, reminder_set, user_data)


def reminder_set(message, user_data):
    try:
        reminder_time = datetime.datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        delta = reminder_time - now
        if delta.total_seconds() <= 0:
            bot.send_message(message.chat.id, 'Вы ввели прошедшую дату, попробуйте еще раз.')
        else:
            reminder_name = user_data[message.chat.id]['reminder_name']
            bot.send_message(message.chat.id,
                             'Напоминание "{}" установлено на {}.'.format(reminder_name, reminder_time))
            reminder_timer = threading.Timer(delta.total_seconds(), send_reminder, [message.chat.id, reminder_name])
            reminder_timer.start()
    except ValueError:
        bot.send_message(message.chat.id, 'Вы ввели неверный формат даты и времени, попробуйте еще раз.')


def send_reminder(chat_id, reminder_name):
    bot.send_message(chat_id, 'Напоминание "{}"!'.format(reminder_name))


@bot.message_handler(func=lambda message: True)
def handle_all_message(message):
    bot.send_message(message.chat.id, 'Я не понимаю, что вы говорите. Чтобы создать напоминание, введите /reminder.')


if __name__ == '__main__':
    bot.polling(none_stop=True)
