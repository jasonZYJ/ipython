
#!/usr/bin/env python
#-*- coding:utf-8 -*-
 
import socket
import os
import threading
 
def handle(fd,conn,epoll):
        base_path = '/home/cdsvlab/log-dir'
        print('connected...')
        pre_data = conn.recv(1024)
        print(pre_data)
 
        if len(pre_data) == 0:
		        print("zero data")
		        epoll.modify(fd,select.EPOLLHUP)
        
        return False
 
        #获取请求方法、文件名、文件大小
        file_name,file_size = pre_data.split('|')
        print(file_name)
        print(file_size)
	#print "file_size is %d" % int(file_size) 
            # 防止粘包，给客户端发送一个信号。
        conn.sendall('nothing')            
        
        recv_size = 0
            #上传文件路径拼接
        file_dir = os.path.join(base_path,file_name)
        f = file(file_dir,'wb')
        Flag = True
        while Flag:
            #未上传完毕，
            if int(file_size)>recv_size:
                print("package ....recv_size %d" % recv_size)
                data = conn.recv(1024)
                recv_size+=len(data)
                #写入文件
                if len(data)>0:
                    f.write(data)
                #上传完毕，则退出循环
            else:
                print("file write done, recv_size = %d" % recv_size)
                recv_size = 0
                Flag =False
                
        print('upload successed.')
        f.close()
        epoll.modify(fd,select.EPOLLHUP)
        return True


class file_server:
	def __init__(self):
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_address = ("127.0.0.1", 9998)
		self.epoll = select.epoll()
		self.fd_to_socket = {}
		self.fd_to_thread = {}
	def listen(self):
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversocket.bind(self.server_address)
		self.serversocket.listen(10)
		print("服务器启动成功，监听IP：" , self.server_address)

	def server_epoll(self):
		flag_global = 0
		#服务端设置非阻塞
		self.serversocket.setblocking(False)
		#超时时间
		timeout = -1
		self.epoll.register(self.serversocket.fileno(), select.EPOLLIN)
		self.fd_to_socket[self.serversocket.fileno()]=self.serversocket
		server_on = True
		while server_on:
			print("等待活动连接......")
			events = self.epoll.poll()
			if not events:
				print("epoll超时无活动连接，重新轮询......")
				continue
			print("有" , len(events), "个新事件，开始处理......")

			for fd, event in events:
				print("new event %d of fd %d" % (event,fd))
				event_socket = self.fd_to_socket[fd]

				if event_socket == self.serversocket:
					connection, address = self.serversocket.accept()
					print("新连接：" , address)
					'''Attention: remove unblocking mode set on the accepted socket.
					thread could block to wait for data'''
					#connection.setblocking(False)
					self.epoll.register(connection.fileno(), select.EPOLLIN)
					self.fd_to_socket[connection.fileno()] = connection
					self.fd_to_thread[connection.fileno()] = 0
				elif event & select.EPOLLHUP:
					print('client close')
					self.epoll.unregister(fd)
					self.fd_to_socket[fd].close()
					del self.fd_to_socket[fd]
					self.fd_to_thread[fd] = 0
				elif event & select.EPOLLIN:
					#start to write file.
					print("fd is %d,conn.fileno() is %d" % (fd,connection.fileno()))
					if self.fd_to_thread[fd] == 0:
						working_thread=threading.Thread(target=handle,args=(fd,self.fd_to_socket[fd],self.epoll))
						self.fd_to_thread[fd]=working_thread
						working_thread.start()
						self.fd_to_thread[fd] = 1
				elif event & select.EPOLLOUT:
					print("not support out")

	def epoll_end(self):
		self.epoll.unregister(self.serversocket.fileno())
		self.epoll.close()
		self.serversocket.close()

if __name__=='__main__':
	auto_file_server=file_server()
	auto_file_server.listen()
	auto_file_server.server_epoll()

