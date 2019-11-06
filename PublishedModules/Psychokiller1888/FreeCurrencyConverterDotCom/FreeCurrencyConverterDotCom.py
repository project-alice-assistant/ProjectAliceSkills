import requests
from requests.exceptions import RequestException

from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators


class FreeCurrencyConverterDotCom(Module):
	"""
	Author: Psychokiller1888
	Description: Let's you convert world currencies
	"""

	def __init__(self):
		self._apiKey = self.getConfig('apiKey')
		super().__init__()


	@Decorators.Intent('ConvertCurrency')
	@Decorators.Intent('AnswerCurrency', isProtected=True)
	@Decorators.anyExcept(exceptions=(RequestException, KeyError), text='noServer', printStack=True)
	@Decorators.online
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

		if not self._apiKey:
			self.logWarning(msg="please create a api key at https://www.currencyconverterapi.com/ and add it to the module config")
			self.endDialog(session.sessionId, text=self.randomTalk('noApiKey'))
			return

		url = f'https://free.currconv.com/api/v7/convert?q={fromCurrency}_{toCurrency}&compact=ultra&apiKey={self._apiKey}'
		response = requests.get(url=url)
		response.raise_for_status()
		data = response.json()

		conversion = data[f'{fromCurrency}_{toCurrency}']
		converted = round(float(amount) * float(conversion), 2)

		self.endDialog(session.sessionId, text=self.randomTalk('answer').format(amount, fromCurrency, converted, toCurrency))
