#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import KBEngine
from KBEDebug import *
from Functor import *

import random
import time
import GamePlayer
import GameNNRule
from GameNN import NNSTATE
from Callbacks import supports_callbacks

AREA = 40.0


class GameNNPlayer(GamePlayer.GamePlayer):
	def __init__(self):
		GamePlayer.GamePlayer.__init__(self)

	def reset(self, game):
		self.ready = -1
		self._game = game
		self.gaming = 0
		self.isBanker = 0
		self.handPoker = []
		self.allPoker = []
		self.ownerPoker = 0
		self.qiangRate = -1
		self.yazhu = -1
		self._yazhuAble = []
		self.showState = -1
		self.BroadcardTypeValue = 0
		self.cardTypeValue = 0
		self._setMsgFapai()

	def onSetUser(self, userID):
		''' 设置玩家回调 '''


	def onClientReconnect(self):
		print("onClientReconnect",self.id)
		self._sendYazhuAble()
		self._game.updCutdown()
		self.callClient('onGameNNOwnerPoker', self._ownerPoker)
		self._setMsgFapai(*self._msgFapai)

	def doFapai(self, poker):
		self.allPoker = poker
		self.handPoker = [0]*(len(poker)-1)
		self.ownerPoker = len(poker)-1
		self._setMsgFapai(4, self.ownerPoker, [])


	def _setMsgFapai(self, count=0, myCards=None, allCards=None):
		''' 发牌消息 '''
		self._msgFapai = (count, myCards or [], allCards or [])
		self.callClient('gameNN_fapai', *self._msgFapai)


	@property
	def ownerPoker(self):
		return self._ownerPoker


	@ownerPoker.setter
	def ownerPoker(self, val):
		self._ownerPoker = self.allPoker[0:val]
		self.callClient('onGameNNOwnerPoker', self._ownerPoker)

	def reqGameNNQiang(self, qiangRate):
		try:
			self._game._doQiang(self.seat, qiangRate)
		except AssertionError as identifier:
			print('reqGameNNQiang', identifier)

	def onClientOffline(self):
		if self.ready == 1:
			self.ready = 0
			self.userID = 0
		if self.gaming == 1:
			pass


	def setMinYazhuAble(self, rate):
		nor = [1,4,8]
		self._yazhuAble = [ v for v in nor if rate < v ]
		self._sendYazhuAble()

	def _sendYazhuAble(self):
		yazhuable = self._yazhuAble
		if not self._game._canYazhu(self):
			yazhuable = []
		self.callClient('onGameNNYazhuAble', yazhuable)


	def reqGameNNYazhu(self, yazhu=None):
		'''  '''
		try:
			if yazhu == None:
				yazhu = self._yazhuAble[0]
			assert yazhu in self._yazhuAble
			self._game._doYazhu(self.seat, yazhu)
		except AssertionError as identifier:
			print('reqGameNNYazhu', identifier)

	
	def doFapaiSec(self):
		self.ownerPoker = len(self.allPoker)
		self.handPoker = [0]*(len(self.allPoker))
		self._setMsgFapai(5, self.ownerPoker, [])

	def doCalCardType(self):
		self.cardTypeValue = GameNNRule.judgePoker(self.allPoker)
		self.callClient('cardTypeValue', self.cardTypeValue)


	def reqGameNNShowPoker(self):
		try:
			self._game._doShowPoker(self.seat)
		except AssertionError as identifier:
			print('reqGameNNShowPoker', identifier)


	def reqQuitRoom(self):
		if self._game.canQuitGameState():
			self._game.room.doUserLeave(self.userID)
			self.setUserID(0)


	def reqChangeRoom(self):
		if self._game.canQuitGameState():
			self.callUserBase('doChangeRoom', self.roomID)
			self.setUserID(0)


	def doShowPoker(self, allPokers):
		self.handPoker = self.allPoker
		if self.isBanker:
			self.showState = 2
		else:
			self.showState = 1
		self._setMsgFapai(5, [], allPokers)


	def onSettled(self, settleItem):
		user = self._user()
		if not user:
			return logi('TODO 机器人结算处理')
		curGold = user.doChangeGold(settleItem['value'])
		self.gold = curGold
		curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		if not self.isRobot and user.base:
			user.base.doSaveGameMemo({'time':curtime, 'gameName':'GameNN', 'win':settleItem['value']})
			user.onGameEnd(settleItem['value'])

	def onTimerRobot(self):
		''' 处理机器人业务 '''
		if self.gaming == 0:
			return
		game = self._game
		if game.nnState == NNSTATE.QIANG:
			if game._canPlayerQiang(self):
				self.reqGameNNQiang(random.choice(range(0, game.qiangMax)))
		elif game.nnState == NNSTATE.YAZHU:
			if game._canYazhu(self):
				self.reqGameNNYazhu()
		elif game.canQuitGameState():
			# 没有真实玩家就退出机器人
			if not any(game.userPlayers()):
				self.setRobot(False)
		
		

