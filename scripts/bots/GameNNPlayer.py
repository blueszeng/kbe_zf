# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

class GameNNPlayer(KBEngine.Entity):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		DEBUG_MSG("GameNNPlayer::__init__:%s." % (self.__dict__))

	
