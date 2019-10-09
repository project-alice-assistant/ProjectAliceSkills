import json
from typing import Tuple

import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons.commons import online
from core.dialog.model.DialogSession import DialogSession


class FreeCurrencyConverterDotCom(Module):
	"""
	Author: Psychokiller1888
	Description: Let's you convert world currencies
	"""

	_INTENT_CONVERT_CURRENCY = Intent('ConvertCurrency')
	_INTENT_ANSWER_CURRENCY = Intent('AnswerCurrency', isProtected=True)


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_ANSWER_CURRENCY,
			self._INTENT_CONVERT_CURRENCY
		]

		super().__init__(self._SUPPORTED_INTENTS)
		self._apiKey = self.getConfig('apiKey')

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_CONVERT_CURRENCY or session.previousIntent == self._INTENT_CONVERT_CURRENCY:
			try:
				self.convertCurrency(session)
			except Exception as e:
				self._logger.error(e)
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('noServer'), siteId=session.siteId)

		return True


	def extractSlotValues(self, slots: dict, customData: dict) -> Tuple[str, str, str]:
		amount = 1
		if 'Amount' in slots:
			amount = slots['Amount'][0].value['value']
		else
			amount = customData.get('amount')

		if 'ToCurrency' in slotsObject:
			toCurrency = slots['ToCurrency'][0].value['value']
		else
			toCurrency = customData.get('toCurrency', self.ConfigManager.getAliceConfigByName('baseCurrency', self.name))

		fromCurrency = None
		if 'FromCurrency' in slots:
			fromCurrency = slots['FromCurrency'][0].value['value']
		elif 'Currency' in slots:
			fromCurrency = slots['Currency'][0].value['value']

		return (amount, toCurrency, fromCurrency)


	def offlineHandler(self, session: DialogSession):
		self.endDialog(session.sessionId, text=self.TalkManager.randomTalk('offline', module='system'))


	@online(offlineHandler=offlineHandler)
	def convertCurrency(self, session: DialogSession) -> str:
		siteId = session.siteId
		slotsObject = session.slotsAsObjects
		sessionId = session.sessionId
		customData = session.customData

		amount, toCurrency, fromCurrency = self.extractSlotValues(slotsObject, customData)
		if not fromCurrency:
			self.continueDialog(
				sessionId=sessionId,
				intentFilter=[self._INTENT_ANSWER_CURRENCY],
				text=self.TalkManager.randomTalk(module=self.name, talk='fromWhatCurrency'),
				previousIntent=self._INTENT_CONVERT_CURRENCY,
				customData={
					'module'    : self.name,
					'amount'    : amount,
					'toCurrency': toCurrency
				}
			)
			return

		url = f'https://free.currconv.com/api/v7/convert?q={fromCurrency}_{toCurrency}&compact=ultra&apiKey={self._apiKey}'
		data = requests.get(url=url).json()

		conversion = data[f'{fromCurrency}_{toCurrency}']
		converted = round(float(amount) * float(conversion), 2)

		self.endDialog(
			sessionId=sessionId,
			text=self.randomTalk('answer').format(amount, fromCurrency, converted, toCurrency),
			siteId=session.siteId)
