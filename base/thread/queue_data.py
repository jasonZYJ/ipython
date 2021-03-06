from queue import Queue
from threading import Thread, Event
import time


def producer(out_q):
	i = 0
	while True:
		i += 1
		print("product count:",i) 
		data="hello world " + " " + str(i) 
		out_q.put(data,evt)
		time.sleep(2)
		evt.wait()

def consumer(in_q):
	while True:
		data = in_q.get()
		print("consumer is: ",data)
		evt.set()


q = Queue()
evt =Event()
t1 = Thread(target=consumer, args=(q,))
t2 = Thread(target=producer, args=(q,))
t2.start()
t1.start()
