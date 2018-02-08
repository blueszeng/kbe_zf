# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import d_default_nick
import random
import Math
import importlib
import enumDef
import d_game
import Functor
import json
import Room
import time
import UserInfo
import KbeCallback
from Functor import *

importlib.reload(d_game)
importlib.reload(d_default_nick)
importlib.reload(UserInfo)
importlib.reload(KbeCallback)

DISTANCE_IN_HALL = 10
''' 最大游戏保存次数 '''
MAX_GAMEMEMO = 60
 
def getRandomNick(uid):
	newNick = random.choice(d_default_nick.name1)
	return newNick + str(uid)


# 用户Entity
class User(KBEngine.Proxy, UserInfo.UserInfo, KbeCallback.KbeCallback):
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		KbeCallback.KbeCallback.__init__(self)
		UserInfo.UserInfo.__init__(self)

		self._getRoomIDsIter = None
		self._changeLimit = 3
		self._fiterRoomConditions = None
		# 任务栈
		self._taskStack = []
		# 初始化数据
		self.initProps()
		# self.updInfoFromAccount()


	def initProps(self):
		if self.cellData:
			self.gold = self.cellData.get('gold', 0)


	def updInfoFromAccount(self):
		clientData = None
		for val in self.getClientDatas():
			if not val:
				continue
			try:
				val = json.loads(val.decode("utf-8"))
				if isinstance(val, dict):
					clientData = val
			except Exception as identifier:
				logi(identifier)
		if isinstance(clientData, dict) and self.cellData:
			self.cellData['head'] = clientData.get('headimgurl', '')
			self.cellData['nick'] = clientData.get('nickname', self.cellData['nick'])
			self.cellData['sex'] = clientData.get('sex', 0)


	def sendToClient(self, callName, *args):
		if self.client:
			getattr(self.client, callName, *args)


	@property
	def _hall(self):
		return KBEngine.globalData["Hall"]


	def reqEnterRoom(self, roomID):
		''' 请求进入一个房间 '''
		room = KBEngine.entities.get(roomID)
		if not room or not room.cell:
			return logw('reqEnterRoom', self.id)
		self.cell.doEnterRoom(roomID, room.cell)
		self.matchState = 0


	def _doGetRoomIDs(self, page):
		''' 获得房间列表的迭代器 '''
		roomIDs = self._hall.doGetAllRoomIDs()
		count = len(roomIDs) // page
		for idx in range(0, count+1):
			start = idx*page
			to = (idx+1)*page
			if to > len(roomIDs):
				to = len(roomIDs)
			toIDs = roomIDs[start:to]
			yield toIDs
		yield None

	def reqNewRoomID(self, gameName='GameNN', level=0, conditions=None):
		self._fiterRoomConditions = conditions

		self._hall.addKbeCallback('onRoomCreated', self.id, 'onRoomCreated')
		self._hall.reqCreateRoom( gameName, level, 1)

	def onRoomCreated(self, roomID):
		''' 创建房间回调 '''
		self.checkTask()
		room = KBEngine.entities.get(roomID)
		if not self._fiterRoomConditions:
			self._hall.removeKbeCallback('onRoomCreated', self.id, 'onRoomCreated')
			return
		if room and self._fiterRoom(room, self._fiterRoomConditions):
			self._fiterRoomConditions = None
			self._hall.removeKbeCallback('onRoomCreated', self.id, 'onRoomCreated')
			self.reqEnterRoom(roomID)


	def _fiterRoom(self, room, conditions):
		return all( cdt(room) for cdt in conditions)

	def _getRooms(self, roomIDs):
		for roomID in roomIDs:
			room = KBEngine.entities.get(roomID)
			if room:
				yield room
	

	def reqStartGame(self, gameName=None, gameLevel=-1):
		''' 请求开始游戏 '''
		if gameName == None:
			gameName = 'GameNN'
		for v in reversed(list(d_game.match_cfgs(gameName))):
			if v['goldMin'] <= self.gold:
				if gameLevel == -1:
					gameLevel = v['gameLevel']
					break
			elif gameLevel == v['gameLevel']:
				return self.client.onMsgTips(0, '金币不足')
		self._hall.doMatchByUser(self, gameName, gameLevel, 0)
		# self.matchState = 1
		# roomIDs = self._hall.getRoomIDs(self, gameName, gameLevel)
		# for room in self._getRooms(roomIDs):
		# 	if room.roomState == 2:
		# 		return self.reqEnterRoom(room.id)
		# self.reqNewRoomID(gameName, gameLevel, [
		# 	lambda r: r.gameName == gameName,
		# 	lambda r: r.gameLevel == gameLevel,
		# 	lambda r: r.roomState == 2,
		# ])
		

	def reqDebugCmd(self, cmd):
		print('reqDebugCmd', cmd)
		exec(cmd)
		self.client.onDebugCmd('..')

	def doChangeRoom(self, roomID=None):
		''' 切换房间 '''
		room = KBEngine.entities.get(roomID)
		gameName = room.gameName
		gameLevel = room.gameLevel
		self._hall.doMatchByUser(self, gameName, gameLevel, roomID)
		# condition = '_.gameName=="%s" and _.roomState==2 and _.gameLevel==%d and _.id!=%d'%(
		# 	gameName, gameLevel, roomID)
		# roomIDs = self._hall.getRoomIDs(self, gameName, gameLevel)
		# condition = [
		# 	lambda r: r.gameName == gameName,
		# 	lambda r: r.gameLevel == gameLevel,
		# 	lambda r: r.roomState == 2,
		# 	lambda r: r.id != roomID,
		# ]
		# for room in self._getRooms(roomIDs):
		# 	if self._fiterRoom(room, condition):
		# 		return self.reqEnterRoom(room.id)
		# self.reqNewRoomID(gameName, gameLevel, condition)


	def doSaveGameMemo(self, menoItem):
		''' 保存游戏记录 '''
		self.gameMemo.append(menoItem)
		if len(self.gameMemo) > MAX_GAMEMEMO:
			self.gameMemo.pop(0)

	def reqGotGameMemo(self, curIdx, page):
		''' 请求获取 gameMemo 列表 '''

		start = curIdx*page
		to = start + page
		total = len(self.gameMemo)
		if to > total:
			to = total
		items = []
		for idx in range(start, to):
			items.append(self.gameMemo[total-idx-1])
		if self.client:
			self.client.onGotGameMemo(curIdx, total, items)


	def onLoseCell(self):
		''' 关联的cell实体销毁 '''
		# if self._roomCellMB:
		# 	self.createCellEntity(self._roomCellMB)

	def onGetCell(self):
		''' 创建cell完成 '''
		# self.cell.addKbeCallback('reqChargeGold', self.id, 'base.onChargeGold')

	def onEntitiesEnabled(self):
		"""
		KBEngine method.
		该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
		cell部分。
		"""
		INFO_MSG("account[%i] entities enable. mailbox:%s" % (self.id, self.client))

		self.saveLoginMemo()
		if self.cell:
			''' 重新连接 '''
			self.cell.onClientReconnect()
		else:
			self.createInNewSpace(None)


	def onLogOnAttempt(self, ip, port, password):
		"""
		KBEngine method.
		客户端登陆失败时会回调到这里
		"""
		INFO_MSG(ip, port, password)
		return KBEngine.LOG_ON_ACCEPT

	def onClientDeath(self):
		"""
		KBEngine method.
		客户端对应实体已经销毁
		"""
		DEBUG_MSG("Account[%i].onClientDeath:" % self.id)
		self.cell.onClientOffline()


	def reqLoginOut(self):
		''' 登出请求 '''
		if self.cell:
			# self.cell.onClientOffline()
			print('待处理 cell 登出')
		else:
			self.destroy()
		# 断开连接
		self.disconnect()

	def reqGetMatchInfos(self, gameType):
		''' 匹配场次信息 '''
		gameName = enumDef.GAME_TYPE_NAME.get(gameType)
		assert gameName, 'gameType is error: '+gameType
		matchInfos = []
		for cfg in d_game.GAMENAME_MATCH.get(gameName):
			info = dict(cfg)
			info['able'] = 1 if self.gold >= info['goldMin'] else 0
			matchInfos.append(info)
			
		self.client.onGotMatchInfos(matchInfos)

	def onGoldChange(self, gold):
		self.gold = gold
		self.goldTotal_nn = gold

	@property
	def loginIP(self):
		strip = ".".join([str(self.clientAddr[0] >> x & 0xff) for x in [24, 16, 8, 0]])
		return transformIP(strip)



	def reqGetGoldRank(self):
		''' 请求获取排行榜 '''
		KBEngine.globalData['Hall'].reqGetGoldRank(self.client)
	
	
	def _getListPage(self, propName, idx, page):
		''' 列表分页 '''
		array = getattr(self, propName, [])
		start = idx*page
		to = start + page
		total = len(array)
		if to > total:
			to = total
		items = []
		for i in range(start, to):
			items.append(array[total-i-1])
		return total, items


def transformIP(strIP):
	#self._ip = ".".join([str(self.clientAddr[0] >> x & 0xff) for x in [24, 16, 8, 0]])
	#返回的字符串
	returnIP = ['a','b','c','d']	
	#取ip的第几个位置
	iset = 3
	#上一次点在字符串的位置
	ispot = 0
	for i in range(len(strIP)):
		if strIP[i] == '.':
				returnIP[iset] = '.' + strIP[ispot:i]
				iset -= 1
				ispot = i + 1
	returnIP[0] = strIP[ispot:len(strIP)]
	rip = ''.join(returnIP)
	return rip
