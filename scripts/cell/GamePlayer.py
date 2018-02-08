#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import random
import weakref
import KBEngine
from Functor import *
from KBEDebug import *

from Callbacks import supports_callbacks

import Game

AREA = 40.0

ROBOT_TIME = 1.0


class GamePlayer(KBEngine.Entity):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		self._robotTimer = None

	def setUserID(self, userID):
		old = self.userID
		self.userID = userID
		self.onSetUser(userID)
		if userID == 0:
			self.nick = ''
			self.uid = 0
			self.gold = 0
			self.head = ''
			self.initcoin = 0
			if old:
				self.game.onUserQuit(self.seat)
		else:
			user = self._user()
			self.nick = user.nick
			self.uid = user.uid
			self.initcoin = user.gold
			self.gold = self.initcoin
			self.head = user.head
			self.game.onUserJoin(self.seat)


	def onSetUser(self, userID):
		raise Warning('onSetUser')


	def ableHandler(self, userID):
		return userID == self.userID

	@property
	def game(self):
		return KBEngine.entities.get(self.gameID)

	def doStartGame(self):
		''' 执行开始操作 '''
		self.gaming = 1

	def doTaxGold(self, taxGold):
		''' 金币税收 '''
		user = self._user()
		if user:
			user.doChangeGold(int(taxGold))

	def _user(self):
		if self.userID > 0:
			return KBEngine.entities.get(self.userID)

	def onDestroy(self):
		if self.isRobot:
			# 机器人销毁虚user
			user = self._user()
			if user and not user.isDestroyed:
				user.destroy()

	def clearUserOffline(self):
		if self.isRobot:
			return
		user = self._user()
		if user:
			if user.isOffline or not user.isWitnessing(self.id):
				self.game.doKickUser(self.userID)
				return True

	def callClient(self, callName, *args):
		''' 调用客户端 '''
		user = self._user()
		if user and user.client:
			if user.isInRoom(self.game.roomID):
				getattr(user.client, callName)(*args)

	def callUserBase(self, callName, *args):
		''' 调用 userBase '''
		user = self._user()
		if user and user.base:
			if user.isInRoom(self.game.roomID):
				getattr(user.base, callName)(*args)

	def onClientReconnect(self):
		print("onClientReconnect",self.id)
		pass

	@property
	def isRobot(self):
		user = self._user()
		if user:
			return user.client == None

	def setRobot(self, isRobot):
		if isRobot:
			if not self.userID:
				posInfo = (self.spaceID, self.position, self.direction)
				user = KBEngine.createEntity( 'User', *posInfo )
				user.nick = 'robot'+str(self.id)
				self.setUserID(user.id)
				self.robotUserID = user.id
			self._robotTimer = self.addTimer(1,ROBOT_TIME,0)
		else:
			if self.robotUserID:
				self._user().destroy()
				self.robotUserID = 0
				self.setUserID(0)

	def onTimer(self, tid, *args):
		if tid and self._robotTimer == tid:
			if not self.isRobot:
				self.delTimer(tid)
			else:
				if random.random() > 0.5:
					self.onTimerRobot()


	def onTimerRobot(self):
		''' 机器人timer '''
		print('onTimerRobot')
	
