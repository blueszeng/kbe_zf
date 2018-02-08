import KBEngine as kbe
from KBEDebug import *
import acts
import importlib

boter = lambda: kbe.bots.values()[0]

def user(bot=None):
	bot = bot or boter()
	for e in bot.entities.values():
		if e.className == 'PlayerUser':
			return e

def reset():
	importlib.reload(acts)

def rel(module):
	importlib.reload(module)


def step():
	for bot in kbe.bots.values():
		u = user(bot)
		if u:
			nor = acts.bubbling.blackboard(u)
			logd('step', u.id, nor.tick())
