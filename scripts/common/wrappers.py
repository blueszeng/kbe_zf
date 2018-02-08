#!/usr/bin/env python
# -*- coding: utf-8 -*-\

from Functor import *


def client_req(func):
	''' 同名客户端回应函数装饰器
		@client_req
		def reqXX(self):
			return 1, '错误'
		等效于：
		def reqXX(self):
			if self.hasWitness:
				self.client.reqXX(1, '错误')
			
	'''
	def newFunc(self, *args, **kwargs):
		resps = func(self, *args, **kwargs)
		if resps == None:
			return
		if hasattr(self, 'hasClient') and not self.hasClient:
			return
		if hasattr(self, 'hasWitness') and not self.hasWitness:
			return
		if not isinstance(resps, tuple):
			resps = (resps, )
		callfunc = getattr(self.client, func.__name__)
		callfunc(*resps)
	return newFunc


# def client_req():
# 	''' 同名客户端回应函数装饰器 '''
# 	return req_resp(None, 'toClient')

# print(client_req()(print))
