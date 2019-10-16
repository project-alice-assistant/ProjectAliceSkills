import json

import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
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
			(self._INTENT_ANSWER_CURRENCY, self.convertCurrencyIntent),
			(self._INTENT_CONVERT_CURRENCY, self.convertCurrencyIntent),
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def convertCurrencyIntent(self, session: DialogSession, **_kwargs):
		amount = 1
		if 'Amount' in session.slots:
			amount = session.slotsAsObjects['Amount'][0].value['value']
		elif 'amount' in session.customData:
			amount = session.customData['Amount']

		toCurrency = self.ConfigManager.getAliceConfigByName('baseCurrency', self.name)
		if 'ToCurrency' in session.slotsAsObjects:
			toCurrency = session.slotsAsObjects['ToCurrency'][0].value['value']
		elif 'toCurrency' in session.customData:
			toCurrency = session.customData['toCurrency']

		if 'FromCurrency' not in session.slots:
			if 'Currency' in session.slots:
				fromCurrency = session.slotsAsObjects['Currency'][0].value['value']
			else:
				self.continueDialog(
					sessionId=session.sessionId,
					intentFilter=[self._INTENT_ANSWER_CURRENCY],
					text=self.TalkManager.randomTalk(module=self.name, talk='fromWhatCurrency'),
					customData={
						'module'    : self.name,
						'amount'    : amount,
						'toCurrency': toCurrency
					}
				)
				return
		else:
			fromCurrency = session.slotsAsObjects['FromCurrency'][0].value['value']

		try:
			url = f"https://free.currconv.com/api/v7/convert?q={fromCurrency}_{toCurrency}&compact=ultra&apiKey={self.getConfig('apiKey')}"
			req = requests.get(url=url)
			data = json.loads(req.content.decode())

			conversion = data[f'{fromCurrency}_{toCurrency}']
			converted = round(float(amount) * float(conversion), 2)

			self.endDialog(session.sessionId, text=self.randomTalk('answer').format(amount, fromCurrency, converted, toCurrency), siteId=session.siteId)
		except Exception as e:
			self._logger.error(e)
			self.endDialog(session.sessionId, text=self.randomTalk('noServer'), siteId=session.siteId)
