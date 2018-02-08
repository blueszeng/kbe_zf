#!/usr/bin/env python
# -*- coding: utf-8 -*-\

import KBEngine
from KBEDebug import *
from Functor import *


class KbeCallback:
	''' 基于kbe的事件回调，通过entity查找和函数名来监听和触发
		通过注册方法来实现远程回调
	 '''
	def __init__(self):
		self._kbecallbacks = []
		self._onceCallbacks = {}

	def addKbeCallback(self, eventName, eid, callbackName):
		logd('addKbeCallback:', eventName, eid, callbackName)
		self._kbecallbacks.append((eventName, eid, callbackName))

	def onceKbe(self, eventName, mailBox, callbackName):
		''' 一次事件监听 '''
		logd('onceKbe:', eventName, mailBox, callbackName)
		if not self._onceCallbacks.get(eventName):
			self._onceCallbacks[callbackName] = []
		self._onceCallbacks[callbackName].append((mailBox, callbackName))


	def kbeFire(self, eventName, *args):
		logd('kbeFire:', eventName, *args)
		for name, eid, callbackName in self._kbecallbacks:
			if eventName == name:
				self._doCall(eid, callbackName, *args)
		if self._onceCallbacks.get(eventName):
			for mailBox, callbackName in self._onceCallbacks[eventName]:
				getattr(mailBox, callbackName)(*args)
			self._onceCallbacks[eventName] = []
	

	def _doCall(self, eid, callbackName, *args):
		entity = KBEngine.entities.get(eid)
		if entity:
			try:
				eval('entity.'+callbackName)(*args)
			except Exception as identifier:
				logw('_doCall: error', identifier)

	def removeKbeCallback(self, eventName, eid, callbackName):
		logd('removeKbeCallback:', eventName, eid, callbackName)
		callback = (eventName, eid, callbackName)
		if callback in self._kbecallbacks:
			self._kbecallbacks.remove(callback)



