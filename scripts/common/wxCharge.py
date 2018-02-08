
# -*- coding: utf-8 -*-

# import requests
from Functor import *
from KBEDebug import *
import tornado

import time
import random
import hashlib
import collections
try:
	import xmltodict as xmltodict
except Exception:
	import common.xmltodict as xmltodict


appid = 'wx96f11e4f93743a3a'
mch_id = '1495129262'


def converToGold(tradeNum):
	return tradeNum*1.1

def unifiedorder(trade_no, num, handle):
	''' 统一下单 '''
	args = {
		'appid': appid,
		'mch_id': mch_id,
		'nonce_str': str(random.random()),
		'body': 'jiufa-goldCharge',
		'notify_url': 'null',
		'out_trade_no': trade_no,
		'trade_type': 'APP',
		'total_fee': num,
	}
	args['sign'] = createSign(args)
	content = xmltodict.unparse({
		'xml': args
	})
	
	http_client = tornado.httpclient.AsyncHTTPClient()
	requrl = "https://api.mch.weixin.qq.com/pay/unifiedorder"
	request = tornado.httpclient.HTTPRequest(requrl, method='POST', body=content)

	def _callback(handle, response):
		''' 处理回应 '''
		info = parseResponse(response)
		isSuccess = info['return_code'] == 'SUCCESS'
		if not isSuccess:
			handle(isSuccess, info)
		else:
			logi('info', info)
			args = {
				'appid': appid,
				'noncestr': info['nonce_str'],
				'package': 'Sign=WXPay',
				'partnerid': mch_id,
				'prepayid': info['prepay_id'],
				'timestamp': str(int(time.time())),
			}	
			args['sign'] = createSign(args)
			logi('args', args)
			handle(isSuccess, args)

	http_client.fetch(request, Functor(_callback, handle))


def queryResult(trade_no, handle):
	''' 查询结果 '''
	args = {
		'appid': appid,
		'mch_id': mch_id,
		'nonce_str': str(random.random()),
		'out_trade_no': trade_no,
	}
	args['sign'] = createSign(args)
	content = xmltodict.unparse({
		'xml': args
	})
	http_client = tornado.httpclient.AsyncHTTPClient()
	requrl = "https://api.mch.weixin.qq.com/pay/orderquery"
	request = tornado.httpclient.HTTPRequest(requrl, method='POST', body=content)

	def _callback(handle, response):
		''' 处理回应 '''
		info = parseResponse(response)
		isSuccess = info['return_code'] == 'SUCCESS'
		logi('queryResult response', info)
		if not isSuccess:
			handle(isSuccess, '')
		else:
			logi('info', info)
			handle(isSuccess, info['trade_state'])

	http_client.fetch(request, Functor(_callback, handle))



def parseResponse(response):
	''' 解析回应 '''
	try:
		assert not response.error, "Error: %s" % (response.error)
		content = str(response.body, encoding = "utf-8")
		content = xmltodict.parse(content)
		return dict(content['xml'])
	except Exception as identifier:
		logw(identifier)


def createSign(args):
	''' 签名算法 '''
	keys = list(args.keys())
	keys.sort()
	tostr = ''
	for k in keys:
		tostr += '' if tostr == '' else '&'
		tostr += k + '=' + str(args[k])
	tostr += '&key=123456789Leguohudongjiufa1234567'
	logi('tostr', tostr)
	md5 = hashlib.md5()
	md5.update(tostr.encode("utf8"))
	return md5.hexdigest().upper()

	
# print(requests.get("http://1uv8700489.iask.in:24768/"))
# unifiedorder()
