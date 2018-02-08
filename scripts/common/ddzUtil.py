# -*- coding: utf-8 -*-

"""
斗地主算法
3-14: 3-A 16:2 17: 小王, 18 大王
"""
from Functor import *
import random
from Poker import *
from functools import reduce


# 整副牌
allPoker = Poker()
for idx, rank in enumerate(CardEnum.nums):
	maxColor = CardEnum.colors[idx]
	for color in range(0, maxColor):
		allPoker.append(rank*10+color)


def copyAllPoker():
	return allPoker.copy()


def dealPokers():
	''' 洗牌并发牌 '''
	cards = copyAllPoker
	random.shuffle(cards)
	count = int((len(cards)-3)/3)
	pokers = {}
	for idx in range(0, 3):
		pokers[idx] = cards[idx*count:(idx+1)*count]
	return pokers, cards[-3:]

p = (3, 13)
n = (1, 13)
m = (5, 13)
EnableCfg = {
	(1, 1, 0, 0, -1)	: 1,	#''' 单 '''
	(1, m, 0, 0, -1)	: 2,	#''' 顺子 '''
	(2, 1, 0, 0, -1)	: 3,	#''' 对 '''
	(2, p, 0, 0, -1)	: 4,	#''' 连对 '''
	(3, 1, 0, 0, -1)	: 5,	#''' 三不带 '''
	(3, n, 1, n, -1)	: 6, 	#''' 三带一 '''
	(3, n, 2, n, -1)	: 7, 	#''' 三带二 '''
	(4, n, 1, n, -1)	: 8, 	#''' 三带二 '''
	(4, n, 2, n, -1)	: 9, 	#''' 三带二 '''
	(4, 1, 0, 0, -1)	: 10, 	#''' 炸弹 '''
	(1, 1, 1, 1,170)	: 11,	#''' 王炸 '''
}

def isEnableByTypeFeature(height, width, tailHeight, tailLen, rank):
	''' 由 TypeFeature 判断合法牌型 '''
	for (height_, hLen_, tailHeight_, tailLen_, rank_), tID in EnableCfg.items():
		if hLen_ is tailLen_ and tailLen_ is n:
			''' 要求数量相等并限制数量 '''
			if width != tailLen or width not in range(*n):
				continue
		elif hLen_ is m or hLen_ is p:
			''' 限制数量 '''
			if width not in range(*hLen_):
				continue
		else:
			if width != hLen_ or tailLen != tailLen_:
				continue
		if rank_ != -1:
			''' 限制 rank '''
			if rank_ != rank:
				continue
		if height == height_ and tailHeight == tailHeight_:
			return (height, width, tailHeight, tailLen, rank, tID)


def isEnableByPoker(poker=None, ranks=None):
	''' 能否组合出合法的出牌 '''
	if poker:
		ranks = poker.ranks
	for minH in [4,3,2,1]:
		maxIdxs = getMaxSubTypeSizeIdxs(ranks, minH)
		for width in range(len(maxIdxs), 0, -1):
			for idxs in getSubIdxsByWidth(maxIdxs, width):
				ret = checkAfterFiterIdxs(ranks, minH, idxs)
				if ret:
					return ret


def getMaxSubTypeSizeIdxs(ranks, height=4):
	''' 得到某高度的最大宽度列索引表 '''
	maxIdxs = []
	for idx, h in ranks.items():
		if h >= height and (len(maxIdxs) == 0 or maxIdxs[-1] == idx - 1):
			maxIdxs.append(idx)
	return maxIdxs


def checkAfterFiterIdxs(ranks, height, idxs):
	''' 检查剔除对应高度和列之后的牌型 '''
	remain = fiterRanks(ranks, height, idxs)
	width, tailH, tailLen = len(idxs), 0, 0
	if False not in [(x == 2 or x == 4) for x in remain]: # 是否全是对子
		tailLen = remain.count(2) + remain.count(4) * 2
		if tailLen > 0: tailH = 2
	else:
		tailLen = reduce(lambda x, y: x + y, remain)
		if tailLen > 0: tailH = 1
	return isEnableByTypeFeature(height, width, tailH, tailLen, idxs[0])


