# -*- coding: utf-8 -*-
import sys
sys.path.append("common")

# import interface.wxCharge

def req_resp(func):
	reqName = func.__name__
	print(reqName)

	def theFunc(ins):
		args = func(ins)
		assert len(args) > 0
		
	return theFunc

class Foo:
	def __init__(self):
		pass

	@d_request
	def func1(self):
		print('func1', self)



print(Foo)
fo = Foo()
print(fo.func1())
