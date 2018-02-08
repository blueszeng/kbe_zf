#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import KBEngine
from KBEDebug import *
from Functor import *

import random
import importlib
import d_game
from Callbacks import supports_callbacks
from echo import callback_property


def newGame(entity):
	return KBEngine.createEntity( 'Game', entity.spaceID, entity.position, entity.direction)


def is_seatedPlayer(player):
	''' 座位是否已经有玩家 '''
	return player.userID > 0


''' 税收比例配置 '''
TAX_RATE = [
	1, 0.6, 0.35, 0.2
]

def get_tax_rate(gameLevel):
	''' 得到税收比例 '''
	return TAX_RATE[gameLevel]


class Game(KBEngine.Entity):
	''' 游戏基类 '''
	def __init__(self):
		KBEngine.Entity.__init__(self)
		self._players = {}
		self.initPlayers()

	def reset(self):
		try:
			self.onReset()
		except Exception:
			raise Warning('reset')
		

	def onReset(self):
		raise Warning('onReset')


	@property
	def _playerClsName(self):
		''' 抽象属性, 游戏玩家类名 '''
		return 'GamePlayer'

	@property
	def _maxSeat(self):
		''' 抽象属性, 最大座位号 '''
		return 1

	@property
	def players(self):
		''' 只读，并且避免原容器被修改 '''
		for player in self._players.values():
			yield player

	@property
	def maxUserCount(self):
		''' 最大用户数量 '''
		return self._maxSeat

	def startGame(self):
		''' 开始游戏，userID 存在的为游戏玩家 '''
		self._gameSeats = []
		for player in self.seatedPlayers:
			player.doTaxGold(self.getTaxGold())
			player.doStartGame()
			self._gameSeats.append(player.seat)
		self.onStart(self._gameSeats)
		return self._gameSeats


	@property
	def room(self):
		if self.roomID:
			return KBEngine.entities.get(self.roomID)


	@property
	def seatedPlayers(self):
		''' 已经坐下的玩家 '''
		for player in self.players:
			if is_seatedPlayer(player):
				yield player


	def onStart(self, gameSeats=None):
		raise Warning('onStart')


	def initPlayers(self):
		for seat in range(0, self._maxSeat):
			if not self._players.get(seat):
				info = {'gameID':self.id, 'seat': seat, 'roomID':self.roomID}
				entity = KBEngine.createEntity(self._playerClsName, self.spaceID, self.position, self.direction, info)
				self._players[seat] = entity
				self.placeEntity(entity)

	def placeEntity(self, entity):
		assert entity.spaceID == self.spaceID, 'entity outside this space'
		entity.position.x = self.position.x
		entity.position.y = self.position.y


	def onDestroy(self):
		for player in self.players:
			player.destroy()


	def onUserEnterRoom(self, userID):
		''' 玩家进入房间回调 '''
		raise Warning('onUserJoin')

	def onUserJoin(self, seat):
		''' 玩家加入游戏回调 '''
		raise Warning('onUserJoin')

	def onUserQuit(self, seat):
		''' 玩家离开游戏回调 '''
		raise Warning('onUserQuit')


	def handler(self, eid, reqName, *args):
		''' 处理转发消息 '''
		player = next(self.players)
		if player and hasattr(player, reqName):
			for player in self.players:
				if player.ableHandler(eid):
					reqFunc = getattr(player, reqName)
					reqFunc(*args)
		if hasattr(self, reqName):
			reqFunc = getattr(self, reqName)
			return reqFunc(eid, *args)
		print(reqName+' have no handler')


	def user_onEnteredAoI(self, eid):
		print('user_onEnteredAoI')
		self.onUserEnterRoom(eid)


	def reqRoomSeatdown(self, userID, seat=0):
		''' 请求坐下 '''
		if userID in (v.userID for v in self.players):
			raise Warning('reqRoomSeatdown: %d'% (userID,))
		one = self._players[seat] #优先座位号
		if one.userID:
			for player in self._ableSeat():
				one = player
				break
		if one.userID: #没有座位了
			return
		one.setUserID(userID)
		return True


	def onClientOffline(self, userID):
		if self.roomID:
			user = KBEngine.entities[userID]
			user.reqQuitRoom(userID, self.roomID)

	def _ableSeat(self):
		for player in self.players:
			if not player.userID:
				yield player

	def useRobot(self):
		for player in self._ableSeat():
			player.setRobot(True)
			if random.choice(range(0, 5)) > 3:
				return True


	def cancelRobot(self):
		for player in self.players:
			if player.isRobot:
				player.setRobot(False)

	def _robotCase(self):
		self.useRobot()


	def getTaxGold(self):
		''' 得到税收金币 '''
		return - self.baseScore * get_tax_rate(self.gameLevel)


''' 
KBEngine.reloadScript(True)
import User
game = User.get('GameNN')
t = game._testCase()
print(next(t))
'''

# def test():
# 	game = newGame
# 	print(game)
# 	return game


