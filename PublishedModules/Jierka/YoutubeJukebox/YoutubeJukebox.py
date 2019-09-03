import json
import subprocess

import os
import re
import requests
import youtube_dl

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class YoutubeJukebox(Module):
	"""
	Author: Jierka
	Description: Allows to play music from youtube
	"""

	_INTENT_SEARCH_MUSIC = Intent('SearchMusic')

	BASE_URL = 'https://www.youtube.com/results?search_query='
	REGEX = r"<a\b(?=[^>]* class=\"[^\"]*(?<=[\" ])yt-uix-tile-link[\" ])(?=[^>]* href=\"([^\"]*))"

	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_SEARCH_MUSIC
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def getWildcard(self, session):
		if type(session.payload) is str:
			inputt = json.loads(session.payload)['input']
		else:
			inputt = session.payload['input']

		utterances = self.getUtterancesByIntent(self._INTENT_SEARCH_MUSIC)
		self._logger.info('[{}] Raw input {}'.format(self.name, inputt))

		for utterance in utterances:
			for word in utterance.split(' '):
				inputt = inputt.replace(str(word.strip()) + ' ', '')
				inputt = inputt.replace(' ' + str(word.strip()) + ' ', '')
				inputt = inputt.replace(' ' + str(word.strip()), '')

		inputt = inputt.strip()

		clearInput = ''

		for word in inputt.split(' '):
			if len(word) > 1:
				clearInput = clearInput + str(word) + ' '

		self._logger.info('[{}] Cleaned input {}'.format(self.name, clearInput))

		return clearInput


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		sessionId = session.sessionId

		wildcardQuery = self.getWildcard(session)

		if intent == self._INTENT_SEARCH_MUSIC:
			self.endSession(sessionId=sessionId)

			r = requests.get(self.BASE_URL + wildcardQuery)
			page = r.text
			page = page[page.find('item-section'):]
			matches = re.finditer(self.REGEX, page, re.MULTILINE)
			videolist = []

			for matchNum, match in enumerate(matches, start=1):
				if 'list' not in match.group(1):
					tmp = 'https://www.youtube.com' + match.group(1)
					if len(tmp) <= 70:
						videolist.append(tmp)

			if len(videolist) == 0:
				self.say(text=self.randomTalk(text='noMatch', replace=[
					wildcardQuery
				]), siteId=siteId)
				return True

			item = videolist[1]
			videoKey = item.split('=')[1]
			self._logger.info('[{}] Music video found {}'.format(self.name, item))

			youtubeDlOptions = {
				'outtmpl': '%(id)s.%(ext)s',
				'format': 'bestaudio/best',
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192',
				}]
			}

			resourceDir = self.getResource(resourcePathFile='audio')
			outputFile = os.path.join(resourceDir, '{}.mp3'.format(videoKey))

			if not os.path.isfile(outputFile):
				with youtube_dl.YoutubeDL(youtubeDlOptions) as ydl:
					os.chdir(resourceDir)
					ydl.download([item])

			subprocess.run(['sudo', 'mpg123', outputFile])

		return True
