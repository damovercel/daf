#!/bin/python3

from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from os import environ, mkdir
from lxml.html import fromstring
from json import load
from cloudscraper import create_scraper
# from urllib.parse import quote

###        								###
###        								###
###        								###
print("arregral la linea 32, esta feisima")
###        								###
###    									###
###    									###

BOT_TOKEN = environ.get("BOT_TOKEN")
DEBUG_ID = environ.get("DEBUG_ID")

CONFIG = load(open("./config.json"))
WEB_HEADERS = CONFIG["WEB_HEADERS"]
WEB_BROWSER = CONFIG["WEB_BROWSER"]
URL_ANIMEFLV = CONFIG["URL_ANIMEFLV"]
CDN_ANIMEFLV = CONFIG["CDN_ANIMEFLV"]

scraper = create_scraper(browser=WEB_BROWSER)

def printt(*values):
	rep = ""
	if len(values) == 1:
		rep += values[0]
	else:
		for c in values:
			rep += f"{c}\n"
	bot.send_message(chat_id=DEBUG_ID, text=rep)




def command_start(update, context):
	chatId = update["message"]["chat"]["id"]
	print("/start")
	bot.send_message(chat_id=chatId, text="Bot en creacion...")

def command_find(update, context):
	chatId = update["message"]["chat"]["id"]
	to_find_string = ' '.join(context.args)
	message_searching = bot.send_message(chat_id=chatId, text=f"Buscando: {to_find_string}", disable_web_page_preview=True)
	find_string = ""
	req = scraper.get(url=f"{URL_ANIMEFLV}/browse?q={'+'.join(context.args)}")
	raw_tree = fromstring(html=req.content)
	print(req.status_code)

	if req.status_code == 200:
		for v in raw_tree.xpath('//*[@class="ListAnimes AX Rows A03 C02 D02"]')[0]:
			v_name = v[0][1][0][0].text
			v_url_short = v[0][0].attrib["href"]
			v_url = f"{URL_ANIMEFLV}{v_url_short}"
			find_string += f"<b>{v_name}</b>\n<code>/info {v_url}</code>\n\n"
	if find_string:
		bot.edit_message_text(chat_id=chatId, message_id=message_searching["message_id"], text=f"Resultados para <b>{to_find_string}</b>:\n\n{find_string}", parse_mode="html", disable_web_page_preview=True)
	else:
		bot.edit_message_text(chat_id=chatId, message_id=message_searching["message_id"], text=f"No hay resultados para: <b>{to_find_string}</b>", parse_mode="html", disable_web_page_preview=True)

def command_info(update, context):
	chatId = update["message"]["chat"]["id"]
	if len(context.args) != 1:
		bot.send_message(chat_id=chatId, text="Error: El numero de argumentos es incorrecto")
		return
	to_info_find = context.args[0]
	message_searching = bot.send_photo(chat_id=chatId, photo=open("./work.jpg", "rb"), caption=f"Obteniendo detalles de: <b>{to_info_find}</b>", parse_mode="html")
	req = scraper.get(url=to_info_find)
	raw_tree = fromstring(html=req.content)
	print(req.status_code)

	if req.status_code == 200:
		t_title = raw_tree.xpath('//*[@class="Ficha fchlt"]/div[2]/h1')[0].text
		t_type = raw_tree.xpath('//*[@class="Ficha fchlt"]/div[2]/span')[0].text
		t_stars = raw_tree.xpath('//*[@class="Votes"]/span')[0].text
		t_votes = raw_tree.xpath('//*[@class="Nmbr"]/span')[0].text

		t_status = raw_tree.xpath('//*[@class="AnmStts A"]/span')[0].text
		t_image_url = URL_ANIMEFLV + raw_tree.xpath('//*[@class="AnimeCover"]/div/figure/img')[0].attrib["src"]
		print(t_image_url)
		t_genres_list = []
		for g in raw_tree.xpath('//*[@class="Nvgnrs"]')[0]:
			t_genres_list.append(g.text)
		t_genres = ", ".join(t_genres_list)
		t_sinopsis = raw_tree.xpath('//*[@class="Description"]/p')[0].text
		script_text = ""
		for s in raw_tree.xpath('//*/script'):
			if s.text is not None:
				if s.text.find("anime_info") != -1:
					script_text = s.text

		first_ne = script_text.find(";")
		second_ne = script_text.find(";", first_ne + 1)
		first_eq = script_text.find("=")
		second_eq = script_text.find("=", first_eq + 1)
		var_anime_info = eval(script_text[first_eq + 1:first_ne].strip())
		var_episodes = eval(script_text[second_eq + 1:second_ne].strip())
		
		t_episodes = 0
		for i, e in enumerate(var_episodes):
			if type(e[0]) is int:
				if i == 0:
					t_episodes = e[0]
				elif e[0] > t_episodes:
					t_episodes = e[0]

		info_result = f"<b>{t_title}</b>\n\n"
		info_result += f"<b>Type</b>: {t_type}\n"
		info_result += f"<b>Status</b>: {t_status}\n"
		info_result += f"<b>Episodes</b>: {t_episodes}\n"
		info_result += f"<b>Score</b>: {t_stars}⭐️ / {t_votes} votes\n"
		info_result += f"<b>Genres</b>: {t_genres}\n\n"
		info_result += f"<b>Sinopsis</b>: {t_sinopsis}\n\n"
		info_result += f"<code>/caps {to_info_find}</code>"
		print(info_result, len(info_result))
		bot.edit_message_media(chat_id=chatId, media=InputMediaPhoto(media=f"{URL_ANIMEFLV}/uploads/animes/covers/{var_anime_info[0]}.jpg", caption=info_result, parse_mode="html") , message_id=message_searching["message_id"])

