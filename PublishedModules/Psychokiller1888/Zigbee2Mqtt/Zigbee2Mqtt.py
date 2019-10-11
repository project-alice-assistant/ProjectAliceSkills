import getpass
import subprocess
from pathlib import Path

from core.base.model.Module import Module
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession


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


	def onModuleInstalled(self):
		service = f"""\
[Unit]
Description=zigbee2mqtt
After=network.target

[Service]
ExecStart=/usr/bin/npm start
WorkingDirectory=/opt/zigbee2mqtt
StandardOutput=inherit
StandardError=inherit
Restart=always
User={getpass.getuser()}

[Install]
WantedBy=multi-user.target"""

		filepath = Path(commons.rootDir(), 'zigbee2mqtt.service')
		filepath.write_text(service)
		subprocess.run(['sudo', 'mv', str(filepath), '/etc/systemd/system/zigbee2mqtt.service'])
		subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
