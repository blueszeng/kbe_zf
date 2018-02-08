#!/usr/bin/env python
# -*- coding: utf-8 -*-\
import sys,os
if __name__ == '__main__':
	sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..\\common'))

#import ddzUtil
import random
from Poker import Poker, Card,CardEnum
from enum import Enum

''' class NiuNiuTpye:
	#jjn = 100
	boom = 90
	wuXiao = 80
	#huLu = 70
	#tongHua = 60
	wuHua = 50
	#shunZi = 40
	niuNiu = 30
	niu = 20
	no = 10
class NiuNiuRate:
	#jjn = 10
	boom = 6
	wuXiao = 6
	#huLu = 7
	#tongHua = 6
	wuHua = 5
	#shunZi = 5
	niuNiu = 4
	niu_max = 3
	niu_sec = 2
	niu_thr = 1
	niu_no = 1 '''

niuNiuType = {
	'boom'		:	90,
	'wuXiao'	:	80,
	'wuHua'		:	50,
	'niuNiu'	:	30,
	'niu'		:	20,
	'no'		:	10
}

niuniuRate = {
	niuNiuType['boom']		: 6,
	niuNiuType['wuXiao']	: 6,
	niuNiuType['wuHua']		: 5,
	niuNiuType['niuNiu']	: 4,
	niuNiuType['niu'] + 9	: 3,
	niuNiuType['niu'] + 8	: 2,
	niuNiuType['niu'] + 7	: 2,
	niuNiuType['niu'] + 6	: 1,
	niuNiuType['niu'] + 5	: 1,
	niuNiuType['niu'] + 4	: 1,
	niuNiuType['niu'] + 3	: 1,
	niuNiuType['niu'] + 2	: 1,
	niuNiuType['niu'] + 1	: 1,
	niuNiuType['no']		: 1
}

# 整副牌
allPoker = Poker()
for idx, rank in enumerate(CardEnum.nums):
	maxColor = CardEnum.colors[idx]
	if rank == 17 or rank == 18:
		maxColor = 0
	for color in range(0, maxColor):
		allPoker.append(rank*10+color)

def fapai():
	''' 发牌 '''
	# 整副牌
	cards = allPoker.copy()
	random.shuffle(cards)
	count = yield len(cards)
	while len(cards) > 0:
		toCards = cards[-count-1:-1]
		cards = cards[:-count]
		count = yield toCards

def judgePoker(_poker):
	_poker = Poker(_poker).fix()
	#牌型判断结果组合
	cardType = 0
	cardNNvalue = list(_poker.nnRankList())
	count = sum(cardNNvalue)
	# print(count)
	remind = count % 10
	#判断五小
	is_fiveMin = False
	if count < 10:
		is_fiveMin = True
		for v in cardNNvalue:
			if v >= 5:
				is_fiveMin = False
	#判断是否有牛
	have_niu = False
	niu_number = 0
	niu_niu = False
	if is_fiveMin == False:
		for item in _poker.twoCount():
			if item % 10 == remind:
				have_niu = True
				niu_number = remind
				if cardType < niuNiuType['niu'] + remind:
					cardType = niuNiuType['niu'] + remind
		if have_niu == True and niu_number == 0:
			niu_niu = True
			if cardType < niuNiuType['niuNiu']:
				cardType = niuNiuType['niuNiu']
	else:
		if cardType < niuNiuType['wuXiao']:
			cardType = niuNiuType['wuXiao']
	#判断是否是五花
	is_fiveFlower = False
	if niu_niu == True:
		if count == 50:
			is_fiveFlower = True
			if cardType < niuNiuType['wuHua']:
				cardType = niuNiuType['wuHua']
	#判断炸弹牛
	have_boom = False
	maxCard = _poker.haveBoom()
	if maxCard != None:
		have_boom = True
		if cardType < niuNiuType['boom']:
			cardType = niuNiuType['boom']
	#没牛
	if cardType < niuNiuType['no']:
		cardType = niuNiuType['no']
	#获取最大牌值
	if maxCard == None:
		maxCard = _poker.getMaxNNRank()
	''' #判断顺子
	shunZi = False
	tempSZ = _poker.isNNShunZi()
	if tempSZ != None:
		shunZi = True
		maxCard = tempSZ
	#判断同花
	tongHua = _poker.isTongHua()
	#判断葫芦牛
	huLu = False
	tempHL = _poker.isHuLu()
	if tempHL != None:
		huLu = True
		maxCard = tempHL '''
	#见见牛  炸弹  五小  同花  葫芦  同花  五花  顺子  有牛  牛几
	
	''' #if shunZi == True and tongHua == True:
	#	cardType = NiuNiuTpye.jjn
	#elif have_boom == True:
	if have_boom == True:
		cardType = NiuNiuTpye.boom
	elif is_fiveMin == True:
		cardType = NiuNiuTpye.wuXiao
	#elif huLu == True:
	#	cardType = NiuNiuTpye.huLu
	#elif tongHua == True:
	#	cardType = NiuNiuTpye.tongHua
	elif is_fiveFlower == True:
		cardType = NiuNiuTpye.wuHua
	#elif shunZi == True:
	#	cardType = NiuNiuTpye.shunZi
	elif niu_niu == True:
		cardType = NiuNiuTpye.niuNiu
	elif have_niu == True:
		cardType = NiuNiuTpye.niu + remind
	else:
		cardType = NiuNiuTpye.no '''
	cardValue = cardType*1000 + maxCard.nnRank*10 + maxCard.color
	# print(cardValue)
	return cardValue

