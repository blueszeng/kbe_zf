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
import URL
import d_default_nick
from Functor import *


importlib.reload(wxCharge)
importlib.reload(httpHelper)

def getRandomNick(uid):
	newNick = random.choice(d_default_nick.name1)
	return newNick + str(uid)


MAX_LOGINMEMO = 6*4


# 用户信息部分
class UserInfo:
	def __init__(self):
		self._memoIDs = {}
		self.uid = self.databaseID
		self.cellData['uid'] = self.uid
		loginData = self.getClientDatas()[0]
		datas = json.loads(loginData.decode("utf-8"))
		loginType = datas[0]
		data = len(datas) > 1 and datas[1] or ''
		# if len(data) > 0 and self.userInfoFlag == data:
		# 	return
		self.accountType = loginType
		self.accountData = data
		if loginType == 'wx_login_code':
			self.initWxUserInfo(data)
		elif loginType == 'nick_login':
			self.cellData['nick'] = self.__ACCOUNT_NAME__
			self.userInfoFlag = data
		elif loginType == 'phone':
			# self._hall
			self.account = self.__ACCOUNT_NAME__
			self.phone = data
			self.cellData['nick'] = self._initPhoneNick(data)
			self.userInfoFlag = data
			self.initAgentUser(data)
		else:
			if not self.cellData['nick'] or self.cellData['nick'] == '':
				self.cellData['nick'] = getRandomNick(self.uid)
			# logw('init', loginType, data)


	def _initPhoneNick(self, phone):
		''' 修改昵称为手机号并加入*，在更换手机后昵称会重置 '''
		if len(phone) == 11:
			s1 = phone[0:3]
			s2 = '****'
			s3 = phone[7:11]
			return str('').join( [s1, s2, s3] )
		return phone

	def saveLoginMemo(self):
		''' 保存登录记录 '''
		memo = {
			'id': self._getMemoID('loginMemo', len(self.loginMemo)),
			'time': int(time.time()),
			'ip': self.loginIP}
		self.loginMemo.append(memo)
		if len(self.loginMemo) > MAX_LOGINMEMO:
			self.loginMemo.pop(0)
			self.loginMemo = self.loginMemo


	def reqGetLoginMemo(self, curIdx, page):
		''' 获取登录记录 '''
		start = curIdx*page
		to = start + page
		total = len(self.loginMemo)
		if to > total:
			to = total
		items = []
		for idx in range(start, to):
			items.append(self.loginMemo[total-idx-1])
		if self.client:
			self.client.onGetLoginMemo(curIdx, total, items)
		


	def initWxUserInfo(self, token):
		''' 初始化微信用户信息 '''
		url = "https://api.weixin.qq.com/sns/userinfo?%s=%s&&%s=%s"%(
			'access_token', token,
			'openid', self.__ACCOUNT_NAME__
		)
		logi("url", url)
		httpHelper.httpFetch(url, self.onWxGotUserInfo)


	def initAgentUser(self, phone):
		agentUser = KBEngine.createBaseLocally('AgentUser', {
				'userdbid': self.databaseID,
				'playerid': self.__ACCOUNT_NAME__,
				'goldTotal_nn': 0,
				'timesTotal_nn': 0,
			})
		agentUser.writeToDB()
		self.agentdbid = agentUser.databaseID
		logi('self.agentdbid', self.agentdbid)

		# self._hall.saveAgentUserInfo({
		# 	'playerid': self.__ACCOUNT_NAME__,
		# 	'account': self.__ACCOUNT_NAME__,
		# 	'dbid': self.databaseID})

	@property
	def agentUser(self):
		if self.agentdbid:
			return KBEngine.createBaseFromDBID('AgentUser', self.agentdbid)


	def onWxGotUserInfo(self, data):
		''' 得到微信用户信息 '''
		logi('onWxGotUserInfo', data)
		self.userInfoFlag = token
		self.accountData = data
		if hasattr(self, 'cellData') and self.cellData:
			self.cellData['accountDataCell'] = data
		else:
			self.cell.doUpdAccountData(data)


	def onGetQuickOrder(self, data):
		if data['error'] == '1':
			self._curChargeID = data['orderid']
			self.client.onGotChargeUrl(data['msg'])
			logi('1111', data['msg'])
		else:
			logi('1111', data)



	def reqChargeOrder(self, chargeType, chargeNum):
		''' 请求支付订单 '''
		logi('reqChargeOrder', chargeType, chargeNum)
		assert chargeNum > 0
		if not hasattr(self, '_chargeId'):
			self._chargeId = 10
		self._chargeId += 1
		self._curChargeID = str(self.uid*10000 + self._chargeId)
		self._curChargeNum = int(chargeNum)
		# self._curChargeNum = int(1)
		self._curChargeType = chargeType
		if chargeType == 3:
			''' GM支付 '''
			self.cell.reqChargeGold(chargeNum, self._curChargeID)
			return
		if chargeType == 2:
			''' 快捷支付 '''
			httpHelper.fetch(httpHelper.post(URL.WEB_reqChargeOrder,
				playerid=self.__ACCOUNT_NAME__,
				tranAmt=chargeNum,
				acct_no="6214832800617412",
				), self.onGetQuickOrder, encode='GBK')
			return
		if chargeType == 1:
			''' 微信支付 '''
			wxCharge.unifiedorder(self._curChargeID, self._curChargeNum, self.onGotChargeOrder)

	
	def onGotChargeOrder(self, isSuccess, info):
		logi('onGotChargeOrder',isSuccess, info)
		if isSuccess:
			self.client.onChargeOrder(
				info['partnerid'], 
				info['prepayid'], 
				info['noncestr'], 
				info['sign'], 
				info['timestamp']
			)


	def _getMemoID(self, memoName, default):
		'''得到记录id'''
		curID = self._memoIDs.get(memoName, default)
		self._memoIDs[memoName] = curID + 1
		return self.databaseID*1000 + self._memoIDs[memoName]


	def reqGetChargeResult(self, tradeNo):
		''' 得到支付结果 '''
		if len(tradeNo) == 0:
			tradeNo = self._curChargeID
		assert len(tradeNo) > 0
		assert self._curChargeNum
		if self._curChargeType == 2:
			httpHelper.fetch(httpHelper.post(URL.WEB_reqGetChargeResult,
				orderid=tradeNo,
				), self._onGotChargeResult)
		elif self._curChargeType == 1:
			wxCharge.queryResult(tradeNo, self._onGotChargeResult)


	def _onGotChargeResult(self, isSuccess, state=0):
		''' 得到支付结果 '''
		if not self._curChargeID:
			return
		if self._curChargeType == 2:
			self.cell.reqChargeGold(self._curChargeNum, self._curChargeID)
			self.sendToClient('onGotChargeResult', isSuccess)
		elif isSuccess:
			if state == 'SUCCESS':
				self.cell.reqChargeGold(wxCharge.converToGold(self._curChargeNum), self._curChargeID)
				self._curChargeID = ''
				self._curChargeNum = None
			self.sendToClient('onGotChargeResult', state)

	def onChargeResult(self, result, chargeID):
		''' 保存充值记录 '''
		# memo['id'] = self.databaseID*1000 + len(self.chargeMemo)+1
		assert chargeID == self._curChargeID
		if not self._curChargeID:
			return
		self.chargeMemo.append({
			'id': self._curChargeID,
			'num': self._curChargeNum,
			'charge': self._curChargeType,
			'time': int(time.time()),
			'state': result,
		})
		self._curChargeID = None
		self._curChargeNum = None
		self._curChargeType = None
		self.chargeMemo = self.chargeMemo


	def doSaveChargeMemo(self, memo):
		''' 保存充值记录 '''
		# memo['id'] = self.databaseID*1000 + len(self.chargeMemo)+1
		self.chargeMemo.append(memo)
		self.chargeMemo = self.chargeMemo

	def reqChargeMemo(self, idx, count):
		''' 请求获取充值记录 '''
		start = idx*count
		to = start + count
		total = len(self.chargeMemo)
		if to > total:
			to = total
		items = []
		logd('start to', start, to, total)
		for i in range(start, to):
			items.append(self.chargeMemo[total-i-1])
		self.client.onChargeMemo(idx, total, items)
	

	def onSaveGoldDrawMemo(self, num):
		''' 保存金币取现 '''
		self._goldDrawMemo.append({
			'id': str(self._getMemoID('_goldDrawMemo', len(self._goldDrawMemo))),
			'time': int(time.time()),
			'num': num,
			'state': 1,
		})
		self._goldDrawMemo = self._goldDrawMemo


	def reqGoldDrawMemo(self, idx, page):
		''' 请求获取金币取现记录 '''
		total, items = self._getListPage('_goldDrawMemo', idx, page)
		self.client.reqGoldDrawMemo(idx, total, items)


	def reqAgentDraw(self, num):
		''' 佣金取现 '''
		def _getAgentMoney(data):

			if data['error'] == 1:
				self._agentDrawMemo.append({
					'id': str(self._getMemoID('_agentDrawMemo', len(self._agentDrawMemo))),
					'time': int(time.time()),
					'num': num,
					'state': 1,
				})
				self.client.reqAgentDraw(0, '')
			else:
				self.client.reqAgentDraw(data['error'], '查询错误')
		
		httpHelper.fetch(httpHelper.post(URL.WEB_reqAgentDraw,
				playerid=self.__ACCOUNT_NAME__,
				money=num
				), _getAgentMoney)


	def reqAgentDrawMemo(self, idx, page):
		''' 请求获取金币取现记录 '''
		total, items = self._getListPage('_agentDrawMemo', idx, page)
		self.client.reqAgentDrawMemo(idx, total, items)



