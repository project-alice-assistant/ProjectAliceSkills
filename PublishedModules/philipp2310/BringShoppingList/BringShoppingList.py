from typing import Tuple, Callable
from BringApi.BringApi import BringApi

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import commons, online
from core.dialog.model.DialogSession import DialogSession
from core.base.SuperManager import SuperManager


class BringShoppingList(Module):
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
		self._SUPPORTED_INTENTS = [
			self._INTENT_ADD_ITEM,
			self._INTENT_DEL_ITEM,
			self._INTENT_READ_LIST,
			self._INTENT_CHECK_LIST,
			self._INTENT_DEL_LIST,
			self._INTENT_CONF_DEL,
			self._INTENT_ANSWER_SHOP,
			self._INTENT_SPELL_WORD]

		super().__init__(self._SUPPORTED_INTENTS)

		# Get config values
		self._uuid = self.getConfig('uuid')
		self._uuidlist = self.getConfig('bringListUUID')


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		"""handle all incoming messages"""
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_ADD_ITEM or (intent in {self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD} and session.previousIntent == self._INTENT_ADD_ITEM):
			#Add item to list
			self.editList(session, intent, 'add', self._addItemInt)
		elif intent == self._INTENT_DEL_ITEM or (intent in {self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD} and session.previousIntent == self._INTENT_DEL_ITEM):
			#Delete items from list
			self.editList(session, intent, 'rem', self._deleteItemInt)
		elif intent == self._INTENT_READ_LIST:
			self.endDialog(session.sessionId, text=self.readList())
		elif intent == self._INTENT_CHECK_LIST or (intent in {self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD} and session.previousIntent == self._INTENT_CHECK_LIST):
			#check if item is in list
			self.editList(session, intent, 'chk', self._checkListInt)
		elif intent == self._INTENT_DEL_LIST:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('chk_del_all'),
				intentFilter=[self._INTENT_CONF_DEL],
				previousIntent=self._INTENT_DEL_LIST)
		elif session.previousIntent == self._INTENT_DEL_LIST and intent == self._INTENT_CONF_DEL:
			if commons.isYes(session):
				self.endDialog(session.sessionId, text=self.deleteCompleteList())
			else:
				self.endDialog(session.sessionId, text=self.randomTalk('nodel_all'))

		return True


	def _getBring(self) -> BringApi:
		"""get an instance of the BringApi"""
		return BringApi(self._uuid, self._uuidlist)

	def _addItemInt(self, items) -> Tuple[list, list]:
		"""
		internal method to add a list of items to the shopping list
		:returns: two splitted lists of successfull adds and items that already existed.
		"""
		bringItems = self._getBring().get_items().json()['purchase']
		added = list()
		exist = list()
		for item in items:
			if not any(entr['name'].lower() == item.lower() for entr in bringItems):
				self._getBring().purchase_item(item, "")
				added.append(item)
			else:
				exist.append(item)
		return added, exist


	def _deleteItemInt(self, items: list) -> Tuple[list, list]:
		"""
		internal method to delete a list of items from the shopping list
		:returns: two splitted lists of successfull deletions and items that were not on the list
		"""
		bringItems = self._getBring().get_items().json()['purchase']
		removed = list()
		exist = list()
		for item in items:
			for entr in bringItems:
				if entr['name'].lower() == item.lower():
					self._getBring().recent_item(entr['name'])
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
		bringItems = self._getBring().get_items().json()['purchase']
		found = list()
		missing = list()
		for item in items:
			if any(entr['name'].lower() == item.lower() for entr in bringItems):
				found.append(item)
			else:
				missing.append(item)
		return found, missing


	def _getShopItems(self, session: DialogSession, intent: str) -> list:
		"""get the values of shopItem as a list of strings"""
		items = list()
		if intent == self._INTENT_SPELL_WORD:
			item = ''.join([slot.value['value'] for slot in session.slotsAsObjects['Letters']])
			items.append(item.capitalize())
		else:
			if 'shopItem' in session.slots:
				for x in session.slotsAsObjects['shopItem']:
					if x.value['value'] != "unknownword":
						items.append(x.value['value'])
		return items


	def _offlineHandler(self, session: DialogSession, *args, **kwargs):
		self.endDialog(session.sessionId, text=SuperManager.getInstance().talkManager.randomTalk('offline', module='system'))


	### INTENTS ###
	@online(offlineHandler=_offlineHandler)
	def editList(self, session: DialogSession, intent: str, answer: str, action: Callable[[list], Tuple[list, list]]):
		items = self._getShopItems(session, intent)
		if items:
			successfull, failed = action(items)
			self.endDialog(session.sessionId, text=self._combineLists(answer, successfull, failed))
		else:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(f'{answer}_what'),
				intentFilter=[self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD],
				previousIntent=intent)


	@online
	def readList(self):
		"""read the content of the list"""
		items = self._getBring().get_items().json()['purchase']
		itemlist = [item['name'] for item in items]
		return self._getTextForList('read', itemlist)


	@online
	def deleteCompleteList(self) -> str:
		"""
		perform the deletion of the complete list
		-> load all and delete item by item
		"""
		items = self._getBring().get_items().json()['purchase']
		for item in items:
			self._getBring().recent_item(item['name'])
		return self.randomTalk('del_all')


	#### List/Text operations
	def _combineLists(self, answer: str, first: list, second: list) -> str:
		"""
		Combines two lists(if filled)
		first+CONN+second
		first
		second
		"""
		strout = ''
		if first:
			strout = self._getTextForList(answer, first)

		if second:
			backup = strout  # don't overwrite added list... even if empty!
			strout = self._getTextForList(f'{answer}_f', second)

		if first and second:
			strout = self.randomTalk('state_con', [backup, strout])

		return strout


	def _getTextForList(self, pref: str, items: list) -> str:
		"""Combine entries of list into wrapper sentence"""
		if not items:
			return self.randomTalk(f'{pref}_none')
		if len(items) == 1:
			return self.randomTalk(f'{pref}_one', [items[0]])

		value = self.randomTalk('gen_list', ['", "'.join(items[:-1]), items[-1]])
		return self.randomTalk(f'{pref}_multi', [value])