def command_caps(update, context):
	chatId = update["message"]["chat"]["id"]
	if len(context.args) != 1:
		bot.send_message(chat_id=chatId, text="Error: El numero de argumentos es incorrecto")
		return
	to_caps_find = context.args[0]
	message_searching = bot.send_message(chat_id=chatId, text=f"Obteniendo capitulos de: <b>{to_caps_find}</b>", parse_mode="html", disable_web_page_preview=True)
	req = scraper.get(url=to_caps_find)
	raw_tree = fromstring(html=req.content)
	print(req.status_code)

	if req.status_code == 200:
		t_title = raw_tree.xpath('//*[@class="Ficha fchlt"]/div[2]/h1')[0].text

		t_cap_name = []
		script_text = ""
		for s in raw_tree.xpath('//*/script'):
			if s.text is not None:
				if s.text.find("anime_info") != -1:
					script_text = s.text
		first_ne = script_text.find(";")
		second_ne = script_text.find(";", first_ne + 1)
		first_eq = script_text.find("=")
		second_eq = script_text.find("=", first_eq + 1)
		var_anime_info = eval(script_text[first_eq + 1:first_ne].strip())
		var_episodes = eval(script_text[second_eq + 1:second_ne].strip())

		for e in var_episodes:
			t_cap_name.append(e[0])

		if t_cap_name[0] > t_cap_name[-1]:
			t_cap_name.reverse()
		print(" ".join([str(e) for e in t_cap_name]))

		for i, c in enumerate(t_cap_name):
			if i == 0:
				bot.edit_message_text(chat_id=chatId, message_id=message_searching["message_id"], text=f"Lista de episodios de: <b>{t_title}</b>", parse_mode="html", disable_web_page_preview=True)
			bot.send_message(chat_id=chatId, text=f"<b>Episodio</b>: {c}\n<code>/download {URL_ANIMEFLV}/ver/{var_anime_info[2]}-{c}</code>", parse_mode="html")

def command_download(update, context):
	chatId = update["message"]["chat"]["id"]
	if len(context.args) != 1:
		bot.send_message(chat_id=chatId, text="Error: El numero de argumentos es incorrecto")
		return
	to_caps_download = context.args[0]
	message_searching = bot.send_photo(chat_id=chatId, photo=open("./work.jpg", "rb"), caption=f"Analizando: <b>{to_caps_download}</b>", parse_mode="html")

	req = scraper.get(url=to_caps_download)
	raw_tree = fromstring(html=req.content)
	print(req.status_code)

	if req.status_code == 200:
		script_text = ""
		for s in raw_tree.xpath('//*/script'):
			if s.text is not None:
				if s.text.find("anime_id") != -1:
					script_text = s.text
		first_ne = script_text.find(";")
		third_ne = script_text.find(";", script_text.find(";", first_ne + 1) + 1)
		first_eq = script_text.find("=")
		third_eq = script_text.find("=", script_text.find("=", first_eq + 1) + 1)
		var_anime_id = eval(script_text[first_eq + 1:first_ne].strip())
		var_episode_number = eval(script_text[third_eq + 1:third_ne].strip())

		t_title = raw_tree.xpath('//*[@class="Brdcrmb fa-home"]/a[2]')[0].text
		download_info = ""
		download_info += f"Intentando obtener enlaces de descarga de: "
		download_info += f"<b>{t_title}</b> / Episodio {var_episode_number}"
		# https://cdn.animeflv.net/screenshots/'+anime_info[0]+'/'+episodes[i][0]+'/th_3.jpg
		bot.edit_message_media(chat_id=chatId, media=InputMediaPhoto(media=f"{CDN_ANIMEFLV}/screenshots/{var_anime_id}/{var_episode_number}/3.jpg", caption=download_info, parse_mode="html") , message_id=message_searching["message_id"])

		mega_list = []
		zippyshare_list = []

		for l in raw_tree.xpath('//*[@class="RTbl Dwnl"]/tbody')[0]:
			if l.xpath('./td[3]')[0].text == "SUB":
				l_name = l.xpath('./td[1]')[0].text
				if l_name in ["MEGA", "Mega", "mega"]:
					mega_list.append(l.xpath('./td[4]/a')[0].attrib["href"])
				elif l_name in ["ZIPPYSHARE", "ZippyShare", "Zippyshare", "zippyshare"]:
					mega_list.append(l.xpath('./td[4]/a')[0].attrib["href"])

		if len(mega_list + zippyshare_list) > 0:
			download_info = ""
			download_info += f"Intentando descargar: "
			download_info += f"<b>{t_title}</b> / Episodio {var_episode_number}\n"
			download_info += f"<b>Url</b>: 0/{len(mega_list + zippyshare_list)}"
			bot.edit_message_caption(chat_id=chatId, message_id=message_searching["message_id"], caption=download_info, parse_mode="html")



if __name__ == '__main__':
	updater = Updater(BOT_TOKEN)
	dispatcher = updater.dispatcher
	bot = updater.bot

	dispatcher.add_handler(CommandHandler(command="start", callback=command_start))
	dispatcher.add_handler(CommandHandler(command="find", callback=command_find))
	dispatcher.add_handler(CommandHandler(command="info", callback=command_info))
	dispatcher.add_handler(CommandHandler(command="caps", callback=command_caps))
	dispatcher.add_handler(CommandHandler(command="download", callback=command_download))
	bot.send_message(chat_id=DEBUG_ID, text="Polling!!!")
	print("Polling!!!")
	updater.start_polling(drop_pending_updates=True)