#!/usr/bin/python

'''
	Morgan Phillips @2013
	winter2718@gmail.com
'''

import sys
import atexit
import operator

'''
Tracking each flow by combo key with a sliding window set aside for each.
The flow list should keep a running "rank/id" number for each entry.  This way 
the results can be sorted according to conversation combo and flow_id.

globalFlowDict has entries: seq  => [sequence of stream start(where Ack=0),direction]
			    ack  => [first acknowledgement number(where syn_flag and ack_flag = True),direction]
			    flows=> [flows]

For now, trying to produce flow ids by calculating the relative seq/ack numbers for each flow and adding them up.
'''

globalFlowDict = {}

def exitDump():
        for key in globalFlowDict.keys():
		'''
		If there's no seq/ack offset, make an estimate using the smallest seq/ack available
		'''
		if globalFlowDict[key]["seqOffset"][0] == 0:
			globalFlowDict[key]["flows"] = sorted(globalFlowDict[key]["flows"],key=operator.itemgetter(3))
			globalFlowDict[key]["seqOffset"] = [long(globalFlowDict[key]["flows"][0][3]),globalFlowDict[key]["flows"][0][7]]
		if globalFlowDict[key]["ackOffset"][0] == 0:
			globalFlowDict[key]["flows"] = sorted(globalFlowDict[key]["flows"],key=operator.itemgetter(3))	
			globalFlowDict[key]["ackOffset"] = [long(globalFlowDict[key]["flows"][0][4]),globalFlowDict[key]["flows"][0][7]]
	
		while len(globalFlowDict[key]["flows"]) > 0:
			tmpFlow = globalFlowDict[key]["flows"].pop()
                        tmpFlow.append(str(generateFlowID(tmpFlow,globalFlowDict[key]["seqOffset"],globalFlowDict[key]["ackOffset"])))
			print '\t'.join(tmpFlow)

#let's not lose track of our last 32 packets.  :)
atexit.register(exitDump)

def generateFlowID(flow,seqOffset,ackOffset):
	
	totalA = 0
	totalB = 0

	#Don't waste time with the handshake
	if flow[5] == "true":
		if flow[6] == "false":
			return 0
		elif flow[6] == "true":
			return 1
	else:

		if seqOffset[1] == "src":
			if flow[7] == "src":
				return (long(flow[3])-seqOffset[0])+(long(flow[4])-ackOffset[0])
			else:
				return (long(flow[4])-seqOffset[0])+(long(flow[3])-ackOffset[0])
		else:
			if flow[7] == "dst":
				return (long(flow[3])-seqOffset[0])+(long(flow[4])-ackOffset[0])
                        else:
                                return (long(flow[4])-seqOffset[0])+(long(flow[3])-ackOffset[0])	

def registerFlow(line):
	line = line.strip()
        fields = line.split("\t")
        try:
		#Just keeping things explicit for myself
                combo = fields[0]
                ts = fields[1]
                tsmicros = fields[2]
                tcp_seq = fields[3]
                tcp_ack = fields[4]
                tcp_flag_syn = fields[5]
                tcp_flag_ack = fields[6]
		direction = fields[7]
		
		if combo not in globalFlowDict.keys():
			globalFlowDict[combo] = {"seqOffset":[0,"src"],"ackOffset":[0,"dst"],"flows":[]} 

		tmpList = [combo,str(ts),str(tsmicros),str(tcp_seq),str(tcp_ack),tcp_flag_syn,tcp_flag_ack,direction]

		if tcp_flag_syn=="true":
			if tcp_flag_ack=="false":
				globalFlowDict[combo]["seqOffset"] = [long(tcp_seq),direction]
			elif tcp_flag_ack=="true":
				globalFlowDict[combo]["ackOffset"] = [long(tcp_seq),direction]
		
		globalFlowDict[combo]["flows"].append(tmpList)
        except:
                pass

for line in sys.stdin:
	registerFlow(line)
	for key in globalFlowDict.keys():
		if len(globalFlowDict[key]["flows"]) > 64 and globalFlowDict[key]["seqOffset"][0] > 0 and globalFlowDict[key]["ackOffset"][0] > 0:

			while len(globalFlowDict[key]["flows"]) > 32:
				tmpFlow = globalFlowDict[key]["flows"].pop()
				tmpFlow.append(str(generateFlowID(tmpFlow,globalFlowDict[key]["seqOffset"],globalFlowDict[key]["ackOffset"])))
				print "\t".join(tmpFlow)
