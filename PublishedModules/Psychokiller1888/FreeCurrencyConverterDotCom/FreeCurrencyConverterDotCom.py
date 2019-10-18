import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons.commons import online


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
		
		self._apiKey = self.getConfig('apiKey')
		super().__init__(self._SUPPORTED_INTENTS)


	@online
	def convertCurrencyIntent(self, session: DialogSession, **_kwargs):
		amount = session.slots.get('Amount', session.customData.get('Amount', 1))

		toCurrency = session.slots.get('ToCurrency',
			session.customData.get('toCurrency',
			self.ConfigManager.getAliceConfigByName('baseCurrency', self.name)))

		fromCurrency = session.slots.get('FromCurrency', session.slots.get('Currency'))
		if not fromCurrency:
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

		try:
			url = f'https://free.currconv.com/api/v7/convert?q={fromCurrency}_{toCurrency}&compact=ultra&apiKey={self._apiKey}'
			data = requests.get(url=url).json()

			conversion = data[f'{fromCurrency}_{toCurrency}']
			converted = round(float(amount) * float(conversion), 2)

			self.endDialog(session.sessionId, text=self.randomTalk('answer').format(amount, fromCurrency, converted, toCurrency))
		except Exception as e:
			self._logger.error(e)
			self.endDialog(session.sessionId, text=self.randomTalk('noServer'))
