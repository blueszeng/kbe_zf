#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import KBEngine
from KBEDebug import *
from Functor import *
import Room
import random
import time
import Math
import Game
import echo
import GameNN
import GamePlayer
import UserHeadTask
import KbeCallback
import d_hall
import d_tips
import json
import d_game
from d_tips import tips
import importlib


importlib.reload(d_game)
importlib.reload(d_hall)
importlib.reload(d_tips)
importlib.reload(UserHeadTask)

AOI_IN_ROOM = 80.0
AOI_IN_HALL = 1.0
MIN_MONEY = 0.01
MAX_MONEY = 9999999999

# 保险金单次最低额
SAFEGOLD_MIN = 1
# 保险金限制
SAFEGOLD_LIMIT = 800

# 客户端用户
class User(KBEngine.Entity, UserHeadTask.UserHeadTask, KbeCallback.KbeCallback):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		KbeCallback.KbeCallback.__init__(self)
		# UserHeadTask.UserHeadTask.__init__(self)
		
		self._callback = {}
		# if not self.head or not len(self.head):
		# 	self.head = '0'
		#self.gold = 0

		self.updInfoFromAccount()
		
		self.doAddGold()
		self._offline = False

		''' 请求处理列表 '''
		self._reqing = {}

		''' 触发更新 '''
		self.doChangeGold()


	def doUpdAccountData(self, data):
		self.accountDataCell = data
		self.updInfoFromAccount()

	def updInfoFromAccount(self):
		if len(self.accountDataCell) == 0:
			return
		data = json.loads(self.accountDataCell)
		if 'nickname' in data:
			self.nick = data['nickname']
		if 'head' in data:
			self.head = data['head']
		if 'headimgurl' in data:
			self.head = data['headimgurl']
		if 'sex' in data:
			self.sex = data['sex']
		
		


	def reqQuitRoom(self, eid, roomID):
		''' 请求退出一个房间 '''
		try:
			assert self.room and self.room.id == roomID
			self._handleByGame('reqQuitRoom')
		except Exception as identifier:
			WARNING_MSG('reqQuitRoom: ', identifier)


	def reqTeleport(self, eid, mailbox):
		''' 请求移动 '''
		self.position.x = 0
		self.position.y = 0
		self.teleport(mailbox, self.position, self.direction)

	
	def doEnterRoom(self, roomID, roomMB=None):
		''' 请求进入房间 '''
		oldRoom = self.room
		if oldRoom and oldRoom.id == roomID:
			return logw('reqEnterRoom 重复进入房间', self.id)
		if roomMB == None:
			self._reqing['reqEnterRoom'] = roomID
			return self._hall.getCellMailBox(self, roomID)
		self.reqTeleport(roomID, roomMB)


	def onGotCellMailBox(self, eid, entityID, cellMB):
		''' 收到回复 '''
		for reqName, theID in self._reqing.items():
			if theID == entityID:
				self._reqing[reqName] = None
				getattr(self, reqName)(self.id, entityID, cellMB)

	@property
	def isOffline(self):
		print('isOffline', self._offline)
		return self._offline


	def reqChangeRoom(self, eid):
		self._handleByGame('reqChangeRoom')


	def reqGameNNStart(self, eid):
		''' 请求开始游戏 '''
		self._handleByGameNN('reqGameNNStart')

	def reqGameNNQiang(self, eid, qiangRate):
		self._handleByGameNN('reqGameNNQiang', qiangRate)

	def reqGameNNYazhu(self, eid, yazhu):
		self._handleByGameNN('reqGameNNYazhu', yazhu)


	def _handleByGameNN(self, reqName, *args):
		assert isinstance(self.game, GameNN.GameNN), 'error GameNN'
		self.game.handler(self.id, reqName, *args)


	def onTeleportSuccess(self, *args):
		game = self.game
		if game and not game._canJoinGame():
			self.base.doChangeRoom(game.roomID)
		# logd('onTeleportSuccess', args)


	def _handleByRoom(self, reqName, *args):
		room = self.room
		if room:
			room.userReq(self.id, reqName, *args)

	def _handleByGame(self, reqName, *args):
		try:
			if self.game:
				self.game.handler(self.id, reqName, *args)
		except Exception as e:
			logw('_handleByGame: ', reqName)


	def reqRoomSeatdown(self, eid, seat=0):
		self._handleByGame('reqRoomSeatdown', seat)
	
	
	def onClientOffline(self):
		print('onClientOffline')
		self._offline = True
		self._handleByGame('onClientOffline')
	
	def onClientReconnect(self):
		logi('onClientReconnect')
		self.onTaskLogined()
		self._offline = False
		self._handleByGame('onClientReconnect')
		self.doAddGold()

	def onGameDestroy(self):
		print('onGameDestroy')
	

	def reqDebugCmd(self, eid, cmd):
		print('reqDebugCmd', cmd)
		exec(cmd)
		self.client.onDebugCmd('..')

	def onGetWitness(self):
		print('onGetWitness')
		self.onTaskLogined()
		self.setAoiRadius(AOI_IN_HALL, 0.0)


	def onEnterSpace(self):
		self._offline = False

	def doAddGold(self):
		''' 登录金币小于 100 则增加 10000 '''
		# if self.gold < 100:
		# 	self.doChangeGold(10000)

	def doChangeGold(self, change=0, total=None):
		if total != None:
			self.gold = int(total)
		else:
			self.gold += int(change)
		if self.base:
			self.base.onGoldChange(self.gold)
		player = self.myPlayer
		if player:
			player.gold = self.gold
		
		# self._checkGoldRank()
		return self.gold


	def _checkGoldRank(self):
		''' 检查能否加入金币榜 '''
		if not self.base or self.uid == 0:
			return
		rankItem = {
			'uid': self.uid,
			'time': int(time.time()),
			'value': self.gold
		}
		goldRankItem = {
			'idx': -1,
			'uid': self.uid,
			'nick': self.nick or '',
			'head': self.head or '',
			'signature': ''
		}
		KBEngine.globalData['Hall'].onGoldRankChange(rankItem, goldRankItem)

	def getDictByKeys(self, keysStr, mb, callName):
		keys = json.loads(keysStr)
		getattr(mb, callName, json.dumps({k: getattr(self, k) for k in keys}))

	def onEnteredAoI(self, entity):
		self._offline = False
		if isinstance(entity, Room.Room):
			''' 进入房间 '''
			self.room.onUserEnter(self.id)
			self.setAoiRadius(AOI_IN_ROOM, 0.0)
		
		if isinstance(entity, Game.Game):
			self._handleByGame('user_onEnteredAoI')
		if self.myPlayer:
			self._hall.onUserJoinedRoom(self.id, self.myPlayer.game.roomID)


	def _getGameNN(self):
		if not self.hasWitness:
			return
		for entity in self.entitiesInAOI():
			if isinstance(entity, GameNN.GameNN):
				return entity

	@property
	def game(self):
		''' 当前可见的game实体 '''
		if not self.hasWitness:
			return
		for entity in self.entitiesInAOI():
			if isinstance(entity, Game.Game):
				return entity

	@property
	def myPlayer(self):
		''' 属于自己的player '''
		if not self.hasWitness:
			return
		for entity in self.entitiesInAOI():
			if isinstance(entity, GamePlayer.GamePlayer) and entity.userID == self.id:
				return entity

	@property
	def gamePlayers(self):
		''' 得到当前所有player '''
		if not self.hasWitness:
			return
		for entity in self.entitiesInAOI():
			if isinstance(entity, GamePlayer.GamePlayer):
				yield entity

	@property
	def room(self):
		''' 当前所在 room 实体 '''
		if not self.hasWitness:
			return
		for entity in self.entitiesInAOI():
			if isinstance(entity, Room.Room):
				return entity

	def isInRoom(self, roomID):
		''' 是否在房间中 '''
		if self.hasWitness:
			if roomID in (v.id for v in self.entitiesInAOI()):
				return True

	def reqRoomChat(self, eid, *args):
		''' 在房间中发言 '''
		self.allClients.onRoomPlayerChat(eid, *args)


	def reqSendHudong(self, eid, toSeat, hudongID):
		''' 互动道具 '''
		assert toSeat != None
		seatedPlayers = list(filter(Game.is_seatedPlayer, self.gamePlayers))
		mySeat = it_first(v.seat for v in seatedPlayers if v.userID == self.id)
		if mySeat == None:
			return logw('reqSendHudong mySeat is None:', self.id)

		goldUse = d_game.HUDONG_ONCE_GOLD
		if mySeat == toSeat:
			num = (it_count(seatedPlayers) - 1)
			goldUse = num * goldUse

		if not self.room.isGoldEnough(self.gold-goldUse):
			logi('reqSendHudong gold is not enough:', self.id, self)
			return self.sendMsgTips(tips['互动道具'], '金币不足')

		if toSeat not in (v.seat for v in seatedPlayers):
			return logw('reqSendHudong toSeat is not in seated:', self.id, toSeat)

		if toSeat in (v.seat for v in seatedPlayers):
			logi('reqSendHudong toSeat is in seated:', self.id, toSeat)

		self.doChangeGold(-goldUse)
		self.allClients.onRecvHudong(mySeat, toSeat, hudongID)


	def sendMsgTips(self, msgID, msgStr=''):
		if self.base and self.client:
			self.client.onMsgTips(msgID, msgStr)


	def isWitnessing(self, eid):
		''' entity是否在其视野中 '''
		if self.hasWitness:
			if eid in (v.id for v in self.entitiesInAOI()):
				return True

	@property
	def _hall(self):
		return KBEngine.globalData["Hall"]


	def _test_game(self, isRestart=False):
		if isRestart:
			self._case = None
		if getattr(self, '_case', None) == None:
			self._case = self.game._testCase(self)
		print(next(self._case))


	def reqChargeGold(self, chargeNum, chargeID=None):
		''' 充值 '''
		self.doChangeGold(chargeNum)
		self.sendMsgTips(0, '充值成功！')
		# chargeId = int(random.random()*100000)
		# timeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		# memo = {'id':chargeId, 'num':chargeNum, 'charge':1, 'time':timeStr, 'state':1}
		self.base.onChargeResult(1, chargeID or '')
		# self.kbeFire('reqChargeGold', chargeNum)
		self.onTaskCharge(chargeNum)


	def showAll(self):
		print(vars(self))
		keys = ['hasWitness', 'isOnGround', 'isWitnessed', 'client']
		print([(k, getattr(self, k)) for k in keys])


	def reqChangeSignature(self, eid, signature):
		''' 修改签名 '''
		self.signature = signature


	def reqChangeNick(self, eid, nick):
		''' 修改签名 '''
		self.nick = nick
		self.sendMsgTips(0, '修改成功'+str(nick))


	def reqSaveGold(self, eid, count):
		''' 请求保存保险金 '''
		if count <= 0:
			return print('reqSaveGold', 'BAD count')
		if count < SAFEGOLD_MIN:
			return self.sendMsgTips(tips['小于最低保险金金额'], str(SAFEGOLD_MIN))
		if self.gold - count < SAFEGOLD_LIMIT:
			return self.sendMsgTips(tips['携带的金币不足'], str(SAFEGOLD_LIMIT))
		self.safeGold += count
		self.doChangeGold(-count)
		self.sendMsgTips(tips['保险金操作成功'], '存')

	def reqDrawSaveGold(self, eid, count, password):
		''' 请求取保险金 '''
		if self.safeGold < count:
			return self.sendMsgTips(tips['保险金余额不足'], str(self.safeGold))
		if self.isSameSafePassword(password):
			return self.sendMsgTips(1, str('密码不正确'))
		self.safeGold -= count
		self.doChangeGold(count)
		self.sendMsgTips(tips['保险金操作成功'], '取')

	def reqChangeGoldPass(self, eid, oldpass, newpass):
		''' 请求更改取款密码 '''
		response = lambda s: self.client and self.client.reqChangeGoldPass(str(s))
		if not self.safePassword or not len(self.safePassword):
			self.safePassword = '123456'
		if self.safePassword != oldpass:
			return response('原密码错误')
		if len(newpass) < 6 and len(newpass) > 8:
			return response('新密码不合法')
		self.safePassword = newpass
		self.onTaskChangeGoldPass()
		response('')

	def isSameSafePassword(self, password):
		if not self.safePassword or not len(self.safePassword):
			self.safePassword = '123456'
		return self.safePassword == password


	def reqGoldDraw(self, eid, num, password):
		''' 金币取现 '''
		assert self.base != None
		assert self.client != None
		response = lambda r, s: self.client and self.client.reqGoldDraw(r, str(s))
		if not num or num < 0:
			return response(1, '不合法请求')
		if self.gold < num:
			return response(2, '金币不足')
		if not self.isSameSafePassword(password):
			logi('n1', self.safePassword, password)
			return response(3, '密码不正确')
		if not self._bankInfo or self._bankInfo['bankNum'] == '':
			return response(4, '未绑定银行卡')
		self.gold -= num
		self.base.onSaveGoldDrawMemo(num)
		response(0,'')

	def reqBindBankCard(self, eid, name, bank, bankNum):
		''' 绑定银行卡信息 '''
		response = lambda r, s: self.client and self.client.reqBindBankCard(r, str(s))
		self._bankInfo = {
			'name': name,
			'bank': bank,
			'bankNum': bankNum,
		}
		response(0,'')

	
	def reqAgentDraw(self, eid, num, password):
		''' 代理取現 '''
		assert self.base != None
		assert self.client != None
		response = lambda r, s: self.client and self.client.reqAgentDraw(r, str(s))
		if not num or num < 0:
			return response(1, '不合法请求')
		if not self.isSameSafePassword(password):
			return response(2, '密码不正确')
		if not self._bankInfo or self._bankInfo['bankNum'] == '':
			return response(3, '未绑定银行卡')
		self.base.reqAgentDraw(num)
		# self.base.onSaveGoldDrawMemo(num)
		


	def _onReqAgentDraw(self, msg):
		pass



def get(idOrClass):
	if isinstance(idOrClass, int):
		obj = KBEngine.entities.get(idOrClass)
		print('found:', obj)
		return obj
	for e in KBEngine.entities.values():
		if e.__class__.__name__ == idOrClass:
			print('found:', e)
			return e
