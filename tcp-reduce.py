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

'''
Try tracking each flow by combo key with a sliding window for each
The flow list should keep a running "rank" number for each entry.  This way 
the results can be sorted according to conversation number and flow rank.

conversation_id:combo1 rank:0
conversation_id:combo2 rank:0
conversation_id:combo1 rank:1
etc....
'''

globalFlowDict = {}

def exitDump():
        for key in globalFlowDict.keys():
		globalFlowDict[key] = sorted(globalFlowDict[key],flowComparator,reverse=True)
		while len(globalFlowDict[key]) > 1:
			print '\t'.join(globalFlowDict[key].pop())

#let's not lose track of our last 32 packets.  :)
atexit.register(exitDump)

def rankAndLabel(flowList):
	pass
	'''
	This should be used to assign a flow_id to each flow.
	Moves through every flow list using the combo as a key.
	'''

def flowComparator(x,y):
        if x[2] == y[3]:
                return 1
	else:
		return 0

def registerFlow(line):
	line = line.strip()
        fields = line.split("\t")
        try:
		#Just keeping things explicit for myself
                combo = fields[0]
                ts = str(fields[1])
                tsmicros = str(fields[2])
                tcp_seq = str(fields[3])
                tcp_ack = str(fields[4])
                tcp_flag_syn = fields[5]
                tcp_flag_ack = fields[6]
		flow_id = "0"
		
		if combo not in globalFlowDict.keys():
			globalFlowDict[combo] = [] 

		tmpList = [combo,ts,tsmicros,tcp_seq,tcp_ack,tcp_flag_syn,tcp_flag_ack,flow_id]

		if tcp_flag_syn=="true" and tcp_flag_ack=="false":
			globalFlowDict[combo].insert(0,tmpList)
		elif tcp_flag_syn=="true" and tcp_flag_syn=="true":
			globalFlowDict[combo].insert(1,tmpList)
		else:
			globalFlowDict[combo].append(tmpList)
        except:
                pass

for line in sys.stdin:
	registerFlow(line)
	for key in globalFlowDict.keys():
		if len(globalFlowDict[key]) > 64:
			globalFlowDict[key] = sorted(globalFlowDict[key],flowComparator,reverse=True)
			while len(globalFlowDict[key]) > 32:
				print "\t".join(globalFlowDict[key].pop())
