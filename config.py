
class Cfg:
	def __init__():
		try:
			with open('bebra.txt','r') as file:
				a = file.read()
				if a:
					first_exec = False
				else:
					first_exec = True
				file.close()
		except:
			with open('bebra.txt','w') as file:
				first_exec = True
				file.close()
		return first_exec
	first_exec = __init__()
	key = '9850a68d890a615aa18ec387646a77d3cfaf3fb8f5b9860d7e582da9f3bf0e43b924ebc5026fc1c75cd63'

	HEADERS = {
	 		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.41 YaBrowser/21.5.0.582 Yowser/2.5 Safari/537.36'
		}

	osk = {
		2:[
			'pidor',
			'bullshit',
			', где лопата?',
			'my slave',
			'работать!!',
			],
		1:[
			', где лопата?',
			', а по жопе?',
			'my slave',
			'работать!!',
			'stupid',
			]
		}

	rand_joke = {
		1:'http://old.301-1.ru/small-joke/',
		2:'https://pikabu.ru/story/shutki_za_300_5842437',
		3:'https://nekdo.ru/page/300/',
		4:'https://anekdotov.net/anekdot/',
		5:'https://anekdot-ru.turbopages.org/anekdot.ru/s/',
		6:'https://vse-shutochki.ru/anekdoty/'
	}
	rand_img_joke = {
		1:'https://yandex.ua/images/search?text=смешные%20приколы%202021&from=tabbar',
	}
	counters = [-1 for x in range(len(rand_joke))]
	counters[2-1] = 0
	img_counter = 1