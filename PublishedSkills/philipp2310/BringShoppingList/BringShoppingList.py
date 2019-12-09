from typing import Tuple

from BringApi.BringApi import BringApi

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import AnyExcept, Online


class BringShoppingList(AliceSkill):
	"""
	Author: philipp2310
	Description: maintaines a Bring! shopping list
	"""

	### Intents
	_INTENT_ADD_ITEM = Intent('addItem_bringshop')
	_INTENT_DEL_ITEM = Intent('deleteItem_bringshop')
	_INTENT_READ_LIST = Intent('readList_bringshop')
	_INTENT_CHECK_LIST = Intent('checkList_bringshop', isProtected=True)
	_INTENT_DEL_LIST = Intent('deleteList_bringshop')
	_INTENT_CONF_DEL = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_SHOP = Intent('whatItem_bringshop', isProtected=True)
	_INTENT_SPELL_WORD = Intent('SpellWord', isProtected=True)


	def __init__(self):
		self._INTENTS = [
			(self._INTENT_ADD_ITEM, self.addItemIntent),
			(self._INTENT_DEL_ITEM, self.delItemIntent),
			(self._INTENT_CHECK_LIST, self.checkListIntent),
			(self._INTENT_READ_LIST, self.readListIntent),
			(self._INTENT_DEL_LIST, self.delListIntent),
			self._INTENT_CONF_DEL,
			self._INTENT_ANSWER_SHOP,
			self._INTENT_SPELL_WORD
		]

		super().__init__(self._INTENTS)

		self._INTENT_ANSWER_SHOP.dialogMapping = {
			self._INTENT_ADD_ITEM: self.addItemIntent,
			self._INTENT_DEL_ITEM: self.delItemIntent,
			self._INTENT_CHECK_LIST: self.checkListIntent
		}

		self._INTENT_SPELL_WORD.dialogMapping = {
			self._INTENT_ADD_ITEM: self.addItemIntent,
			self._INTENT_DEL_ITEM: self.delItemIntent,
			self._INTENT_CHECK_LIST: self.checkListIntent
		}

		self._INTENT_CONF_DEL.dialogMapping = {
			'confDelList': self.confDelIntent
		}

		self._uuid = self.getConfig('uuid')
		self._uuidlist = self.getConfig('listUuid')
		self._bring = None


	def onStart(self):
		super().onStart()
		self._connectAccount()
		return self.supportedIntents


	def bring(self):
		if not self._bring:
			if not self._uuid or not self._uuidlist:
				self._uuid, self._uuidlist = BringApi.login(self.getConfig('bringEmail'), self.getConfig('bringPassword'))
				self.updateConfig('uuid', self._uuid)
				self.updateConfig('listUuid', self._uuidlist)

			self._bring = BringApi(self._uuid, self._uuidlist)
		return self._bring


	@Online
	def _connectAccount(self):
		try:
			self._bring = self.bring()
		except BringApi.AuthentificationFailed:
			raise SkillStartingFailed(self._name, 'Please check your account login and password')


	def _deleteCompleteList(self):
		"""
		perform the deletion of the complete list
		-> load all and delete item by item
		"""
		items = self.bring().get_items().json()['purchase']
		for item in items:
			self.bring().recent_item(item['name'])


	def _addItemInt(self, items) -> Tuple[list, list]:
		"""
		internal method to add a list of items to the shopping list
		:returns: two splitted lists of successfull adds and items that already existed.
		"""
		bringItems = self.bring().get_items().json()['purchase']
		added = list()
		exist = list()
		for item in items:
			if not any(entr['name'].lower() == item.lower() for entr in bringItems):
				self.bring().purchase_item(item, "")
				added.append(item)
			else:
				exist.append(item)
		return added, exist


	def _deleteItemInt(self, items: list) -> Tuple[list, list]:
		"""
		internal method to delete a list of items from the shopping list
		:returns: two splitted lists of successfull deletions and items that were not on the list
		"""
		bringItems = self.bring().get_items().json()['purchase']
		removed = list()
		exist = list()
		for item in items:
			for entr in bringItems:
				if entr['name'].lower() == item.lower():
					self.bring().recent_item(entr['name'])
					removed.append(item)
					break
			else:
				exist.append(item)
		return removed, exist


	def _checkListInt(self, items: list) -> Tuple[list, list]:
		"""
		internal method to check if a list of items is on the shopping list
		:returns: two splitted lists, one with the items on the list, one with the missing ones
		"""
		bringItems = self.bring().get_items().json()['purchase']
		found = list()
		missing = list()
		for item in items:
			if any(entr['name'].lower() == item.lower() for entr in bringItems):
				found.append(item)
			else:
				missing.append(item)
		return found, missing


	def _getShopItems(self, answer: str, intent: str, session: DialogSession) -> list:
		"""get the values of shopItem as a list of strings"""
		if intent == self._INTENT_SPELL_WORD:
			item = ''.join([slot.value['value'] for slot in session.slotsAsObjects['Letters']])
			return [item.capitalize()]

		items = [x.value['value'] for x in session.slotsAsObjects.get('shopItem', list()) if x.value['value'] != "unknownword"]

		if not items:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(f'{answer}_what'),
				intentFilter=[self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD],
				currentDialogState=intent)
		return items


	### INTENTS ###
	def delListIntent(self, session: DialogSession):
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('chk_del_all'),
			intentFilter=[self._INTENT_CONF_DEL],
			currentDialogState='confDelList')


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	def confDelIntent(self, session: DialogSession):
		if self.Commons.isYes(session):
			self._deleteCompleteList()
			self.endDialog(session.sessionId, text=self.randomTalk('del_all'))
		else:
			self.endDialog(session.sessionId, text=self.randomTalk('nodel_all'))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	def addItemIntent(self, intent: str, session: DialogSession):
		items = self._getShopItems('add', intent, session)
		if items:
			added, exist = self._addItemInt(items)
			self.endDialog(session.sessionId, text=self._combineLists('add', added, exist))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	def delItemIntent(self, intent: str, session: DialogSession):
		items = self._getShopItems('rem', intent, session)
		if items:
			removed, exist = self._deleteItemInt(items)
			self.endDialog(session.sessionId, text=self._combineLists('rem', removed, exist))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	def checkListIntent(self, intent: str, session: DialogSession):
		items = self._getShopItems('chk', intent, session)
		if items:
			found, missing = self._checkListInt(items)
			self.endDialog(session.sessionId, text=self._combineLists('chk', found, missing))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	def readListIntent(self, session: DialogSession):
		"""read the content of the list"""
		items = self.bring().get_items().json()['purchase']
		itemlist = [item['name'] for item in items]
		self.endDialog(session.sessionId, text=self._getTextForList('read', itemlist))


	#### List/Text operations
	def _combineLists(self, answer: str, first: list, second: list) -> str:
		firstAnswer = self._getTextForList(answer, first) if first else ''
		secondAnswer = self._getTextForList(f'{answer}_f', second) if second else ''
		combinedAnswer = self.randomTalk('state_con', [firstAnswer, secondAnswer]) if first and second else ''

		return combinedAnswer or firstAnswer or secondAnswer


	def _getTextForList(self, pref: str, items: list) -> str:
		"""Combine entries of list into wrapper sentence"""
		if not items:
			return self.randomTalk(f'{pref}_none')
		elif len(items) == 1:
			return self.randomTalk(f'{pref}_one', [items[0]])

		value = self.randomTalk(text='gen_list', replace=[', '.join(items[:-1]), items[-1]])
		return self.randomTalk(f'{pref}_multi', [value])
