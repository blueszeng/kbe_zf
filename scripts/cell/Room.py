#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import KBEngine
from KBEDebug import *
from Functor import *
from enumDef import RoomState
import d_game
import KbeCallback

''' 游戏名列举 '''
ALL_GAMES = (
	'GameNN',
)

AREA = 100.0

class Room(KBEngine.Entity):
	''' 房间, 负责管理空间和其他 entity '''
	def __init__(self):
		KBEngine.Entity.__init__(self)
		KbeCallback.KbeCallback.__init__(self)

		self.gameName = None
		self.gameLevel = None
		self._game = None
		# self.base.setRoomState(RoomState.noReady)

	@property
	def game(self):
		return self._game

	def resetGame(self):
		''' 初始化 game 相关 entity '''
		assert self.gameName in ALL_GAMES
		if getattr(self, '_game', None):
			self._game.destroy()
		posInfo = (self.spaceID, self.position, self.direction, {'roomID':self.id,'gameLevel':self.gameLevel})
		self._game = KBEngine.createEntity( self.gameName, *posInfo )
		self.gameID = self._game.id

		# self.base.setRoomState(RoomState.waiting)
		self.doMatch(True)
		self._game.reset()

	def doMatch(self, isMatch):
		if isMatch:
			KBEngine.globalData["Hall"].doMatchByRoom(self, self.gameName, self.gameLevel)
		else:
			KBEngine.globalData["Hall"].doCancelMatch(self.id)

	def reqCreateGame(self, gameName, gameLevel):
		assert self._game == None
		self.gameName = gameName
		self.gameLevel = gameLevel
		self.resetGame()
		KBEngine.globalData["Hall"].onGameCreated(self.gameID)

	def isGoldEnough(self, gold):
		''' 金币是否足够 '''
		return d_game.get_gold_limit(self.gameName, self.gameLevel) <= gold


	def doUserEnter(self, usermb, gold):
		''' user 请求进入 '''
		if not self.game._canJoinGame():
			return logi('doUserEnter', '_canJoinGame')
		if not self.isGoldEnough(gold):
			return logi('doUserEnter', 'isGoldEnough')
		if usermb.spaceID != self.spaceID:
			usermb.reqTeleport(self.id, self)
			return
		if entity.position.x != self.position.x:
			entity.position.x = self.position.x
			entity.position.y = self.position.y


	def doUserLeave(self, user):
		if not isinstance(user, KBEngine.Entity):
			user = KBEngine.entities.get(user)
		if user and not user.isDestroyed:
			user.position.x = AREA*user.id


	def onUserEnter(self, eid):
		''' user 进入回调通知 '''
		print('onUserEnter', eid)

	def onGameStarted(self):
		# self.base.setRoomState(RoomState.gaming)
		self.doMatch(False)

	def onGameOvered(self):
		# self.base.setRoomState(RoomState.waiting)
		self.doMatch(True)




def test_newRoom():
	''' 创建房间 '''
	return KBEngine.globalData["Hall"].reqCreateRoom(1)
