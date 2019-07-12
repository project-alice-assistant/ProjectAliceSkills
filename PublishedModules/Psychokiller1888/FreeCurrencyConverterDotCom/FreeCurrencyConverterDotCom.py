# -*- coding: utf-8 -*-

import json

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
import requests


class FreeCurrencyConverterDotCom(Module):
    """
    Author: Psychokiller1888
    Description: Let's you convert world currencies
    """

    _INTENT_CONVERT_CURRENCY     = Intent('ConvertCurrency')
    _INTENT_ANSWER_CURRENCY        = Intent('AnswerCurrency', isProtected=True)

    def __init__(self):
        self._SUPPORTED_INTENTS    = [
            self._INTENT_ANSWER_CURRENCY,
            self._INTENT_CONVERT_CURRENCY
        ]

        super().__init__(self._SUPPORTED_INTENTS)


    def onMessage(self, intent: str, session: DialogSession) -> bool:
        if not self.filterIntent(intent, session):
            return False

        siteId = session.siteId
        slots = session.slots
        slotsObject = session.slotsAsObjects
        sessionId = session.sessionId
        customData = session.customData

        if intent == self._INTENT_CONVERT_CURRENCY or session.previousIntent == self._INTENT_CONVERT_CURRENCY:
            amount = 1
            if 'Amount' in slots:
                amount = slotsObject['Amount'][0].value['value']
            elif 'amount' in customData:
                amount = customData['Amount']

            toCurrency = managers.ConfigManager.getAliceConfigByName('baseCurrency', self.name)
            if 'ToCurrency' in slotsObject:
                toCurrency = slotsObject['ToCurrency'][0].value['value']
            elif 'toCurrency' in customData:
                toCurrency = customData['toCurrency']

            if 'FromCurrency' not in slots:
                if 'Currency' in slots:
                    fromCurrency = slotsObject['Currency'][0].value['value']
                else:
                    managers.MqttServer.continueDialog(
                        sessionId = sessionId,
                        intentFilter = [self._INTENT_ANSWER_CURRENCY],
                        text = managers.TalkManager.randomTalk(module=self.name, talk='fromWhatCurrency'),
                        previousIntent = self._INTENT_CONVERT_CURRENCY,
                        customData = json.dumps({
                            'module': self.name,
                            'amount': amount,
                            'toCurrency': toCurrency
                        })
                    )
                    return True
            else:
                fromCurrency = slotsObject['FromCurrency'][0].value['value']

            try:
                url = 'https://free.currconv.com/api/v7/convert?q={}_{}&compact=ultra&apiKey={}'.format(fromCurrency, toCurrency, managers.ConfigManager.getModuleConfigByName(self.name, 'apiKey'))
                req = requests.get(url = url)
                data = json.loads(req.content.decode())

                conversion = data['{}_{}'.format(fromCurrency, toCurrency)]
                converted = round(float(amount) * float(conversion), 2)

                managers.MqttServer.endTalk(sessionId,
                                            text=managers.TalkManager.randomTalk(module=self.name, talk='answer').format(amount, fromCurrency, converted, toCurrency),
                                            client=siteId)
            except Exception as e:
                self._logger.error(e)
                managers.MqttServer.endTalk(sessionId,
                                            text=managers.TalkManager.randomTalk(module=self.name, talk='noServer'),
                                            client=siteId)

        return True
