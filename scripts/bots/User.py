# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
# import GameConfigs

class User(KBEngine.Entity):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		DEBUG_MSG("User::__init__:%s." % (self.__dict__))
		self._data = {}

	def onEnterSpace(self):
		"""
		KBEngine method.
		这个entity进入了一个新的space
		"""
		DEBUG_MSG("%s::onEnterSpace: %i" % (self.className, self.id))

	def onLeaveSpace(self):
		"""
		KBEngine method.
		这个entity将要离开当前space
		"""
		DEBUG_MSG("%s::onLeaveSpace: %i" % (self.className, self.id))
		
	def onBecomePlayer( self ):
		"""
		KBEngine method.
		当这个entity被引擎定义为角色时被调用
		"""
		DEBUG_MSG("%s::onBecomePlayer: %i" % (self.className, self.id))
	
	def update(self):
		pass

	@property
	def room(self):
		for e in self.clientapp.entities.values():
			if e.className == 'Room':
				return e
	@property
	def game(self):
		for e in self.clientapp.entities.values():
			if e.className == 'GameNN':
				return e
			

			
	
	def onMsgTips(self, *args):
		self._data['onMsgTips'] = args
	def onDebugCmd(self, *args):
		self._data['onDebugCmd'] = args
	def onGotRoomIDs(self, *args):
		self._data['onGotRoomIDs'] = args
	def onEnterRoom(self, *args):
		self._data['onEnterRoom'] = args
	def onRoomPlayerChat(self, *args):
		self._data['onRoomPlayerChat'] = args
	def onGameNNOwnerPoker(self, *args):
		self._data['onGameNNOwnerPoker'] = args
	def onGameNNYazhuAble(self, *args):
		self._data['onGameNNYazhuAble'] = args
	def cardTypeValue(self, *args):
		self._data['cardTypeValue'] = args
	def onStartGameMemo(self, *args):
		self._data['onStartGameMemo'] = args
	def onGotGameMemo(self, *args):
		self._data['onGotGameMemo'] = args
	def onGotMatchInfos(self, *args):
		self._data['onGotMatchInfos'] = args
	def onGotUserinfo(self, *args):
		self._data['onGotUserinfo'] = args
	def onGotSaveinfo(self, *args):
		self._data['onGotSaveinfo'] = args
	def onTextTip(self, *args):
		self._data['onTextTip'] = args
	def onAlterPassword(self, *args):
		self._data['onAlterPassword'] = args
	def onGotLoginInfo(self, *args):
		self._data['onGotLoginInfo'] = args
	def onChargeMemo(self, *args):
		self._data['onChargeMemo'] = args
	def onGoldRank(self, *args):
		self._data['onGoldRank'] = args
	def gameNN_fapai(self, *args):
		self._data['gameNN_fapai'] = args
	def onChargeOrder(self, *args):
		self._data['onChargeOrder'] = args
	def onGotChargeResult(self, *args):
		self._data['onGotChargeResult'] = args
	def onRecvHudong(self, *args):
		self._data['onRecvHudong'] = args
	def reqBindBankCard(self, *args):
		self._data['reqBindBankCard'] = args
	def reqGoldDrawMemo(self, *args):
		self._data['reqGoldDrawMemo'] = args
	def reqGoldDraw(self, *args):
		self._data['reqGoldDraw'] = args
	def reqChangeGoldPass(self, *args):
		self._data['reqChangeGoldPass'] = args
	def onGetLoginMemo(self, *args):
		self._data['onGetLoginMemo'] = args
	def onGotChargeUrl(self, *args):
		self._data['onGotChargeUrl'] = args
	def reqUnlockHead(self, *args):
		self._data['reqUnlockHead'] = args
	def reqChangeFace(self, *args):
		self._data['reqChangeFace'] = args

		
class PlayerUser(User):
	def __init__(self):
		pass

	def onBecomePlayer( self ):
		"""
		KBEngine method.
		当这个entity被引擎定义为角色时被调用
		"""
		DEBUG_MSG("%s::onBecomePlayer: %i" % (self.className, self.id))

	def onEnterSpace(self):
		"""
		KBEngine method.
		这个entity进入了一个新的space
		"""
		DEBUG_MSG("%s::onEnterSpace: %i" % (self.className, self.id))
		
		# 注意：由于PlayerAvatar是引擎底层强制由Avatar转换过来，__init__并不会再调用
		# 这里手动进行初始化一下
		self.__init__()
		
	def onLeaveSpace(self):
		"""
		KBEngine method.
		这个entity将要离开当前space
		"""
		DEBUG_MSG("%s::onLeaveSpace: %i" % (self.className, self.id))

	def update(self):
		DEBUG_MSG("%s::update: %i" % (self.className, self.id))
		if self.isDestroyed:
			return

		# KBEngine.callback(GameConfigs.BOTS_UPDATE_TIME, self.update)
		
