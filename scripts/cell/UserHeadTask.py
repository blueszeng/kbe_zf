# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from Functor import *
import importlib
import time
import datetime


# importlib.reload(wxCharge)

# 任务类型配置
class TASK_TYPE:
	FIRST_LOGIN= 1
	CHARGE_TIMES= 1
	CHARGE_NUM	= 2
	DRAW_PASS	= 3
	GAME_TIMES	= 4
	WIN_TIMES 	= 5
	WIN_GOLDS	= 6
	LOGIN_DAYS	= 7

# 任务条件配置
TASK_CONDITIONS = [
	(TASK_TYPE.FIRST_LOGIN	, 1)	, #首次登录
	(TASK_TYPE.CHARGE_TIMES	, 1)	, #充值次数
	(TASK_TYPE.CHARGE_NUM	, 2000)	, #充值数量
	(TASK_TYPE.DRAW_PASS	, 1)	, #修改取款密码

	(TASK_TYPE.GAME_TIMES	, 3)	, #总游戏次数
	(TASK_TYPE.WIN_TIMES	, 2)	, #游戏赢的次数
	(TASK_TYPE.WIN_GOLDS	, 2000)	, #赢取金币数量

	(TASK_TYPE.LOGIN_DAYS	, 2)	, #登录天数
]


# 用户头像任务
class UserHeadTask:
	def __init__(self):
		pass
		# self.addKbeCallback('reqChargeGold', self.id, 'onTaskCharge')

	def initHeadTask(self):
		if not self.taskProgress or len(self.taskProgress) < len(TASK_CONDITIONS):
			tasks = []
			for idx, task in enumerate(TASK_CONDITIONS):
				clear = 0
				if task[0] == TASK_TYPE.FIRST_LOGIN:
					clear = 1
				tasks.append({
					'id':idx, 
					'clear':clear,
					'type':task[0], 
					'goal':task[1], 
					'had':0})
			self.taskProgress = tasks
		self.updUserHeads()


	def onTaskCharge(self, num):
		self._addTaskProgress(TASK_TYPE.CHARGE_NUM, num)
		self._addTaskProgress(TASK_TYPE.CHARGE_TIMES, 1)

	def onGameEnd(self, win):
		self._addTaskProgress(TASK_TYPE.GAME_TIMES, 1)
		if win > 0:
			self._addTaskProgress(TASK_TYPE.WIN_TIMES, 1)
			self._addTaskProgress(TASK_TYPE.WIN_GOLDS, win)

	def onTaskChangeGoldPass(self):
		self._addTaskProgress(TASK_TYPE.DRAW_PASS, 1)

	def onTaskLogined(self):
		self.initHeadTask()
		curtime = time.time()
		if hasattr(self, 'lastLoginTime'):
			if time.strftime("%Y-%m-%d", 
				time.localtime(curtime)) == time.strftime("%Y-%m-%d", time.localtime(self.lastLoginTime)):
				return
		self.lastLoginTime = int(curtime)
		self._addTaskProgress(TASK_TYPE.LOGIN_DAYS, 1)

	def _addTaskProgress(self, tType, num):
		logd('_addTaskProgress', len(self.taskProgress), tType, num)
		needUpd = 0
		for idx, task in enumerate(self.taskProgress):
			if tType == task['type']:
				if task['had'] < task['goal']:
					task['had'] += num
					needUpd += 1
					if task['had'] >= task['goal']:
						self.updUserHeads()
						logi('self.headids', self.headids)
		if needUpd > 0:
			self.taskProgress = self.taskProgress


	def updUserHeads(self):
		old = ''
		for idx, task in enumerate(self.taskProgress):
			old += str(self.isTaskAchieve(idx))
		self.headids = old
		if not hasattr(self, 'head') or len(self.head) == 0:
			self.head = '0'


	def isTaskAchieve(self, idx):
		task = self.taskProgress[idx]
		if task['clear']:
			return 2
		if task['goal'] <= task['had']:
			return 1
		return 0


	def reqUnlockHead(self, eid, idx):
		''' 请求解锁头像 '''
		if self.headids[idx] == '0':
			return self.client.reqUnlockHead('没有完成任务')
		self.taskProgress[idx]['clear'] = 1
		self.updUserHeads()
		self.client.reqUnlockHead('')

	def reqChangeFace(self, eid, idx):
		''' 请求更换头像 '''
		if self.headids[idx] != '2':
			return self.client.reqChangeFace('尚未拥有该头像')
		self.head = str(idx)
		self.client.reqChangeFace('')
