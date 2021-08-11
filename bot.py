import config
import sqlite3
import telebot
from telebot.types import InputMediaAudio
from telebot import types
import markups
from array import *

bot = telebot.TeleBot(config.token)

conn = sqlite3.connect('db.db', check_same_thread=False)
cursor = conn.cursor()
bot = telebot.TeleBot(config.token)

kat = "test"
genre = "test"


sqlkat = 'SELECT file_id FROM audio WHERE "kat"=? LIMIT ?, 10'

sqlgenre = 'SELECT file_id FROM audio WHERE "genre"=? LIMIT 10'


def db_table_val(file_id: str, file_name: str, kat: str, genre: str):
	cursor.execute('INSERT INTO audio (file_id, file_name, kat, genre) VALUES (?, ?, ?, ?)', (file_id, file_name, kat, genre))
	conn.commit()

@bot.message_handler(content_types=["audio"])
def handle_files(message):
	document_name = message.audio.file_name
	document_id = message.audio.file_id
	db_table_val(file_id=document_id, file_name=document_name, kat=kat, genre=genre)
	bot.send_message(message.chat.id, "Книга успешно добавлена")
	#bot.send_message(message.chat.id, "Имя: " + document_name + document_id) # Отправляем пользователю file_id

@bot.message_handler(commands=['start', 'home'])
def get_text_messages(message):
	bot.send_message(message.chat.id, "Привет, я ищу аудиокниги по нашей обширной библиотеке Чтобы начать воспользуйся меню навигации.", reply_markup = markups.startmenu_markup)

@bot.message_handler(commands=['help'])
def get_text_messages(message):
	bot.reply_to(message, "Список команд: /menu - Открывает меню навигации")

@bot.message_handler(commands=['menu'])
def get_text_messages(message):
	bot.send_message(message.chat.id, "Выберите категорию", reply_markup = markups.menu_markup)

@bot.message_handler(commands=['add'])
def get_text_messages(message):
	global mci
	mci = message.chat.id
	if mci == -1001527235017:
		bot.send_message(message.chat.id, "Выберите категорию аудиокниг", reply_markup = markups.kategory_markup)
		bot.register_next_step_handler(message, addkat)
def addkat(message):
	global kat
	kat = message.text
	bot.send_message(message.chat.id, "Категория выбрана")
	bot.send_message(message.chat.id, "Выберите жанр аудиокниг", reply_markup = markups.genre_markup)
	bot.register_next_step_handler(message, addgenre)
def addgenre(message):
	global genre
	genre = message.text
	bot.send_message(message.chat.id, "Жанр выбран")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	if call.message:

		data = []
		kat = call.data.split('|')[0]
		numstr = int(call.data.split('|')[1])
		direction = call.data.split('|')[2]

		skip = numstr*10

		if direction == "назад":
			numstr = numstr-1

			param = str(kat) + '|' + str(numstr)

			for value in cursor.execute(sqlkat, (kat,skip,)):
				separator=""
				dats = separator.join(value)
				data.append(InputMediaAudio(dats))
			bot.send_media_group(call.message.chat.id, data)

			dm = len(cursor.execute('SELECT file_id FROM audio WHERE "kat"=?', (kat,)).fetchall())
			print(dm)

			if( numstr == 1 ):
				nav = types.InlineKeyboardMarkup(row_width=2)
				button2 = types.InlineKeyboardButton(numstr, callback_data=param+'|страница')
				button3 = types.InlineKeyboardButton("Вперед", callback_data=param+'|вперед')
				nav.add(button2,button3)
			else:
				nav = types.InlineKeyboardMarkup(row_width=3)
				button1 = types.InlineKeyboardButton("Назад", callback_data=param+'|назад')
				button2 = types.InlineKeyboardButton(numstr, callback_data=param+'|страница')
				button3 = types.InlineKeyboardButton("Вперед", callback_data=param+'|вперед')
				nav.add(button1,button2,button3)

			bot.send_message(call.message.chat.id, "Аудиокниги по запросу "+kat, reply_markup = nav)

		if direction == "вперед":
			numstr = numstr+1

			param = str(kat) + '|' + str(numstr)

			for value in cursor.execute(sqlkat, (kat,skip,)):
				separator=""
				dats = separator.join(value)
				data.append(InputMediaAudio(dats))
			bot.send_media_group(call.message.chat.id, data)

			dm = len(cursor.execute('SELECT file_id FROM audio WHERE "kat"=?', (kat,)).fetchall())

			if( dm > (numstr*10) ):
				nav = types.InlineKeyboardMarkup(row_width=3)
				button1 = types.InlineKeyboardButton("Назад", callback_data=param+'|назад')
				button2 = types.InlineKeyboardButton(numstr, callback_data=param+'|страница')
				button3 = types.InlineKeyboardButton("Вперед", callback_data=param+'|вперед')
				nav.add(button1,button2,button3)
			else:
				nav = types.InlineKeyboardMarkup(row_width=2)
				button1 = types.InlineKeyboardButton("Назад", callback_data=param+'|назад')
				button2 = types.InlineKeyboardButton(numstr, callback_data=param+'|страница')
				nav.add(button1,button2)


			bot.send_message(call.message.chat.id, "Аудиокниги по запросу "+kat, reply_markup = nav)

