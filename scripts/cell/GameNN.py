#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import random
import KBEngine
import kbemain
from KBEDebug import *
from Functor import *

import Game
import time
import d_game
import importlib
import GameNNRule
import User
from Callbacks import supports_callbacks
from echo import callback_property

AREA = 40.0
''' 最大座位号 '''
MAX_SEAT = 6
''' 最少开始游戏人数 '''
USER_MIN_COUNT = 2

QIANG_MAX = 4 

class NNSTATE:
	''' 游戏状态枚举 
		初始状态 NONE, 当人数达到开始游戏要求 切换到 BEGIN,
		在 NONE/BEGIN 阶段可以退出
		SETTLE 结束之后切换到 BEGIN
	'''
	NONE, BEGIN, FAPAI, QIANG, BANKER, YAZHU, FAPAISEC, SETTLE = range(0,8)

# 超时时间
TIMEOUT = {
	NNSTATE.NONE: 7,
	NNSTATE.BEGIN: 5,
	NNSTATE.FAPAI: 2,
	NNSTATE.QIANG: 15,
	NNSTATE.BANKER: 4,
	NNSTATE.YAZHU: 10,
	NNSTATE.FAPAISEC: 3,
	NNSTATE.SETTLE: 10,
}

class GameNN(Game.Game):
	''' 牛牛游戏模块 '''
	def __init__(self):
		Game.Game.__init__(self)
		self.gameName = 'GameNN'

	def onLoad(self):
		importlib.reload(GameNNRule)
		importlib.reload(kbemain)

	@property
	def _playerClsName(self):
		'''  游戏玩家类名 '''
		return 'GameNNPlayer'

	@property
	def _maxSeat(self):
		'''  最大座位号 '''
		return MAX_SEAT

	def onReset(self):
		self.nnState = NNSTATE.NONE
		self.room.onGameOvered()
		self.qiangMax = QIANG_MAX
		self.baseScore = self._getBaseScore()
		self.candidate = []
		self.bankerSeat = -1
		self.bankerRate = -1
		# self.settlement = {'items':[]}
		for player in self.players:
			player.reset(self)
		self._timers = {}
		self._addGameTimer()


	def _getBaseScore(self):
		return d_game.GAMENAME_MATCH[self.gameName][self.gameLevel]['baseScore']


	def reqGameNNStart(self, userID):
		''' 请求开始 '''
		print("reqGameNNStart")

	def onUserEnterRoom(self, userID):
		''' 玩家进入直接坐下 '''
		if not self.reqRoomSeatdown(userID):
			#失败踢出玩家
			self.doKickUser(userID)


	def doKickUser(self, userOrID):
		''' 踢出用户 '''
		userID = userOrID
		if isinstance(userOrID, User.User):
			userID = userOrID.id
		for player in self.players:
			if player.userID == userID:
				if player.isRobot:
					player.setRobot(False)
				else:
					player.setUserID(0)
		room = self.room
		if room:
			room.doUserLeave(userID)
		else:
			raise Warning('doKickUser error: no room')


	def onUserQuit(self, seat):
		''' 玩家离开游戏 '''

	def canQuitGameState(self):
		return self._isAbleGameState() or self.nnState == NNSTATE.SETTLE

	def onTimer(self, tid, uid):
		state = self._timers.get(tid)
		if state == None:
			return
		self._timers.pop(tid)
		self.delTimer(tid)
		if self.nnState != state:
			return
		state_func = {
			NNSTATE.NONE: self._onTimerNone,
			NNSTATE.BEGIN: self._onTimerBegin,
			NNSTATE.FAPAI: self._onTimerFapai,
			NNSTATE.QIANG: self._onTimerQiang,
			NNSTATE.BANKER: self._onTimerBanker,
			NNSTATE.YAZHU: self._onTimerYazhu,
			NNSTATE.FAPAISEC: self._onTimerFapaiSec,
			NNSTATE.SETTLE: self._onTimerSettle,
		}
		if state in state_func:
			state_func[state]()

	def _onTimerNone(self):
		''' 等待状态定时器 '''
		self._addGameTimer()
		if self._canStartGame():
			self.doWaitBegin()
			return 'doWaitBegin'
		for player in self.players:
			# 非机器人玩家
			if player.userID > 0 and not player.isRobot:
				self.useRobot()
				return
			# if random.random() > 0.6:
			# 	self.useRobot()


	def _onTimerBegin(self):
		self._tryStartGame()


	def _tryStartGame(self):
		if self._canStartGame():
			self.startGame()


	def _addGameTimer(self):
		timeout = TIMEOUT[self.nnState]
		self._timers[self.addTimer(timeout,0,0)] = self.nnState
		self.cutdown = timeout
		self._cutdownFrom = time.clock()

	def updCutdown(self):
		''' 更新倒计时 '''
		if self.cutdown > 0:
			return
		cutdownTo = time.clock()
		cutdown = self.cutdown + (self._cutdownFrom - cutdownTo)
		self._cutdownFrom = cutdownTo
		if self.cutdown < 0:
			self.cutdown = 0
			return
		self.cutdown = int(cutdown)


	# @supports_callbacks
	def onStart(self, seats=None):
		''' 开始游戏 '''
		self.nnState = NNSTATE.FAPAI
		self._addGameTimer()
		self._doFapai()
		self.room.onGameStarted()


	def onUserJoin(self, seat):
		''' 处理玩家加入 '''
		if self._canStartGame():
			self.doWaitBegin()


	def doWaitBegin(self):
		''' 等待开始游戏 '''
		if self.nnState != NNSTATE.NONE:
			self.reset()
		self.nnState = NNSTATE.BEGIN
		self._addGameTimer()


	@property
	def userCount(self):
		return len(tuple(self.seatedPlayers))

	def _doFapai(self):
		fapai = GameNNRule.fapai()
		assert next(fapai)
		for player in self._gamePlayers():
			player.doFapai(fapai.send(5))

	def _onTimerFapai(self):
		self.nnState = NNSTATE.QIANG
		self._addGameTimer()


	def _doQiang(self, seat, qiangRate):
		''' 执行抢庄 '''
		assert self.nnState == NNSTATE.QIANG
		assert self._players[seat].qiangRate == -1
		self._players[seat].qiangRate = qiangRate
		if -1 not in (v.qiangRate for v in self._ableQiangPlayers()):
			# 全都已抢，进入下一阶段
			self._onQiangEnd()

	def _onTimerQiang(self):
		for player in self._ableQiangPlayers():
			self._doQiang(player.seat, 0)


	def _ableQiangPlayers(self):
		for player in self._gamePlayers():
			if player.qiangRate == -1:
				yield player


	def _onQiangEnd(self):
		self._doSetBanker()


	def _doSetBanker(self):
		''' 执行定庄 '''
		self.nnState = NNSTATE.BANKER
		self._addGameTimer()
		maxRate = max(v.qiangRate for v in self._gamePlayers())
		candidate = []
		for seat in (v.seat for v in self._gamePlayers() if maxRate == v.qiangRate):
			candidate.append(seat)
		bankseat = random.choice(candidate)
		self.bankerSeat = bankseat
		self._players[bankseat].isBanker = 1
		self.bankerRate = maxRate or 1
		self.candidate = candidate


	def _onTimerBanker(self):
		for player in self._gamePlayers():
			player.qiangRate = -1
		self._toYazhuState()

	def _toYazhuState(self):
		self.nnState = NNSTATE.YAZHU
		self._addGameTimer()
		for player in self._gamePlayers():
			player.setMinYazhuAble(self.bankerRate)


	def _doYazhu(self, seat, yazhu):
		assert self.nnState == NNSTATE.YAZHU
		self._players[seat].yazhu = yazhu
		if not any(self._ableYazhus()):
			self._onYazhuEnd()
			
	def _ableYazhus(self):
		for player in self._gamePlayers():
			if self._canYazhu(player):
				yield player


	def _onTimerYazhu(self):
		for player in self._ableYazhus():
			player.reqGameNNYazhu()

	def _canYazhu(self, player):
		if player.gaming == 0:
			return
		return player.seat != self.bankerSeat and player.yazhu == -1

	def _onYazhuEnd(self):
		self.nnState = NNSTATE.FAPAISEC
		self._doFapaiSec()
		self._addGameTimer()
		self._doJudgeCardType()
		# self._addGameTimer()
		# 翻牌状态
		for player in self._gamePlayers():
			player.showState = 0


	def _doFapaiSec(self):
		for player in self._gamePlayers():
			player.doFapaiSec()

	def _doJudgeCardType(self):
		for player in self._gamePlayers():
			player.doCalCardType()

	def _onTimerFapaiSec(self):
		# 所有翻牌
		allPokers = [player.allPoker for player in self.players]
		for player in self._gamePlayers():
			player.doShowPoker(allPokers)
		self._doSettle()

	def _ableShowPoker(self):
		for player in self._gamePlayers():
			if player.showState == 0:
				yield player


	def _doSettle(self):
		''' 结算 '''
		self.nnState = NNSTATE.SETTLE
		self._addGameTimer()

		for player in self._gamePlayers():
			#print("update BroadcardTypeValue")
			player.BroadcardTypeValue = player.cardTypeValue
			#print(player.BroadcardTypeValue)
		bankWinValue = 0
		items = {}
		banker = self._players[self.bankerSeat]
		valBanker = banker.BroadcardTypeValue
		for player in self._gamePlayers():
			if player.seat != self.bankerSeat:
				val1 = player.BroadcardTypeValue
				winRate = GameNNRule.comparePoker(val1,valBanker)
				winValue = winRate * self.bankerRate * player.yazhu * self.baseScore
				bankWinValue -= winValue
				items[player.seat] = {'value':winValue}
		items[self.bankerSeat] = {'value':bankWinValue}
		settlement = {'items': []}
		for player in self._gamePlayers():
			item = items[player.seat]
			player.onSettled(item)
			item['seat'] = player.seat
			item['nick'] = player.nick
			settlement['items'].append(item)
		self.settlement = settlement


	def _onTimerSettle(self):
		''' 重置 '''
		self.reset()
		self._checkPlayers()
		self._tryStartGame()


	def _checkPlayers(self):
		''' 检查玩家状态能否继续留在房间 '''
		room = self.room
		for player in self.players:
			if player.userID == 0:
				continue
			if player.clearUserOffline():
				''' 玩家离线踢出玩家 '''
				continue
			if not room.isGoldEnough(player.gold):
				''' 金币不足踢出玩家 '''
				user = player._user()
				assert user, 'user is None'
				self.doKickUser(user)
				user.sendMsgTips(0, '金币不足, 请选择其他场次')


	def _gamePlayers(self):
		''' 游戏中的玩家 '''
		for player in self.players:
			if player.gaming > 0:
				yield player

	def _ableQiangPlayer(self):
		for player in self._gamePlayers():
			if self._canPlayerQiang(player):
				yield player

	def _canPlayerQiang(self, player):
		return player.qiangRate == -1


	def _isAbleGameState(self):
		''' 能否开始游戏的状态 '''
		return self.nnState in (NNSTATE.NONE, NNSTATE.BEGIN)


	def _canStartGame(self):
		if not self._isAbleGameState():
			return False
		if self.userCount >= USER_MIN_COUNT:
			return True

	def _canJoinGame(self):
		''' 能否加入游戏 '''
		if not self._isAbleGameState():
			return False
		if self.userCount < MAX_SEAT:
			return True

	def userPlayers(self):
		''' 真实玩家 '''
		for player in self.players:
			if player.userID > 0 and not player.isRobot:
				yield player


	def _testCase(self, user):
		self.reset()
		yield
		if not self._canStartGame():
			self.useRobot()
		yield
		self.startGame()
		yield
		ableQiangs = self._ableQiangPlayer()
		ableYazhus = self._ableYazhus()
		_ableShowPoker = self._ableShowPoker()
		while True:
			if self.nnState == NNSTATE.QIANG:
				p = next(ableQiangs)
				if p:
					p.reqGameNNQiang(random.randint(0, 3))
			elif self.nnState == NNSTATE.YAZHU:
				p = next(ableYazhus)
				if p:
					p.reqGameNNYazhu()
			elif self.nnState == NNSTATE.FAPAISEC:
				p = next(_ableShowPoker)
				if p:
					p.reqGameNNShowPoker()
			elif self.nnState == NNSTATE.SETTLE:
				yield
				self.reset()
				yield
				self.startGame()
				ableQiangs = self._ableQiangPlayer()
				ableYazhus = self._ableYazhus()
				_ableShowPoker = self._ableShowPoker()
			yield


''' 
KBEngine.reloadScript(True)
import User
game = User.get('GameNN')
t = game._testCase()
print(next(t))
'''

def newCase():
	game = KBEngine.globalData["Hall_cell"]._create('GameNN')
	print(game)
	return game


