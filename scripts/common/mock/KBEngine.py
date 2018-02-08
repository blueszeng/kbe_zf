# -*- coding: utf-8 -*-

# 模拟 kbe 环境, 用于单元测试


from collections import defaultdict


class MockProp(dict):
	def __init__(self, name='MockProp'):
		self.__dict__ = self
		# self.__dict__._dict = defaultdict(dict)
		self.__dict__.name = name

	def __getattr__(self, name):
		# return self.__dict__._dict[name]
		return MockProp(name)

	def __repr__(self):
		return self.__dict__.name


class TestObj(dict):
	def __init__(self, default=None):
		self.__dict__ = self
		self.__dict__._dict = defaultdict(default)

	def __getattr__(self, name):
		return self.__dict__._dict[name]


class Entity:
	def __init__(self):
		print('mock Entity init')
		self.id = 233
		self.spaceID = 666
		self.position = []
		self.direction = ''
	
	# def __getattr__(self, name):
	# 	return MockProp(name)

	def addTimer(self, *args):
		print("mock: addTimer", args)
		id = 1024
		# self.onTimer(id, 0)
		return id
	
	def delTimer(self, *args):
		pass
	


cellAppData = defaultdict(dict)

def createEntity(className, *args):
	mdl = __import__(className)
	clsObj = getattr(mdl, className)
	return clsObj()

def publish():
	return False

LOG_TYPE_NORMAL = 'LOG_TYPE_NORMAL'
LOG_TYPE_DBG = 'LOG_TYPE_DBG'
LOG_TYPE_INFO = 'LOG_TYPE_INFO'
LOG_TYPE_WAR = 'LOG_TYPE_WAR'
LOG_TYPE_ERR = 'LOG_TYPE_ERR'
def scriptLogType(*args):
	pass