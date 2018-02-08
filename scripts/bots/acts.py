# -*- coding: utf-8 -*-

from behave import condition, action, FAILURE, forever, repeat, failer
import random
# import KBEngine
# from KBEDebug import *


randomActs = {
	'reqGetMatchInfos': [
		lambda r: r.base.reqGetMatchInfos,
		[
			lambda : 1,
		]
	],
}

@condition
def isNotInRoom(u):
	return not u.room

@action
def reqStartGame(u):
	u.base.reqStartGame('GameNN', 0)

@condition
def canQuitRoom(u):
	return u.game and u.game.nnState in [0,1,7]

@action
def reqQuitRoom(u):
	u.cell.reqQuitRoom( u.room.id )

@action
def reqChangeRoom(u):
	return u.cell.reqChangeRoom()

@condition
def randomDo(*a):
	return random.choice([1, 0,0,0]) == 1

@action
def reqGetGoldRank(u):
	return u.base.reqGetGoldRank()

@action
def reqGetMatchInfos(u):
	return u.base.reqGetMatchInfos(1)

@action
def reqChargeMemo(u):
	return u.base.reqChargeMemo(1, 5)

@action
def reqChargeGold(u):
	return u.cell.reqChargeGold(random.randint(1,1000))

@action
def reqNewRoomID(u):
	return u.base.reqNewRoomID()

norGame = (
    randomDo >> isNotInRoom >> reqStartGame
	| randomDo >> canQuitRoom >> reqQuitRoom
	| randomDo >> canQuitRoom >> reqChangeRoom
	# | randomDo >> reqGetGoldRank
	| randomDo >> reqGetMatchInfos
	| randomDo >> reqChargeMemo
	| randomDo >> reqChargeGold
)

bubbling = (
	randomDo >> reqGetMatchInfos
	| randomDo >> reqChargeGold
    | randomDo >> isNotInRoom >> reqStartGame
	| randomDo >> canQuitRoom >> reqQuitRoom
	| randomDo >> canQuitRoom >> reqChangeRoom
	| randomDo >> reqGetGoldRank
	| randomDo >> reqChargeMemo
)

def doRandomAct(rob):
	caller, args = randomActs['reqGetMatchInfos']
	return caller(rob)(*[v() for v in args])


