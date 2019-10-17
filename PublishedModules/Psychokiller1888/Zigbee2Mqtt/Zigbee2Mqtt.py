import getpass
import subprocess
from pathlib import Path

from core.base.model.Module import Module
from core.commons import commons


class Zigbee2Mqtt(Module):
	"""
	Author: Psychokiller1888
	Description: Have your zigbee devices communicate with alice directly over mqtt
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= []
		super().__init__(self._SUPPORTED_INTENTS)


	def onStart(self) -> list:
		super().onStart()
		subprocess.run(['sudo', 'systemctl', 'start', 'zigbee2mqtt'])
		return self._SUPPORTED_INTENTS


	def onStop(self):
		super().onStop()
		subprocess.run(['sudo', 'systemctl', 'stop', 'zigbee2mqtt'])
