# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

class GameNN(KBEngine.Entity):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		DEBUG_MSG("GameNN::__init__:%s." % (self.__dict__))


