# -*- coding: utf-8 -*-


class CardEnum:
	nums =   [		  3,4,5,6,7,8,9,	10,	11,	12,	13,	14,		16,	17,		18]
	colors = [		  4,4,4,4,4,4,4, 	4, 	4, 	4, 	4, 	4, 		4, 	1, 		1]
	strs =   [0,'A',2,3,4,5,6,7,8,9,	'X','J','Q','K','A',0,	2,	'u',	'V']

KING1 = 170
KING2 = 180


class Card(int):
	''' 单张牌, int 类型拓展 '''
	def __new__(cls, rank, color=-1):
		val = rank
		if color >= 0:
			val = rank*10+color
		return int.__new__(cls, val)

	def __init__(self, rank):
		int.__init__(self)
		self.rank = int(rank/10)
		self.color = rank%10
		self.nnRank = self.rank
		#if self.nnRank >= 11 and self.nnRank <= 13:
		#	self.nnRank = 10
		if self.nnRank == 14:
			self.nnRank = 1
		elif self.nnRank == 16:
			self.nnRank = 2
		

	def __repr__(self):
		return str(CardEnum.strs[self.rank])


class Poker(list):
	# def __new__(cls, *args, **kwargs):
	# 	return list.__new__(cls, *args, **kwargs)

	''' 牌组, Card 类型 list '''
	def __init__(self, *args):
		list.__init__(self, *args)
		self._fixed = False

	def fix(self):
		if self._fixed:
			return self
		self._fixed = True
		self.sort()
		self.ranks = {}
		for i, card in enumerate(self):
			card = Card(card)
			self[i] = card
			self.ranks[card.rank] = self.ranks.get(card.rank, 0) + 1
		return self

	# 按照rank迭代 
	def iterRank(self):
		for rank in CardEnum.nums:
			height = self.ranks.get(rank, 0)
			if height > 0:
				yield (rank, height)

	def __repr__(self):
		if self._fixed == False:
			self.fix()
		s = '.'
		for rank, height in self.iterRank():
			if height > 0:
				s += str(CardEnum.strs[rank])*height+'.'
		return s

	def rankList(self):
		for item in self:
			yield item.rank

	def nnRankList(self):
		for item in self:
			if item.nnRank >= 11 and item.nnRank <= 13:
				yield 10
			else:
				yield item.nnRank

	def twoCount(self):
		count = len(self)
		for idx1 in range(0, count-1):
			value_m = self[idx1].nnRank
			if self[idx1].nnRank >= 11 and self[idx1].nnRank <= 13:
				value_m = 10
			for idx2 in range(idx1+1, count):
				value_n = self[idx2].nnRank
				if self[idx2].nnRank >= 11 and self[idx2].nnRank <= 13:
					value_n = 10
				yield value_m + value_n

	def haveBoom(self):
		count = len(self)
		if count >= 4:
			for idx1 in range(0, count-4):
				equalNumber = 0
				for idx2 in range(idx1+1, count):
					if self[idx1].rank == self[idx2].rank:
						equalNumber = equalNumber + 1
				if equalNumber == 3:
					return self[idx1]
		return None

	def getMaxRank(self):
		maxCard = None
		for item in self:
			if maxCard == None or item.rank > maxCard.rank:
				maxCard = item
		return maxCard

	def getMaxNNRank(self):
		maxCard = None
		for item in self:
			if maxCard == None or item.nnRank > maxCard.nnRank:
				maxCard = item
			elif item.nnRank == maxCard.nnRank and item.nnRank == 10:
				if item.rank > maxCard.rank:
					maxCard = item
		return maxCard

	def isNNShunZi(self):
		tempListPk = self
		count = len(tempListPk)
		for i in range(0, count-1):
			for j in range(count-1,i+1):
				if tempListPk[i].nnRank > tempListPk[j].nnRank:  
					tempPk = tempListPk[i]
					tempListPk[i] = tempListPk[j]
					tempListPk[j] = tempPk
		for idx in range(0, count-1):
			tempVal1 = tempListPk[count-1-idx].nnRank
			tempVal2 = tempListPk[count-2-idx].nnRank
			if tempVal1 != tempVal2 + 1:
				if idx == count-2 and tempVal1 == 10 and tempVal2 == 1:
					return tempListPk[0]
				else:
					return None
		return tempListPk[count-1]

	def isTongHua(self):
		count = len(self)
		for idx in range(0, count-1):
			if self[idx].color != self[idx+1].color:
				return False
		return True

	def isHuLu(self):
		count = len(self)
		haveThree = None
		haveTwo = None
		for idx1 in range(0, count-1):
			sumN = 0
			for idx2 in range(idx1+1, count):
				if self[idx1].nnRank == self[idx2].nnRank:
					sumN = sumN + 1
			if sumN == 3:
				haveThree = self[idx1]
		if haveThree != None:
			for idx1 in range(0, count-1):
				sumN = 0
				if self[idx1].nnRank != haveThree.nnRank:
					for idx2 in range(idx1+1, count):
						if self[idx1].nnRank == self[idx2].nnRank:
							sumN = sumN + 1
				if sumN >= 2:
					haveTwo = self[idx1]
		if haveThree != None and haveTwo != None:
			return haveThree
		else:
			return None
		''' if self._fixed != True:
			self.sort()
		count = len(self)
		for idx in range(0, count-1):
			tempVal1 = self[idx].rank
			tempVal2 = self[idx+1].rank
			if tempVal1 == 14:
				tempVal1 = 1
			elif tempVal1 == 16:
				tempVal1 = 2
			if tempVal2 == 14:
				if idx == 3:
					tempVal2 = 14
			elif tempVal2 == 16:
				tempVal2 = 2
			if tempVal1 + 1 != tempVal2:
				return None
		return self[0] '''

	# 是否包含目标牌
	def isContain(self, poker):
		for rank, height in poker.iterRank():
			if self.ranks.get(rank, 0) < height:
				return False
		return True

