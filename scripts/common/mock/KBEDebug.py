# -*- coding: utf-8 -*-
import sys

def printMsg(args, isPrintPath):
	print(*args)

def TRACE_MSG(*args): 
	printMsg(args, False)
	
def DEBUG_MSG(*args): 
	printMsg(args, True)
	
def INFO_MSG(*args): 
	printMsg(args, False)
	
def WARNING_MSG(*args): 
	printMsg(args, True)

def ERROR_MSG(*args): 
	printMsg(args, True)
