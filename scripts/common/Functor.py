# -*- coding: utf-8 -*-

"""
用法:
a = 1
b = 2
def abc(a, b):
   print a, b
   
func = Functor(abc, a)
func(b)
"""
import time



class Functor:
	def __init__(self, func, *args, **kwargs):
		self._func = func
		self._Args = args
		self._Kwargs = kwargs

	def __call__(self, *args, **kwargs):
		args = self._Args + args
		kwargs = kwargs.copy()
		kwargs.update(self._Kwargs)
		return self._func(*args, **kwargs)


def bind(func, *args, **kwargs):
	return Functor(func, *args, **kwargs)


def onceCallback(callbackerObj, callback, *args):
	''' 监听一次 Callbacks 回调, 调用后移除事件监听
		callbackerObj: CallbackProperty 类型
		callback: 回调函数
		'''
	callbackID = None
	def _func(*a):
		callback(*tuple(args+a))
		callbackerObj.remove_callback(callbackID)
	print(callbackerObj)
	callbackID = callbackerObj.add_callback(_func, takes_target_args=True)


def it_count(it):
	''' 迭代器计数 '''
	c = 0
	for v in it:
		c += 1
	return c

def it_first(it):
	''' 取迭代器第一个元素 '''
	for v in it:
		return v


# 装饰器:调试函数输出
def debugFunc(func):
	def f(self, *args, **kwargs):
		print('>>>Debug',func.__name__, args, kwargs or '')
		ret = func(self, *args, **kwargs)
		print('<<<Debug',func.__name__, 'return:', ret)
		return ret
	return f


# 块管理器:输出执行块所用时间
class UsedTime:
	def __init__(self):
		self._fromTime = None

	def __enter__(self):
		self._fromTime = time.time()

	def __exit__(self, etype, value, traceback):
		print('used time:', time.time()-self._fromTime)
