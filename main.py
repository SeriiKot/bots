import telebot
from telebot import types
from pytube import YouTube
from moviepy.editor import VideoFileClip
from pathlib import Path
import os
import psutil
import subprocess
import sqlite3
from datetime import datetime, timedelta

TOKEN = "6344833079:AAE7OwH-dZkkh-JXZeGnS7dJ_Dz9cHNPosQ"
bot = telebot.TeleBot(TOKEN)

# Создание соединения с базой данных
conn = sqlite3.connect('subscriptions.db')
cursor = conn.cursor()

# Создание таблицы для ID чатов и времени регистрации
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        registration_date TEXT
    )
''')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, "Hello!\nSend me the link YouTube video/just video(up to 50 minutes)")
	
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def text(message):
	url_video = message.text
	chat_id = message.chat.id
	save_path = "./video"
	download_video(url_video, chat_id, message, save_path)

@bot.message_handler(commands=['info'])
def send_status(message):
	chat_id = message.chat.id

	try:
		# Получаем статистику
		cpu_load = psutil.cpu_percent()
		memory_info = psutil.virtual_memory()
		swap_info = psutil.swap_memory()
		temperatures = get_cpu_temperatures()
			
		# Отправляем сообщение с полученными данными
		message_text = (
			f"Cpu: {cpu_load}%\n"
			f"Mem: {memory_info.percent}%\n"
			f"Swap: {swap_info.percent}%\n"
			f"Temp: {temperatures}°C"
		)
		bot.send_message(chat_id, message_text)
	except Exception as e:
		bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")

def get_cpu_temperatures(file_path="/sys/class/thermal/thermal_zone0/temp"):
	try:
		with open(file_path, 'r') as file:
			# Читаем значение температуры из файла
			temperature_str = file.read().strip()

			# Преобразуем строку в целое число
			temperature = int(temperature_str)

			# Преобразуем температуру из тысяч градусов Цельсия в градусы Цельсия
			temperature_celsius = temperature / 1000.0

			return temperature_celsius
	except Exception as e:
		#print(f"Error getting CPU temperature: {str(e)}")
		return "N/A"

@bot.message_handler(commands=['donate'])
def donate(message):
	bot.send_message(message.chat.id, "Thank you!^^\n+37377804707(Qiwi, Agroprombank)")

@bot.message_handler(content_types=["video"])
def video(message):
	chat_id = message.chat.id
	try:
		# Получаем информацию о видео
		video = message.video

		# Получаем уникальный идентификатор файла
		file_id = video.file_id

		# Получаем информацию о файле
		file_info = bot.get_file(file_id)

		# Получаем ссылку для скачивания файла
		file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

		# Определяем путь для сохранения видео
		save_path = f"./video/{chat_id}/{file_id}.mp4"
		folder_p = f"./video/{chat_id}"
		folder_path = Path(folder_p)
		if not folder_path.exists():
			folder_path.mkdir(parents=True, exist_ok=True)

		# Скачиваем видео
		print("Downloading video...")
		bot.send_message(chat_id, f"Download video...")
		os.system(f"wget -O {save_path} {file_url}")
		print("Dowmload video: OK")
		bot.send_message(chat_id, f"Dowmload video: OK")

		# Отправляем на обработку
		convert(f"./video/{chat_id}/{file_id}.mp4", f"./audio/{file_id}({chat_id}).mp3", chat_id)

	except Exception as e:
		print(f"Error handling video: {e}")
		bot.reply_to(message, "Error downloading video.")
	

def download_video(url, chat_id, message, save_path):
	try:
		yt = YouTube(url)
		video = yt.streams.get_lowest_resolution()
		print(f"Download video {yt.title}")
		ad = yt.title.replace('|', '').replace('?', '').replace(',', '').replace("'", "").replace('"', '').replace("#", "").replace(".", "")
		bot.send_message(chat_id, f"Download video: {yt.title}", parse_mode="html")
		video.download(f"{save_path}/{chat_id}")
		print("Download video: OK")
		bot.send_message(chat_id, "Download video: OK")
		#bot.edit_message_text(text="Download video: OK", chat_id=chat_id, message_id=message.message_id)
		#ad = yt.title.replace('|', '').replace('?', '').replace(',', '').replace("'", "").replace('"', '')
		audio = f"./video/{chat_id}/{ad}.mp4"
		convert(audio, f"./audio/{ad}({chat_id}).mp3", chat_id)
	except Exception as e:
		print(f"Error: {str(e)}")
		bot.send_message(chat_id, "Sorry, an unexpected error occurred or this video cannot be downloaded yet due to some political issues.\nWe will fix this problem soon.\nTry something different.")


def convert(input_path, output_path, chat_id):
	try:
		print("Convert...")
		bot.send_message(chat_id, "Convert...")
		#bot.edit_message_text(text="Convert...", chat_id=chat_id, message_id=message.message_id)
		video_clip = VideoFileClip(input_path)
		audio_clip = video_clip.audio
		audio_clip.write_audiofile(output_path)
		audio_clip.close()
		video_clip.close()
		print("Convert: OK")
		bot.send_message(chat_id, "Convert: OK")
		#bot.edit_message_text(text="Convert: OK", chat_id=chat_id, message_id=message.message_id)
		delete(input_path)
		send_audio(chat_id, output_path)
	except Exception as e:
		print(f"Error: {str(e)}")
		bot.send_message(chat_id, f"Error: {str(e)}")
		delete(input_path)

def send_audio(chat_id, input_audio):
	with open(input_audio, "rb") as audio_file:
		bot.send_document(chat_id, audio_file)
		delete(input_audio)
			

def delete(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
	
	
	
bot.polling()
