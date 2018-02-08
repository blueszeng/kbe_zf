#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import KBEngine
from KBEDebug import *
from Functor import *
import importlib



class HallMatch:
	''' 大厅匹配部分
	'''
	def __init__(self):
		self._rooms = {}
		self._games = {
			'GameNN': {}
		}
		''' 匹配中的玩家 '''
		self._matchUsers = {}
		''' 匹配中的房间 '''
		self._matchRooms = {}


	def doMatchByUser(self, user, gameName, gameLevel=-1, filterID=0):
		''' 玩家匹配 '''
		userMatch = (user, gameName, gameLevel, filterID)
		for roomMatch in self._matchRooms.values():
			if self.doMatch(userMatch, roomMatch):
				return
		self._matchUsers[user.id] = userMatch
		self.reqCreateRoom(gameName, gameLevel)


	def doMatchByRoom(self, room, gameName, gameLevel):
		''' 房间匹配 '''
		roomMatch = (room, gameName, gameLevel)
		for userMatch in self._matchUsers.values():
			if self.doMatch(userMatch, roomMatch):
				return
		self._matchRooms[room.id] = roomMatch


	def doMatch(self, userMatch, roomMatch):
		user, gN, gL, fID = userMatch
		room, gNr, gLr = roomMatch
		if gN and gNr != gN:
			return
		if gL >= 0 and gLr != gL:
			return
		if fID > 0 and fID == room.id:
			return
		user.reqEnterRoom(room.id)
		# user.onceKbe('onEnterRoomOk', self, 'onUserJoinedRoom')
		return True

	def doCancelMatch(self, roomID):
		if self._matchRooms.get(roomID):
			self._matchRooms.pop(roomID)


	def onUserJoinedRoom(self, userID, roomID):
		if self._matchUsers.get(userID):
			self._matchUsers.pop(userID)
		
