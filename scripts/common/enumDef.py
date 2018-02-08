# -*- coding: utf-8 -*-


# 房间状态枚举
class RoomState:
	noReady = 1
	waiting = 2
	fulled = 3
	gaming = 4


GAME_NAME_TYPE = {
	'GameNN': 1
}
GAME_TYPE_NAME = {
	1: 'GameNN'
}

''' 牛牛匹配场次配置 '''
MATCH_NN_INFOS = [
	{
		'gameLevel': 0,
		'baseScore': 1,
		'goldMin': 100,
		'goldMAX': 1000,
	},
	{
		'gameLevel': 1,
		'baseScore': 10,
		'goldMin': 1000,
		'goldMAX': 10000,
	},
	{
		'gameLevel': 2,
		'baseScore': 100,
		'goldMin': 10000,
		'goldMAX': 100000,
	},
	{
		'gameLevel': 3,
		'baseScore': 1000,
		'goldMin': 100000,
		'goldMAX': 1000000,
	},
]


GAMENAME_MATCH = {
	'GameNN': MATCH_NN_INFOS
}
