# -*- coding: utf-8 -*-
import KBEngine
import Functor
import socket
from KBEDebug import *

class Poller:
	"""
	演示：
	可以向kbengine注册一个socket，由引擎层的网络模块处理异步通知收发。
	用法: 
	from Poller import Poller
	poller = Poller()
	
	开启(可在onBaseappReady执行)
	poller.start("localhost", 12345)
	
	停止
	poller.stop()
	"""
	def __init__(self):
		self._socket = None
		self._clients = {}
		
	def start(self, addr, port):
		"""
		virtual method.
		"""
		self._socket = socket.socket()
		self._socket.bind((addr, port))
		self._socket.listen(10)
		
		KBEngine.registerReadFileDescriptor(self._socket.fileno(), self.onRecv)
		# KBEngine.registerWriteFileDescriptor(self._socket.fileno(), self.onWrite)

	def send(self):
		self._socket = socket.socket()
		self._socket.connect(('www.baidu.com',80))
		self._socket.send('''GET https://www.baidu.com/ HTTP/1.1
		Host: www.baidu.com
		Connection: keep-alive
		Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
		Upgrade-Insecure-Requests: 1
		User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36
		Accept-Language: zh-CN,zh;q=0.8
		''')
		KBEngine.registerReadFileDescriptor(self._socket.fileno(), self.onRecv)

	def stop(self):
		if self._socket:
			KBEngine.deregisterReadFileDescriptor(self._socket.fileno())
			self._socket.close()
			self._socket = None
		
	def onWrite(self, fileno):
		pass
		
	def onRecv(self, fileno):
		if self._socket.fileno() == fileno:
			sock, addr = self._socket.accept()
			self._clients[sock.fileno()] = (sock, addr)
			KBEngine.registerReadFileDescriptor(sock.fileno(), self.onRecv)
			DEBUG_MSG("Poller::onRecv: new channel[%s/%i]" % (addr, sock.fileno()))
		else:
			sock, addr = self._clients.get(fileno, None)
			if sock is None:
				return
			
			data = sock.recv(2048)
			DEBUG_MSG("Poller::onRecv: %s/%i get data, size=%i" % (addr, sock.fileno(), len(data)))
			self.processData(sock, data)
			KBEngine.deregisterReadFileDescriptor(sock.fileno())
			sock.close()
			del self._clients[fileno]
			
	def processData(self, sock, datas):
		"""
		处理接收数据
		"""
		logi('processData', datas)
