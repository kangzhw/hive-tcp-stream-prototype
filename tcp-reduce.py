#!/usr/bin/python

'''
	Morgan Phillips @2013
	winter2718@gmail.com

	Don't forget, this is a hacked up prototype. It only performs partial ordering at the moment.:]

	To help in ordering I'm going to use a simple sliding window:
	->Read in 64 packets
	->Sort them
	->Write the first 32
	->Read in 32 more packets
	->Repeat from step 2
'''

import sys
import atexit

globalFlowList = []

def exitDump():
        globalFlowList = sorted(globalFlowList,flowComparator,reverse=True)
	while globalFlowList != None:
		print "\t".join(globalFlowList.pop())

#let's not lose track of our last 32 packets.  :)
atexit.register(exitDump)

def flowComparator(x,y):
        if x[2] == y[3]:
                return 1
	else:
		return 0

def appendFlowToList(line):
	line = line.strip()
        fields = line.split("\t")
        try:
		#Just keeping things explicit for myself
                combo = fields[0].split(":")
                ip1 = combo[0]
                port1 = combo[1]
                ip2 = combo[2]
                port2 = combo[3]

                ts = fields[1]
                tsmicros = fields[2]
                tcp_seq = fields[3]
                tcp_ack = fields[4]
                tcp_flag_syn = fields[5]
                tcp_flag_ack = fields[6]
		
		tmpList = [ts,tsmicros,tcp_seq,tcp_ack,tcp_flag_syn,tcp_flag_ack,ip1,port1,ip2,port2]

		if tcp_flag_syn=="true" and tcp_flag_ack=="false":
			globalFlowList.insert(0,tmpList)
		elif tcp_flag_syn=="true" and tcp_flag_syn=="true":
			globalFlowList.insert(1,tmpList)
		else:
			globalFlowList.append(tmpList)
	
        except:
                pass

for line in sys.stdin:
	appendFlowToList(line)
	if len(globalFlowList) > 64:
		globalFlowList = sorted(globalFlowList,flowComparator,reverse=True)
		while len(globalFlowList) > 32:
			print "\t".join(globalFlowList.pop())
