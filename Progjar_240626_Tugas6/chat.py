import sys
import os
import json
import uuid
import logging
from queue import  Queue
import threading 
import socket

class RealmCommunicationThread(threading.Thread):
	def __init__(self, chat, target_realm_address, target_realm_port):
		self.chat = chat
		self.target_realm_address = target_realm_address
		self.target_realm_port = target_realm_port
		self.queue = Queue()  # Queue for outgoing messages to the other realm
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		threading.Thread.__init__(self)
	def run(self):
		self.sock.connect((self.target_realm_address, self.target_realm_port))
		while True:
			# Menerima data dari realm lain
			data = self.sock.recv(32)
			if data:
				command = data.decode()
				response = self.chat.proses(command)
				# Mengirim balasan ke realm lain
				self.sock.sendall(json.dumps(response).encode())
			# Check if there are messages to be sent
			while not self.queue.empty():
				msg = self.queue.get()
				self.sock.sendall(json.dumps(msg).encode())
	def put(self, msg):
		self.queue.put(msg)

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}}
		self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
		self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}

		self.realm = None
		target_realm_address = '172.16.16.101'
		target_realm_port = 65001
		self.realm = RealmCommunicationThread(self, target_realm_address, target_realm_port)
		self.realm.start()

		# print("Using __dict__:")
		# print(self.realm.__dict__)

		# print("\nUsing vars():")
		# print(vars(self.realm))

		# print("\nUsing dir():")
		# print(dir(self.realm))

		# print("\nUsing pprint:")
		# from pprint import pprint
		# pprint(vars(self.realm))

	def proses(self,data):
		j=data.split(" ")
		try:
			command=j[0].strip()
			if (command=='auth'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("AUTH: auth {} {}" . format(username,password))
				return self.autentikasi_user(username,password)
			elif (command=='send'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			elif (command=='inbox'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("INBOX: {}" . format(sessionid))
				return self.get_inbox(username)
			elif (command=='sendgroup'):
				sessionid = j[1].strip()
				group_name = j[2].strip()
				message=""
				for m in j[3:]:
					message="{} {}" . format(message,m)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,group_name))
				return self.send_group_message(sessionid,usernamefrom,group_name,message)
			elif (command == 'sendrealm'):
				sessionid = j[1].strip()
				realm_name = j[2].strip()
				usernameto = j[3].strip()
				message = ""
				for w in j[4:]:
					message = "{} {}".format(message, w)
				logging.warning("SENDREALM: session {} send message from {} to {} in realm {}".format(sessionid, self.sessions[sessionid]['username'], usernameto, realm_name))
				return self.send_realm_message(sessionid, usernameto, message)
			elif (command == 'sendgrouprealm'):
				sessionid = j[1].strip()
				realm_name = j[2].strip()
				group_name = j[3].strip()
				message = ""
				for w in j[4:]:
					message = "{} {}".format(message, w)
				logging.warning("SENDGROUPREALM: session {} send message from {} to {} in realm {}".format(sessionid, self.sessions[sessionid]['username'], group_name, realm_name))
				return self.send_group_realm_message(sessionid, group_name, message)
			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except KeyError:
			return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}
	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	def send_message(self,sessionid,username_from,username_dest,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		
		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:	
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}

	def get_inbox(self,username):
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())
			
		return {'status': 'OK', 'messages': msgs}
	
	def send_group_message(self, sessionid, username_from, group_name, message):
		if sessionid not in self.sessions:
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		
		s_fr = self.get_user(username_from)
		if s_fr is False:
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
		
		if group_name == "pemain_bola":
			pemain_bola = ['messi', 'henderson', 'lineker']
		
			for username_dest in pemain_bola:
				if username_dest != username_from:
					s_to = self.get_user(username_dest)
					if s_to is False:
						continue

					notif = {'msg_from': s_fr['nama'], 'msg_on_group': group_name, 'msg': message}
					outqueue_sender = s_fr['outgoing']
					inqueue_receiver = s_to['incoming']

					try:    
						outqueue_sender[username_from].put(notif)
					except KeyError:
						outqueue_sender[username_from]=Queue()
						outqueue_sender[username_from].put(notif)
					try:
						inqueue_receiver[username_from].put(notif)
					except KeyError:
						inqueue_receiver[username_from]=Queue()
						inqueue_receiver[username_from].put(notif)

		return {'status': 'OK', 'message': 'Message Sent'}

	def send_realm_message(self, sessionid, username_to, message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		
		username_from = self.sessions[sessionid]['username']
		message = { 'msg_from': username_from, 'msg_to': username_to, 'msg': message }
		self.realm.put(message)
		self.realm.queue.put(message)
		return {'status': 'OK', 'message': 'Message Sent to Realm'}

	def send_group_realm_message(self, sessionid, group_name, message):
		if sessionid not in self.sessions:
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		
		username_from = self.sessions[sessionid]['username']

		if group_name == "pemain_bola":
			pemain_bola = ['messi', 'henderson', 'lineker']
		
			for username_dest in pemain_bola:
				if username_dest != username_from:
					message = { 'msg_from': username_from, 'msg_on_group': group_name, 'msg': message }
					
					self.realm.put(message)
					self.realm.queue.put(message)

		return {'status': 'OK', 'message': 'Message Sent to Group in Realm'}

if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	tokenid = sesi['tokenid']

	print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
	print(j.proses("sendgroup {} pemain_bola gol berapa?" . format(tokenid)))

	print(j.proses("inbox {}" . format(tokenid)))

	print(j.proses("sendrealm {} {} henderson halo atlet" . format(tokenid, j.realm._name)))
	print(j.proses("sendgrouprealm {} {} pemain_bola halo para atlet" . format(tokenid, j.realm._name)))

	print(j.proses("auth henderson surabaya"))
	tokenid = sesi['tokenid']
	print(j.proses("inbox {}" . format(tokenid)))