# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import random
import Math
import importlib
import wrappers
import json
import time
import httpHelper
from Functor import *


importlib.reload(wrappers)
importlib.reload(httpHelper)


# 用户信息部分
class UserInfo:
	def __init__(self):
		pass

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


	@wrappers.client_req
	def reqGoldDraw(self, eid, num, password):
		''' 金币取现 '''
		if not num or num < 0:
			return 1, '不合法请求'
		if self.gold < num:
			return 2, '金币不足'
		if not self.isSameSafePassword(password):
			return 2, '密码不正确'
		if not self._bankInfo or self._bankInfo['bankNum'] == '':
			return 3, '未绑定银行卡'
		self.cell.doChangeGold(num, self.gold+num)
		self.onSaveGoldDrawMemo(num)
		return 0, ''

	@wrappers.client_req
	def reqBindBankCard(self, eid, name, bank, bankNum):
		''' 绑定银行卡信息 '''
		self._bankInfo = {
			'name': name,
			'bank': bank,
			'bankNum': bankNum,
		}
		return 0, ''

	@wrappers.client_req
	def reqAgentDraw(self, num, password):
		''' 代理取現 '''
		if not num or num < 0:
			return 1, '不合法请求'
		if not self.isSameSafePassword(password):
			return 2, '密码不正确'
		if not self._bankInfo or self._bankInfo['bankNum'] == '':
			return 3, '未绑定银行卡'
		httpHelper.fetch('', {
			'playerid': self.account
		})
		return 0,''

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

