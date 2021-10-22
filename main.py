from random import randrange
from time import sleep

from config import Cfg as cfg

import threading

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from bs4 import BeautifulSoup
import requests
from os import path
from pydub import AudioSegment
import speech_recognition as sr

HEADERS = cfg.HEADERS
rand_joke = cfg.rand_joke
key = cfg.key
counters = cfg.counters
img_counter = cfg.img_counter
first_exec = cfg.first_exec
rand_img_joke = cfg.rand_img_joke
osk = cfg.osk


def request(URL):
	response = requests.get(URL, headers = HEADERS)
	return BeautifulSoup(response.content, 'html.parser')

#Memoization

def MemZ_img(soup):
	return soup.findAll('img', class_='serp-item__thumb justifier__thumb')

def MemZ1(soup):
	joke_blocks = soup.findAll('div', class_ = 'div_joke_content')
	return list(joke_blocks[0].findAll('p', class_ = 'small_joke_list'))

def MemZ2(soup):
	joke_blocks = soup.findAll('div', class_='story-block story-block_type_text')
	joke_list2 = list(joke_blocks[0].findAll('p'))
	i = 2
	while i < len(joke_list2):
		joke_list2.pop(i)
		i += 2
	return joke_list2
	
def MemZ3(soup):
	return soup.findAll('div', class_='text')

def MemZ4(soup):
	return soup.findAll('div', class_='anekdot')

def MemZ5(soup):
	a = list(soup.findAll('p', class_='paragraph unit unit_text_m'))
	i = 1
	while i < len(a):
		a.pop(i)
		i += 1
	return a
def MemZ6(soup):
	a = list(soup.findAll('div',class_='post'))
	del a[0]
	for i in range(len(a)):
		a[i] = list(a[i])
		for j in a[i]:
			if str(j).startswith("<hr"):
				a[i] = a[i][:a[i].index(j)]
				break
	index = False
	for i in range(len(a)):
		if index:
			a = a[:index]
			break
		j = 0
		while j < len(a[i]):
			if str(a[i][j]).startswith('<br'):
				del a[i][j]
			if str(a[i][j]).startswith('<a'):
				index = i
				break
			j += 1
	x = 0
	while x < len(a):
		if len(a[x]) > 1:
			joke_list[1].append(a[x])
			del a[x]
		else:
			a[x] = a[x][0]
		x += 1
	return a

#End code of Memoization

#Joke parsers
def parse(jokes, counter1, is_parse2=False):
	if not is_parse2:
		counters[counter1] = counters[counter1] + 1 if counters[counter1] != len(jokes) else -1
		jKfinal = [jokes[counters[counter1]]]
	else:
		counters[counter1] = counters[counter1] + 2 if counters[counter1] != len(jokes) else 0
		jKfinal = [jokes[counters[counter1]],jokes[counters[counter1]+1]]
	return jKfinal,counters[counter1]

#End of Joke parsers

def sender(id, text, user=False):
	args = {"message": text, "random_id" : 0}
	if not user:
		args["chat_id"] = id
	else:
		args["user_id"] = id
	vk_session.method('messages.send', args)

def get_bebra():
	bebr = {}
	with open('bebra.txt', 'r') as file:
		a = file.read()
		a = a.split()
		file.close()
	i = 0
	while i < len(a):
		bebr[int(a[i])] = int(a[i+1])
		[a.pop(0) for x in range(2)]
		i += 1
	return bebr 
def save_bebra_count(bebr):
	with open('bebra.txt','w') as file:
		for a in bebr:
			file.write(" "+str(a)+" "+str(bebr[a]))
			print(f'save action {a} {bebr[a]}')
		file.close()


#main code
def get_ank():
	joke_list_num = randrange(1,joke_list_count)
	URL = rand_joke[joke_list_num]

	num_joke_list,parser,counter = get_jokes_lists(URL)

	ank,counters[counter] = parser(num_joke_list,counter) if joke_list_num != 2 else parser(num_joke_list,counter,True)
	txt = ''
	for a in ank:
		if joke_list_num == 1:
			for i in a.get_text().split():
				txt += i +" "
		else:
			txt += a.get_text()+"\n"
	return txt
def get_jokes_lists(URL):
	soup = {
		'http://old.301-1.ru/small-joke/': [joke_list[0],parse,0],
		'https://pikabu.ru/story/shutki_za_300_5842437': [joke_list[1],parse,1],
		'https://nekdo.ru/page/300/': [joke_list[2],parse,2],
		'https://anekdotov.net/anekdot/': [joke_list[3],parse,3],
		'https://anekdot-ru.turbopages.org/anekdot.ru/s/': [joke_list[4],parse,4],
		'https://vse-shutochki.ru/anekdoty/': [joke_list[5],parse,5]
	}
	return soup[URL]

