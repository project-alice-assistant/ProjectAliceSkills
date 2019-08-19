# -*- coding: utf-8 -*-

import json


import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
import requests
import os
import re
import youtube_dl
import subprocess


class YoutubeJukebox(Module):
	"""
	Author: Jierka
	Description: Allows to play music from youtube
	"""

	_INTENT_SEARCH_MUSIC = Intent('SearchMusic')

	BASE_URL = "https://www.youtube.com/results?search_query="
	REGEX = r"<a\b(?=[^>]* class=\"[^\"]*(?<=[\" ])yt-uix-tile-link[\" ])(?=[^>]* href=\"([^\"]*))"

	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_SEARCH_MUSIC
		]

		super().__init__(self._SUPPORTED_INTENTS)

	def getWildcard(self, session):
		input = ''

		if type(session.payload) is str:
			input = json.loads(session.payload)['input']
		else:
			input = session.payload['input']

		utterances = self.getUtterancesByIntent(self._INTENT_SEARCH_MUSIC)
		print("[{}] Raw input {}".format(self.__class__.__name__, input))

		for utterance in utterances:
			for word in utterance.split(" "):
				input = input.replace(str(word.strip()), "")

		input = input.strip()

		clearInput = ''

		for word in input.split(" "):
			if len(word) > 1:
				clearInput = clearInput + str(word) + " "

		print("[{}] Cleaned input {}".format(self.__class__.__name__, clearInput))

		return clearInput

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		slots = session.slots
		sessionId = session.sessionId
		customData = session.customData

		wildcardQuery = self.getWildcard(session)

		if intent == self._INTENT_SEARCH_MUSIC:
			managers.MqttServer.endTalk(sessionId=sessionId, text="")

			r = requests.get(self.BASE_URL + wildcardQuery)
			page = r.text
			matches = re.finditer(self.REGEX, page, re.MULTILINE)
			videolist = []

			for matchNum, match in enumerate(matches, start=1):
				if "list" not in match.group(1):
					tmp = 'https://www.youtube.com' + match.group(1)
					videolist.append(tmp)

			if len(videolist) == 0:
				managers.MqttServer.say(text=self.randomTalk(text='noMatch', replace=[
					wildcardQuery
				]), client=siteId)
				return True

			item = videolist[0]
			videoKey = item.split('=')[1]
			print("[{}] Music video found {}".format(self.__class__.__name__, item))

			youtubeDlOptions = {
				'outtmpl': '%(id)s.%(ext)s',
				'format': 'bestaudio/best',
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192',
				}]
			}

			resourceDir = os.path.dirname(os.path.realpath(__file__)) + '/audio'
			outputFile = resourceDir + '/' + videoKey + '.mp3'

			if not os.path.isfile(outputFile):
				with youtube_dl.YoutubeDL(youtubeDlOptions) as ydl:
					os.chdir(resourceDir)
					ydl.download([item])

			subprocess.run(['sudo', 'mpg123', outputFile])

		return True

