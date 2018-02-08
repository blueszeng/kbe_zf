# -*- coding: utf-8 -*-
import sys
import KBEngine

oldPrint = print

def print(*args):
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_NORMAL)
	oldPrint(*args)

def printMsg(args, isPrintPath):
	for m in args:oldPrint (m)

def TRACE_MSG(*args): 
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_NORMAL)
	printMsg(args, False)


def DEBUG_MSG(*args): 
	if KBEngine.publish() == 0:
		KBEngine.scriptLogType(KBEngine.LOG_TYPE_DBG)
		printMsg(args, True)
	
def INFO_MSG(*args): 
	if KBEngine.publish() <= 1:
		KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)
		printMsg(args, False)
	
def WARNING_MSG(*args): 
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_WAR)
	printMsg(args, True)

def ERROR_MSG(*args): 
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
	printMsg(args, True)


def logv(*args):
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_NORMAL)
	oldPrint(*args)

def logd(*args):
	if KBEngine.publish() == 0:
		KBEngine.scriptLogType(KBEngine.LOG_TYPE_DBG)
		oldPrint(*args)

def logi(*args):
	if KBEngine.publish() <= 1:
		KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)
		oldPrint(*args)
	
def logw(*args):
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_WAR)
	oldPrint(*args)

def loge(*args):
	KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
	oldPrint(*args)
	