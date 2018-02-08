# -*- coding: utf-8 -*-
import KBEngine
import Functor
from KBEDebug import *

import enumDef


def canJoin(room):
	return room and room.roomState == 2


class Room(KBEngine.Base):
	def __init__(self):
		KBEngine.Base.__init__(self)

		# 请求在cellapp上创建cell空间
		self.createInNewSpace(None)
		

	def doCreateGame(self):
		self.cell.reqCreateGame(self.gameName, self.gameLevel)

	def doEnter(self, entity):
		pass

	def onGetCell(self):
		''' 创建cell完成 '''
		print("Room onGetCell", self.id)
		''' 通知大厅 '''
		self.doCreateGame()
		KBEngine.globalData["Hall"].onRoomCreated(self.id)


	def setRoomState(self, roomState):
		print('setRoomState', self.id, roomState)
		self.roomState = roomState



