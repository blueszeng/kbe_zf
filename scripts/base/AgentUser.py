# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import random
import Math
import importlib
import json
import time
import httpHelper
import wxCharge
import d_default_nick
from Functor import *


importlib.reload(wxCharge)

def getRandomNick(uid):
	newNick = random.choice(d_default_nick.name1)
	return newNick + str(uid)


MAX_LOGINMEMO = 6*4


# 代理玩家信息
class AgentUser(KBEngine.Base):
	def __init__(self):
		pass

	def initAgentUser(self, playerid):
		
		
		self._hall.saveAgentUserInfo({
			'playerid': playerid, 
			'account': self.__ACCOUNT_NAME__, 
			'dbid': self.databaseID})

		def onWriteToDB(self,celldata):
			self.user.agentdbid = databaseID

		@property
		def user(self):
			if self.userid:
				return KBEngine.createBaseFromDBID('user', self.userid)