def fiterRanks(ranks, height, idxs):
	return [a-height if i in idxs else a for (i, a) in ranks.items()]

def dictFiterRanks(ranks, height, idxs):
	newRanks = {}
	for k, v in ranks.items():
		newRanks[k] = v
		if k in idxs:
			newRanks[k] = v-height
	return newRanks


def isEnableDiscard(poker, target):
	''' 比较是否是合法的出牌 '''
	myRanks = poker.ranks
	if isBomb(poker) and not isBomb(target):
		return True
	typeFeature = isEnableByPoker(target)
	if not typeFeature:
		return False
	height, width, tailH, tailLen, rank, val = typeFeature
	idxs = getMaxSubTypeSizeIdxs(myRanks, height)
	if len(idxs) == 0:
		return False
	ret = checkAfterFiterIdxs(myRanks, height, idxs)
	if not ret:
		return False
	_, _, _, _, myRank, _ = ret
	return myRank > rank


def isBomb(poker):
	''' 是否是炸弹 '''
	if len(poker) == 2:
		if KING1 in poker and KING2 in poker:
			return True
	if len(poker) == 4 and False not in [poker[0] == x for x in poker]:
		return True


def matchEnableDiscard(poker, targetPoker):
	''' 匹配合法的出牌 '''
	myRanks = poker.ranks
	typeFeature = isEnableByPoker(targetPoker)
	height, width, tailH, tailLen, rank, val = typeFeature
	for idxs in getMatchIdxsByHeightWidth(myRanks, height, width):
		if idxs[0] <= rank:
			continue
		remain = dictFiterRanks(myRanks, height, idxs)
		if tailH == 0:
			return getSubPokerByIdxsAndHeight(poker, idxs, height)
		tailPoker = getSubTailPokerByCount(poker, remain, tailH, tailLen)
		if tailPoker:
			return tailPoker + getSubPokerByIdxsAndHeight(poker, idxs, height)


def getMatchIdxsByHeightWidth(ranks, height, width):
	for rank, h in ranks.items():
		for i in range(0, width):
			if ranks.get(rank+i, 0) < height:
				break
			if i == width - 1:
				yield [rank for rank in range(rank, rank+width)]


def getSubPokerByIdxsAndHeight(poker, idxs, height):
	sub = []
	for idx in idxs:
		cards = [card for card in poker if idx == Card(card).rank]
		sub += cards[0:height]
	return sub


def getSubIdxsByWidth(idxs, width):
	''' 查找矩形 idsx 内 width宽度的子区域 '''
	for i in range(0, len(idxs) - width +1):
		yield idxs[i:width+i]

def getSubTailPokerByCount(poker, ranks, height, count):
	sub = []
	for hLimit in range(height, 5):
		for idx in findIdxByHeight(ranks, height):
			sub += getSubPokerByIdxsAndHeight(poker, [idx], height)
			if len(sub) == count*height:
				return sub


def findIdxByHeight(ranks, height):
	''' 查找包含指定高度的idx '''
	for idx in [i for i,v in ranks.items() if v == height]:
		yield idx
	
	


if __name__ == '__main__':
	tests = [
		[1],
		[2],
		[3],
		[2,2,2],
		[1,1,1,1,1],
		[1,4,3,3,0,1],
		[1,4,3,3,0],
		[4,4,4,4],
		[1,4,3,4,3],
		[1,1,0,2,1,1],
		[0,0,4,4,3,3,3,3],
	]
	with UsedTime():
		for item in tests*1:
			ret = isEnableByPoker(ranks={k:v for k,v in enumerate(item)})
			print(item, ret)
	
	pokers,p = dealPokers()
	poker1 = Poker(Poker(pokers[0]))
	# poker1 = Poker([50,50,50, 40,40,40, 30,60,60,80])
	# poker1 = Poker([50,50,50,50])
	poker1.fix()
	# poker2 = Poker([40,40,40,30,30,30,30,50])
	poker2 = Poker([40,40,40,50])
	poker2.fix()
	print(poker1, poker2, matchEnableDiscard(poker1, poker2))
