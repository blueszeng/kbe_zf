# -*- coding: utf-8 -*-
import tornado.httpclient
import json
from KBEDebug import *
from Functor import *



def toUrl(url, **msg):
	''' 拼接url '''
	items = msg.items()
	if len(items) == 0:
		return url
	cot = '?'
	logi('items', items)
	for key, val in items:
		if cot != '?':
			cot += "&"
		cot += key +'='+val
	return url + cot


def httpFetch(url, resolve, reject=None, byJson=False):
	''' http请求 '''
	http_client = tornado.httpclient.AsyncHTTPClient()

	def _onResponse(response):
		try:
			assert not response.error, "Error: %s" % (response.error)
			content = str(response.body, encoding = "utf-8")
			if byJson:
				content = json.loads(content)
			
			INFO_MSG('httpFetch', content)
			resolve(content)
		except Exception as identifier:
			logw(identifier)
			if reject:
				reject()
	http_client.fetch(url, _onResponse)


def post(url, isJson=True, **data):
	content = data
	if isJson:
		content = json.dumps(data)
	return tornado.httpclient.HTTPRequest(url, method='POST', body=content)


def fetch(request, callback, prase=json.loads, encode='utf-8'):
	def _onResponse(response):
		try:
			assert not response.error, "Error: %s" % (response.error)
			content = str(response.body, encoding = encode)
			content = prase(content)
			INFO_MSG(content)
			
			callback(content)
		except Exception as identifier:
			logw(identifier)

	http_client = tornado.httpclient.AsyncHTTPClient()
	http_client.fetch(request, _onResponse)
