import json
import subprocess

import os
import re
import requests
from requests import RequestException
import youtube_dl

from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators, IntentHandler


class YoutubeJukebox(Module):
	"""
	Author: Jierka
	Description: Allows to play music from youtube
	"""

	def getWildcard(self, session):
		if isinstance(session.payload, str):
			inputt = json.loads(session.payload)['input']
		else:
			inputt = session.payload['input']

		utterances = self.getUtterancesByIntent(self._INTENT_SEARCH_MUSIC)
		self.logInfo(f'Raw input {inputt}')

		inputtList = inputt.split()
		for utterance in utterances:
			inputtList = [value for value in inputtList if value not in utterance.split()]

		clearInput = ' '.join(inputtList)

		self.logInfo(f'Cleaned input {clearInput}')

		return clearInput


	@IntentHandler('SearchMusic')
	@Decorators.anyExcept(exceptions=RequestException, text='noServer', printStack=True)
	@Decorators.online
	def searchMusicIntent(self, session: DialogSession, **_kwargs):
		wildcardQuery = self.getWildcard(session)

		self.endSession(sessionId=session.sessionId)

		response = requests.get("http://www.youtube.com/results", {'search_query':wildcardQuery})
		response.raise_for_status()
		videolist = re.findall(r'href=\"\/watch\?v=(.{11})', response.text)

		if not videolist:
			self.say(text=self.randomTalk(text='noMatch', replace=[wildcardQuery]), siteId=session.siteId)
			return

		videoKey = videolist[0]
		videoUrl = f'http://www.youtube.com/watch?v={videoKey}'
		self.logInfo(f'Music video found {videoUrl}')

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
				ydl.download([videoUrl])

		subprocess.run(['sudo', 'mpg123', outputFile])