def comparePoker(val_1,val_2):
	win_lose = False
	rate = 0
	#对比牌型大小
	if val_1 / 1000 > val_2 / 1000:
		win_lose = True
	elif val_1 / 1000 < val_2 / 1000:
		win_lose = False
	else:
		if val_1 / 1000 == NiuNiuTpye.jjn or val_1 / 1000 == NiuNiuTpye.shunZi:
			if (val_1 % 1000) / 10 > (val_2 % 1000) / 10:
				if (val_2 % 1000) / 10 == 1:
					win_lose = False
				else:
					win_lose = True
			elif (val_1 % 1000) / 10 < (val_2 % 1000) / 10:
				if (val_1 % 1000) / 10 == 1:
					win_lose = True
				else:
					win_lose = False
			else:
				if val_1 % 1000 > val_2 % 1000:
					win_lose = True
				else:
					win_lose = False
		else:
			if val_1 > val_2:
				win_lose = True
			else:
				win_lose = False

	win_val = val_1
	if win_lose == False:
		win_val = val_2
	#根据牌型大小确定番数
	rate = niuniuRate[int(win_val / 1000)]
	''' #if win_val / 1000 == NiuNiuTpye.jjn:
	#	rate = NiuNiuRate.jjn
	#elif win_val / 1000 == NiuNiuTpye.boom:
	if win_val / 1000 == NiuNiuTpye.boom:
		rate = NiuNiuRate.boom
	elif win_val / 1000 == NiuNiuTpye.wuXiao:
		rate = NiuNiuRate.wuXiao
	#elif win_val / 1000 == NiuNiuTpye.huLu:
	#	rate = NiuNiuRate.huLu
	#elif win_val / 1000 == NiuNiuTpye.tongHua:
	#	rate = NiuNiuRate.tongHua
	elif win_val / 1000 == NiuNiuTpye.wuHua:
		rate = NiuNiuRate.wuHua
	#elif win_val / 1000 == NiuNiuTpye.shunZi:
	#	rate = NiuNiuRate.shunZi
	elif win_val / 1000 == NiuNiuTpye.niuNiu:
		rate = NiuNiuRate.niuNiu
	elif win_val / 1000 > NiuNiuTpye.niu:
		if (win_val / 1000) % 10 == 9:
			rate = NiuNiuRate.niu_max
		elif (win_val / 1000) % 10 >= 7:
			rate = NiuNiuRate.niu_sec
		else:
			rate = NiuNiuRate.niu_thr
	else:
		rate = NiuNiuRate.niu_no '''
	#返回输赢倍率值
	if win_lose == True:
		return rate
	else:
		rate = -rate
		return rate
	

if __name__ == '__main__':
	cardColor = {'hei':3,'hong':2,'mei':1,'fang':0}
	cardValue = {'A':140,'2':160,'3':30,'4':40,'5':50,'6':60,'7':70,'8':80,'9':90,'10':100,'J':110,'Q':120,'K':130}
	''' f = fapai()
	next(f)
	poker1 = f.send(5)
	poker1 = Poker(poker1).fix()
	poker2 = f.send(5)
	poker2 = Poker(poker2).fix()
	print(poker1)
	print(poker2)
	rate = comparePoker(judgePoker(poker1),judgePoker(poker2))
	print(rate) '''
	list1 = [cardValue['J']+cardColor['hei'],
			cardValue['A']+cardColor['hong'],
			cardValue['A']+cardColor['mei'],
			cardValue['A']+cardColor['fang'],
			cardValue['2']+cardColor['hei']]

	list2 = [cardValue['K']+cardColor['hei'],
			cardValue['K']+cardColor['hong'],
			cardValue['K']+cardColor['mei'],
			cardValue['K']+cardColor['fang'],
			cardValue['3']+cardColor['hei']]

	poker1 = Poker(list1).fix()
	poker2 = Poker(list2).fix()
	print(poker1)
	print(poker2)
	len1 = len(poker1)
	len2 = len(poker2)
	if len1 != 5 or len2 != 5:
		print('error_1')
	else:
		success = True
		for i in range(0,5):
			for j in range(0,5):
				if poker1[i].rank == poker2[j].rank and poker1[i].color == poker2[j].color:
					print('error_2')
					success = False
		if(success == True):
			rate = comparePoker(judgePoker(poker1),judgePoker(poker2))
			print('success,rate:'+str(rate))
			
	''' poker2 = Poker([10,20,30]).fix()
	for item in poker2.twoCount():
	 	print(item) '''
	''' for item in (v for v in poker2.rankList() if v > 10):
		print(item) '''