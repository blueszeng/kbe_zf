# -*- coding: utf-8 -*-

import KBEngine
import random
import time
import d_hall
from KBEDebug import *
from Functor import *
import importlib

import KbeCallback
import HallMatch
import tornado.httpclient

importlib.reload(d_hall)
importlib.reload(HallMatch)
importlib.reload(KbeCallback)

BOOT_GAMES = {
	'GameNN': [
		1,1,1,1
	]
}


class Hall(KBEngine.Base, KbeCallback.KbeCallback, HallMatch.HallMatch):
	''' 大厅实体 '''
	def __init__(self):
		KBEngine.Base.__init__(self)
		KbeCallback.KbeCallback.__init__(self)
		HallMatch.HallMatch.__init__(self)

		KBEngine.globalData["Hall"] = self

		self._goldRank = [v for v in self.goldRank]

		# 将数据转换成字典
		self._goldRankInfos = {v['uid']:v for v in self.goldRankInfos}
		self._goldRank_addDict = {}
		self._goldRankTimer = self.addTimer(2, 5, 0)

		self._roomIDs = []
		self._roomIDsNN = {0:[],1:[],2:[],3:[]}
		self._roomIDsByGame = {'GameNN':self._roomIDsNN}

		self.initTornado()

		self._agentUsers = None

		# self._gameIDs = []
		# self._doReadyForGames('GameNN', BOOT_GAMES['GameNN'])

	def _getAgentUserByID(self, playerid):
		if not self._agentUsers:
			self._agentUsers = {}
			for idx, agentUser in enumerate(self.agentUsers) or []:
				self._agentUsers[agentUser['playerid']] = idx
				return self._agentUsers.get(agentUser['playerid'])

	def saveAgentUserInfo(self, agentUser):
		idx = self._getAgentUserByID(agentUser['playerid'])
		if not idx:
			self.agentUsers.append(agentUser)
			idx = len(self.agentUsers)
			self._agentUsers[agentUser['playerid']] = idx
		self.agentUsers[idx] = agentUser


	def initTornado(self):
		self._timerTornado = self.addTimer(0.3, 0.3, 0)

	def onTimer(self, tid, userTag):
		if self._timerTornado == tid:
			tornado.ioloop.IOLoop.current().start()
		if self._goldRankTimer == tid:
			self._onTimerUpdGoldRank()



	def getCellMailBox(self, reqMB, entityID):
		entity = self._entity(eid)
		if not entity:
			return logw('getCellMailBox')
		if not entity.cell:
			return logw('getCellMailBox', 'no cell')
		reqMB.onGotCellMailBox(entityID, entity.cell)


	def getRoomIDs(self, reqMB, gameName, gameLevel):
		game_ids = self._roomIDsByGame.get(gameName)
		if not game_ids:
			return logi('getRoomIDs', reqMB.id)
		roomIDs = game_ids.get(gameLevel, [])
		return roomIDs


	def onGoldRankChange(self, rankItem, goldRankItem):
		""" 金币排行榜变化 """
		self._goldRank_addDict[rankItem['uid']] = rankItem
		self._goldRankInfos[goldRankItem['uid']] = goldRankItem


	def _onTimerUpdGoldRank(self):
		''' 定时刷新金币榜 '''
		if len(self._goldRank_addDict) == 0:
			return
		rankDict = d_hall.rankDict(self._goldRank)
		self._goldRank = d_hall.updRankDict(rankDict, self._goldRank_addDict)
		self._goldRank_addDict = {}
		self.goldRank = d_hall.copyRank(self._goldRank)
		rankInfos = self._goldRankInfos
		self.goldRankInfos = [rankInfos[v['uid']] for v in self.goldRank if rankInfos.get(v['uid'])]
		logi('self.goldRank', self.goldRank)


	def reqGetGoldRank(self, clientMB):
		items = []
		for idx, item in enumerate(self._goldRank):
			info = self._goldRankInfos.get(item['uid'])
			if info:
				items.append({
					'idx': idx,
					'gold': item['value'],
					'nick': info['nick'],
					'head': info['head'],
					'signature': info['signature'],
				})
		# print('items', items)
		clientMB.onGoldRank(items)



	def _doReadyForGames(self, gameName, counts):
		for level, count in enumerate(counts):
			self.reqCreateRoom(count, level, gameName)
		

	def reqCreateRoom(self, gameName='GameNN', level=0, count=1):
		''' 创建房间 '''
		params = {'gameName': gameName, 'gameLevel':level }
		for i in range(0, count):
			KBEngine.createBaseAnywhere("Room", params)

	def onRoomCreated(self, roomID):
		print('onRoomCreated')
		room = self._entity(roomID)
		if not room:
			return
		self._roomIDs.append(roomID)
		self._roomIDsNN[room.gameLevel].append(roomID)
		self.kbeFire('onRoomCreated', roomID)


	def reqGetFiterRoomID(self, condition, count=1):
		''' 筛选获得房间id表
		condition: 筛选条件python语句
		 '''
		roomIDs = []
		for idx, room in enumerate(self._fiterRoom(condition)):
			if idx >= count:
				break
			roomIDs.append(room.id)
		return roomIDs


	def doGetAllRoomIDs(self):
		''' 得到所有房间id '''
		return self._roomIDs.copy()


	def onUserEnter(self, eid):
		print('onUserEnter')
		# user = self._getUser(eid)





	def onGameCreated(self, eid):
		print('onGameCreated')
		# game = self._entity(eid)
		# self._gameIDs.append((eid, game.roomID, game.className))


	def _getUser(self, eid):
		user = self._entity(eid)
		assert user.className == 'User'
		return user

	def _fiterRoom(self, condition):
		''' 按条件筛选 '''
		evalStr = '( _ for _ in self._iterRoom() if %s )'%condition
		iterObj = None
		try:
			iterObj = eval(evalStr)
		except SyntaxError as info:
			print('_fiterRoom', info)
		if iterObj != None:
			for room in iterObj:
				yield room

	def _iterRoom(self):
		''' 迭代所有房间 '''
		for roomID in self._roomIDs:
			room = self._entity(roomID)
			yield room

	def _entity(self, idOrClass):
		''' 获得某entity '''
		return get(idOrClass)



def get(idOrClass):
	if isinstance(idOrClass, int):
		obj = KBEngine.entities.get(idOrClass)
		print('found:', obj)
		return obj
	for e in KBEngine.entities.values():
		if e.__class__.__name__ == idOrClass:
			print('found:', e)
			return e




