#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import core.base.Managers as managers
from BringApi.BringApi import BringApi
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons import commons
from typing import Tuple


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
    _INTENT_CONF_DEL = Intent('confDelList_bringshop', isProtected=True)
    _INTENT_ANSWER_SHOP = Intent('whatItem_bringshop', isProtected=True)
    _INTENT_SPELL_WORD = Intent('SpellWord', isProtected=True)

    def __init__(self):
        self._SUPPORTED_INTENTS = [ self._INTENT_ADD_ITEM,
                                    self._INTENT_DEL_ITEM,
                                    self._INTENT_READ_LIST,
                                    self._INTENT_CHECK_LIST,
                                    self._INTENT_DEL_LIST,
                                    self._INTENT_CONF_DEL,
                                    self._INTENT_ANSWER_SHOP,
                                    self._INTENT_SPELL_WORD ]

        super().__init__(self._SUPPORTED_INTENTS)
        
        # Get config values
        self._uuid = self.getConfig('uuid')
        self._uuidlist = self.getConfig('bringListUUID')


    # handle all incoming messages
    def onMessage(self, intent: str, session: DialogSession) -> bool:
        if not self.filterIntent(intent, session):
            return False
        
        if intent == self._INTENT_ADD_ITEM or ( intent in (self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD) and session.previousIntent == self._INTENT_ADD_ITEM ):
            self.addItem(session, intent)
        elif intent == self._INTENT_DEL_ITEM or ( intent in (self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD) and session.previousIntent == self._INTENT_DEL_ITEM ):
            self.deleteItem(session, intent)
        elif intent == self._INTENT_READ_LIST:
            self.readList(session)
        elif intent == self._INTENT_CHECK_LIST or ( intent in (self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD) and session.previousIntent == self._INTENT_CHECK_LIST ):
            self.checkList(session, intent)
        elif intent == self._INTENT_DEL_LIST:
            self.continueDialog( sessionId=session.sessionId,
                                                text=self.randomTalk('chk_del_all'),
                                                intentFilter=[self._INTENT_CONF_DEL],
                                                previousIntent=self._INTENT_DEL_LIST)
        elif session.previousIntent == self._INTENT_DEL_LIST and intent == self._INTENT_CONF_DEL:
            if commons.isYes(session):
                self.endDialog(session.sessionId, self._deleteCompleteList())
            else:
                self.endDialog(session.sessionId, text=self.randomTalk('nodel_all'))

        return True


    # get an instance of the BringApi
    def _getBring(self) -> BringApi:
        return BringApi(self._uuid,self._uuidlist)
    
    
    # perform the deletion of the complete list
    # -> load all and delete item by item
    def _deleteCompleteList(self) -> str:
        items = self._getBring().get_items().json()['purchase']
        for item in items:
            self._getBring().recent_item(item['name'])
        return self.randomTalk('del_all')
    
    
    # internal method to add a list of items to the shopping list
    # returns two splitted lists of successfull adds and items that already existed.
    def _addItemInt(self, items) -> Tuple[list, list]:
        bringItems = self._getBring().get_items().json()['purchase']
        added = list()
        exist = list()
        for item in items:
            if not any(entr['name'] == item for entr in bringItems):
                self._getBring().purchase_item(item, "")
                added.append(item)
            else:
                exist.append(item)
        return added, exist
    
    
    # internal method to delete a list of items from the shopping list
    # returns two splitted lists of successfull deletions and items that were not on the list
    def _deleteItemInt(self, items) -> Tuple[list, list]:
        bringItems = self._getBring().get_items().json()['purchase']
        removed = list()
        exist = list()
        for item in items:
            if any(entr['name'].lower() == item.lower() for entr in bringItems):
                self._getBring().recent_item(item)
                removed.append(item)
            else:
                exist.append(item)
        return removed, exist
    
    # internal method to check if a list of items is on the shopping list
    # returns two splitted lists, one with the items on the list, one with the missing ones
    def _checkListInt(self, check) -> Tuple[list, list]:
        bringItems = self._getBring().get_items().json()['purchase']
        found = list()
        missing = list()
        for c in check:
            if any(c == entr['name'] for entr in bringItems):
                found.append(c)
            else:
                missing.append(c)
        return found, missing
    
    
    # get the values of shopItem as a list of strings
    def _getShopItems(self, session, intent) -> list:
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
    
    
    ### INTENTS ###
    ## Add item to list
    def addItem(self, session, intent) -> bool:
        items = self._getShopItems(session, intent)
        if len(items) > 0:
            added, exist = self._addItemInt(items)
            self.endDialog(session.sessionId, self._combineLists('add', 'state_con', 'end', 'add_f', added, exist))
        else:
            self.continueDialog(
                    sessionId=session.sessionId,
                    text=self.randomTalk('add_what'),
                    intentFilter=[self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD],
                    previousIntent=self._INTENT_ADD_ITEM)
        return True
        
        
    ## Delete items from list
    def deleteItem(self, session, intent) -> bool:
        items = self._getShopItems(session, intent)
        if len(items) > 0:
            removed, failed = self._deleteItemInt(items)
            self.endDialog(session.sessionId, self._combineLists('rem', 'state_con', 'end', 'rem_f', removed, failed))
        else:
            self.continueDialog(
                    sessionId=session.sessionId,
                    text=self.randomTalk('del_what'),
                    intentFilter=[self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD],
                    previousIntent=self._INTENT_DEL_ITEM)
        return True
    
    
    ## check if item is in list
    def checkList(self, session, intent) -> bool:
        items = self._getShopItems(session, intent)
        if len(items) > 0:
            found, missing = self._checkListInt(items)
            self.endDialog(session.sessionId, self._combineLists('chk', 'state_con', 'end', 'chk_f', found, missing))
        else:
            self.continueDialog(
                    sessionId=session.sessionId,
                    text=self.randomTalk('chk_what'),
                    intentFilter=[self._INTENT_ANSWER_SHOP, self._INTENT_SPELL_WORD],
                    previousIntent=self._INTENT_CHECK_LIST)
        return True
    
    
    ## read the content of the list
    def readList(self, session) -> bool:
        items = self._getBring().get_items().json()['purchase']
        itemlist = [ l['name'] for l in items ]
        self.endDialog(session.sessionId, self._getTextForList('read', itemlist))
        return True
    
    
    #### List/Text operations
    ### Combines two lists(if filled)
    # first+CONN+second
    # first
    # second
    def _combineLists(self, str_first: str, str_conn: str, str_end: str, str_second: str, first: list, second: list) -> str:
        strout = ""
        if first:
            strout = self._getTextForList(str_first, first)
        if second:
            backup = strout # don't overwrite added list... even if empty!
            strout = self._getTextForList(str_second,second)
        
        if first and second:
            strout = self.randomTalk('state_con', [backup, strout])
        return strout
    
    ### Combine entries of list into wrapper sentence
    def _getTextForList(self, pref: str, l1: list) -> str:
        category, strout = self._getDefaultList(l1)
        return self.randomTalk(pref+'_'+category, [strout])
    
    ### Return if MULTI or ONE entry and creates list for multi ( XXX, XXX and XXX )
    def _getDefaultList(self, items: list) -> Tuple[str, str]:
        if len(items) > 1:
            return "multi", self.randomTalk('gen_list', [", ".join(items[:-1]), items[-1]])
        elif len(items) == 1:
            return "one", items[0]
        else:
            return "none", ""
