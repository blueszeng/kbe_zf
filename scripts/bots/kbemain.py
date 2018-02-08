# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import test

def onInit(isReload):
	"""
	KBEngine method.
	当引擎启动后初始化完所有的脚本后这个接口被调用
	@param isReload: 是否是被重写加载脚本后触发的
	@type isReload: bool
	"""
	DEBUG_MSG('onInit::isReload:%s' % isReload)

	KBEngine.callback(10, update)

def onStart():
	"""
	KBEngine method.
	在onInitialize调用之后， 准备开始游戏时引擎调用这个接口.
	"""
	
	

def update():
	logd('update')
	test.step()
	KBEngine.callback(1, update)


def onFinish():
	"""
	KBEngine method.
	客户端将要关闭时， 引擎调用这个接口
	可以在此做一些游戏资源清理工作
	"""
	pass
