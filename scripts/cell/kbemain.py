# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

def onInit(isReload):
	"""
	KBEngine method.
	当引擎启动后初始化完所有的脚本后这个接口被调用
	"""
	DEBUG_MSG('onInit::isReload:%s' % isReload)

	KBEngine.cellAppData[ "rooms" ] = {}

	# 在这里重新载入模块
	if isReload:
		for e in KBEngine.entities.values():
			if hasattr(e, 'onLoad'):
				print('reload:', e)
				e.onLoad()
	

def countGamingRoom():
	return sum(1 for e in rooms() if e.isGaming())

def countUserOnline():
	return sum(1 for e in users() if e.hasClient)

def users():
	for e in entities():
		if e.className=='User':
			yield e

def countRooms():
	return countIter(rooms())

def rooms():
	for e in entities():
		if e.className=='Room':
			yield e

def entities():
	for e in KBEngine.entities.values():
		yield e

def countIter(iterObj):
	count = 0
	try:
		for it in iterObj:
			count += 1
	finally:
		pass
	return count
	
def onGlobalData(key, value):
	"""
	KBEngine method.
	globalData改变 
	"""
	DEBUG_MSG('onGlobalData: %s' % key)
	
def onGlobalDataDel(key):
	"""
	KBEngine method.
	globalData删除 
	"""
	DEBUG_MSG('onDelGlobalData: %s' % key)

def onCellAppData(key, value):
	"""
	KBEngine method.
	cellAppData改变 
	"""
	DEBUG_MSG('onCellAppData: %s' % key)
	
def onCellAppDataDel(key):
	"""
	KBEngine method.
	cellAppData删除 
	"""
	DEBUG_MSG('onCellAppDataDel: %s' % key)
	
def onSpaceData( spaceID, key, value ):
	"""
	KBEngine method.
	spaceData改变
	"""
	pass
	
def onAllSpaceGeometryLoaded( spaceID, isBootstrap, mapping ):
	"""
	KBEngine method.
	space 某部分或所有chunk等数据加载完毕
	具体哪部分需要由cell负责的范围决定
	"""
	pass