joke_list = [ [] for x in range(len(rand_joke))]
joke_list_count = len(joke_list)+1
MemZ_init = {
	1:MemZ1,
	2:MemZ2,
	3:MemZ3,
	4:MemZ4,
	5:MemZ5,
	6:MemZ6
}
MemZ_img_init = {
	1:MemZ_img
}
for a in range(1,joke_list_count):
	soup = request(rand_joke[a])
	if a == 1:
		joke_list[a-1] = MemZ_init[a](soup)
		soup = request(rand_img_joke[a])
		img_list = MemZ_img_init[a](soup)
	elif a:
		joke_list[a-1] = MemZ_init[a](soup)



vk = vk_session = vk_api.VkApi(token= key)
longpoll = VkBotLongPoll(vk_session, 207987095)

bebra_count = get_bebra()

print("Bot started")
voice = False
for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW:
		if voice and (event.object.message.get('fwd_messages', False) or event.object.message.get('attachments', False)):
			voice = False
			if event.object.message.get('fwd_messages', False):
				link = event.object.message['fwd_messages'][0]['attachments'][0]['audio_message']['link_mp3']
			elif event.object.message['attachments'][0]('audio_message', False):
				link = event.object.message['attachments'][0]['audio_message']['link_mp3']
			vc = requests.get(link)
			with open('i.mp3','wb') as file:
				file.write(vc.content)
				file.close()

			sound = AudioSegment.from_mp3('i.mp3')
			sound.export('im.wav', format="wav")

			AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "im.wav")
			r = sr.Recognizer()
			with sr.AudioFile(AUDIO_FILE) as source:
				audio = r.record(source)
			try:
				text = "текст: "+r.recognize_google(audio, language="ru-RU")
			except:
				text = 'Error voice !'
			sender(chat_id,text)

		if event.from_chat:
			message = event.object.message['text'].lower()
			user_id = event.object.message['from_id']
			chat_id = event.chat_id


			if message.startswith('!анекдот'):
				print(f'{message} from {user_id}')
				text = get_ank()
				sender(chat_id,text)

			elif message.startswith('!sus'):
				print(f'{message} from {user_id}')
				message = message.split()
				if len(message) > 1:
					if message[1].startswith("[id"):
						userF_id = message[1][1:12]
						user_profile_info = vk_session.method('users.get', {"user_ids":userF_id,'fields': 'sex'})[0]
						text = str(user_profile_info['first_name'])+" "+str(user_profile_info['last_name'])+" "+osk[user_profile_info['sex']][randrange(0,len(osk[1]))]
						sender(chat_id,text)
					else:
						text = 'Неверное id !'
						sender(chat_id,text)
			elif message.startswith('!пикча'):
				print(f'{message} from {user_id}')
				message = message.split()
				try:
					if len(message) == 1:
						message.append(img_counter)
						img_counter += 1
					else:
						message[1] = int(message[1])
					if message[1] > len(img_list) or message[1] <= 0:
						raise ValueError
					else:
						message[1] -= 1
						image = requests.get('http:'+str(img_list[message[1]].get('src')))
						with open('i.jpg','wb') as file:
							file.write(image.content)
							file.close()
						a = vk.method("photos.getMessagesUploadServer")
						b = requests.post(a['upload_url'], files={'photo': open('i.jpg', 'rb')}).json()
						c = vk.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
						d = "photo{}_{}".format(c["owner_id"], c["id"])
						if type == 2:
							txt = f"Лови пикчу {message[1]+1}"
						else:
							txt = "Лови пикчу"
						vk.method("messages.send", {"chat_id":chat_id, "message":txt, "attachment": d, "random_id": 0})

				except ValueError:
					text = 'Неверное id !'
					sender(chat_id,text)
				except:
					text = 'Error'
					sender(chat_id,text)
			elif message.startswith('!бебра'):
				if user_id not in bebra_count:
					bebra_count[user_id] = 5
					save_bebra_count(bebra_count)
				if bebra_count[user_id] > 0:
					user_profile_info = vk_session.method('users.get', {"user_ids":user_id, 'fields':'sex'})[0]
					text = str(user_profile_info['first_name'])+" "+str(user_profile_info["last_name"])
					text += ' занюхнула бебру' if user_profile_info['sex'] == 1 else ' занюхнул бебру'
					sender(chat_id,text)
					bebra_count[user_id] -= 1
					save_bebra_count(bebra_count)
				else:
					user_profile_info = vk_session.method('users.get', {"user_ids":user_id})[0]
					text = 'Вы вынюхали дневную дозу бебры, '+str(user_profile_info['first_name'])+" "+str(user_profile_info['last_name'])
					sender(chat_id,text)
			elif message.startswith('!voice'):
				sender(chat_id,'Жду голосовое..')
				voice = True