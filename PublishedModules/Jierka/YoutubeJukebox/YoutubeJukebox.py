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
		self._INTENTS = {
			self._INTENT_SEARCH_MUSIC: self.searchMusicIntent
		}

		super().__init__(self._INTENTS)


	def getWildcard(self, session):
		if type(session.payload) is str:
			inputt = json.loads(session.payload)['input']
		else:
			inputt = session.payload['input']

		utterances = self.getUtterancesByIntent(self._INTENT_SEARCH_MUSIC)
		self._logger.info(f'[{self.name}] Raw input {inputt}')

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

		self._logger.info(f'[{self.name}] Cleaned input {inputt}')

		return clearInput


	def searchMusicIntent(self, intent: str, session: DialogSession):
		siteId = session.siteId
		sessionId = session.sessionId
		wildcardQuery = self.getWildcard(session)

		self.endSession(sessionId=sessionId)

		r = requests.get(self.BASE_URL + wildcardQuery)
		page = r.text
		page = page[page.find('item-section'):]
		matches = re.finditer(self.REGEX, page, re.MULTILINE)
		videolist = list()

		for matchNum, match in enumerate(matches, start=1):
			if 'list' not in match.group(1):
				tmp = 'https://www.youtube.com' + match.group(1)
				if len(tmp) <= 70:
					videolist.append(tmp)

		if not videolist:
			self.say(text=self.randomTalk(text='noMatch', replace=[
				wildcardQuery
			]), siteId=siteId)
			return

		item = videolist[1]
		videoKey = item.split('=')[1]
		self._logger.info(f'[{self.name}] Music video found {item}')

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
		outputFile = os.path.join(resourceDir, f'{videoKey}.mp3')

		if not os.path.isfile(outputFile):
			with youtube_dl.YoutubeDL(youtubeDlOptions) as ydl:
				os.chdir(resourceDir)
				ydl.download([item])

		subprocess.run(['sudo', 'mpg123', outputFile])