@bot.message_handler(content_types = ['text'])
def send_audio(message):

	data = []
	if message.text == "Каталог📕":
		bot.send_message(message.chat.id, "Выберите категорию", reply_markup = markups.kategory_markup)
	if message.text == "Жанры":
		bot.send_message(message.chat.id, "Выберите категорию", reply_markup = markups.genre_markup)
	if message.text == "Главное меню":
		bot.send_message(message.chat.id, "Возвращаемся в главное меню", reply_markup = markups.startmenu_markup)
	if message.text == "Назад":
		bot.send_message(message.chat.id, "Возвращаемся к выбору категории", reply_markup = markups.kategory_markup)


	#категории
	if message.text == "Бизнес литература" or message.text == "Аудиосказки" or message.text == "Аудиоспектакли" or message.text == "Русская классика" or message.text == "Зарубежная классика" or message.text == "Инвестиции" or message.text == "Иностранные языки" or message.text == "Личностный рост" or message.text == "Профессиональная литература" or message.text == "Современная зарубежная литература" or message.text == "Современная русская литература" or message.text == "Философия и психология" or message.text == "Школьная программа" or message.text == "Эротика":
		kat = message.text
		skip = 0
		numstr = 1
		for value in cursor.execute('SELECT file_id FROM audio WHERE "kat"=?', (kat,)).fetchall():
			separator=""
			dats = separator.join(value)
			data.append(InputMediaAudio(dats))

		bot.send_media_group(message.chat.id, data[:10])

		param = str(kat) + '|' + str(numstr)
		dm = len(cursor.execute('SELECT file_id FROM audio WHERE "kat"=?', (kat,)).fetchall())

		if( dm > (numstr*10) ):
			nav = types.InlineKeyboardMarkup(row_width=2)
			button2 = types.InlineKeyboardButton(numstr, callback_data="numst")
			button3 = types.InlineKeyboardButton("Вперед", callback_data=param+'|вперед')
			nav.add(button2,button3)
			bot.send_message(message.chat.id, "Найдено "+ str(dm)+" аудиокниг по запросу: "+kat, reply_markup = nav)
		else:
			bot.send_message(message.chat.id, "Найдено "+ str(dm)+" аудиокниг по запросу: "+kat)


	#жанры
	if message.text == "Детективы" or message.text == "История" or message.text == "Классика" or message.text == "Нон_фикшен" or message.text == "Поэзия" or message.text == "Подросткам" or message.text == "Политика" or message.text == "Романы" or message.text == "Триллер" or message.text == "Фантастика" or message.text == "Хорор" or message.text == "Художественные":
		genre = message.text
		bot.send_message(message.chat.id, "Аудиокниги жанра "+genre)
		for value in cursor.execute(sqlgenre, (genre,)).fetchmany(4):
			separator=""
			dats = separator.join(value)
			data.append(InputMediaAudio(dats))
		bot.send_media_group(message.chat.id, data)


bot.polling(none_stop=True, interval=0)
