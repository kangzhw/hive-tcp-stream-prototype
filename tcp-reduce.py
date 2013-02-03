#!/usr/bin/python

'''
	Morgan Phillips @2013
	winter2718@gmail.com

	Don't forget, this is a hacked up prototype. It only performs partial ordering at the moment.:]

	To help in ordering I'm going to use a simple sliding window:
	->Read in 64 packets
	->Place them into bins
	->Sort/label the bins
	->Write the first 32 packets from each bin
	->Read in 32 more packets
	->Rinse and repeat

	The code's getting a little messy.  When the prototype starts to come together I'll strip away excessive comments
	and neaten up the code.
'''

import sys
import atexit

'''
Tracking each flow by combo key with a sliding window set aside for each.
The flow list should keep a running "rank/id" number for each entry.  This way 
the results can be sorted according to conversation combo and flow_id.

globalFlowDict has entries: seq=> <sequence of stream start(where Ack=0)>
			   ack=> <first acknowledgement number(where syn_flag and ack_flag = True)>
			   flows=>< list of flow lists >

For now, trying to produce flow ids by calculating the relative seq/ack numbers for each flow and adding them up.
'''

globalFlowDict = {}

def exitDump():
        for key in globalFlowDict.keys():
		'''
		If there's no starting seq/ack, make an estimate using the smallest seq available
		'''
		if globalFlowDict[key]["seqOffset"] < 1:
			globalFlowDict[key]["flows"] = sorted(globalFlowDict[key]["flows"],key=3)
			globalFlowDict[key]["seqOffset"] = long(globalFlowDict[key]["flows"][0][3])
		if globalFlowDict[key]["ackOffset"] < 1:
			globalFlowDict[key]["flows"] = sorted(globalFlowDict[key]["flows"],key=4)
			globalFlowDict[key]["ackOffset"] = long(globalFlowDict[key]["flows"][0][4])			

		while len(globalFlowDict[key]["flows"]) > 1:
			tmpFlow = globalFlowDict[key]["flows"].pop()
			tmpFlow.append(str(generateFlowID(tmpFlow,globalFlowDict[key]["seqOffset"],globalFlowDict[key]["ackOffset"])))
			print '\t'.join(tmpFlow)

#let's not lose track of our last 32 packets.  :)
atexit.register(exitDump)

def testForRelative(possibleRelativeA,possibleRelativeB):
        '''
	Since I'm not yet taking the direction of travel into account
        for the current iteration I'm going to use a test 
        to try to suss out what my relative seq/ack should be.  
	This should be changed in future iterations.
	'''
	if possibleRelativeA < 0:
        	return possibleRelativeB
        elif possibleRelativeB < 0:
                return possibleRelativeA
        elif possibleRelativeA > possibleRelativeB:
                return possibleRelativeB
        else:
        	return possibleRelativeA

def generateFlowID(flow,seqOffset,ackOffset):
	'''
	Let's see how well generating a flow_id from adding up relative seq/ack numbers works.
	Still an incomplete solution; but more robust than a the simple comparator from before....
	'''
	totalA = 0
	totalB = 0

        seqA = (long(flow[3]))-seqOffset
        seqB = (long(flow[4]))-seqOffset

        ackA = (long(flow[4]))-ackOffset
        ackB = (long(flow[3]))-ackOffset

	#Don't waste time with the handshake
	if flow[5] == "true":
		if flow[6] == "false":
			return 0
		elif flow[6] == "true":
			return 1
	else:
		totalA = testForRelative(seqA,seqB)
		totalB = testForRelative(ackA,ackB)

		if totalA+totalB > 1:
			return totalA+totalB
		else:
			return totalA+totalB+1

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
		
		if combo not in globalFlowDict.keys():
			globalFlowDict[combo] = {"seqOffset":0,"ackOffset":0,"flows":[]} 

		tmpList = [combo,str(ts),str(tsmicros),str(tcp_seq),str(tcp_ack),tcp_flag_syn,tcp_flag_ack]

		if tcp_flag_syn=="true":
			if tcp_flag_ack=="false":
				globalFlowDict[combo]["seqOffset"] = long(tcp_seq)
			elif tcp_flag_ack=="true":
				globalFlowDict[combo]["ackOffset"] = long(tcp_ack)
		
		globalFlowDict[combo]["flows"].append(tmpList)
        except:
                pass

for line in sys.stdin:
	registerFlow(line)
	for key in globalFlowDict.keys():
		if len(globalFlowDict[key]["flows"]) > 64 and globalFlowDict[key]["seqOffset"] > 0 and globalFlowDict[key]["ackOffset"] > 0:
			while len(globalFlowDict[key]["flows"]) > 32:
				tmpFlow = globalFlowDict[key]["flows"].pop()
				tmpFlow.append(str(generateFlowID(tmpFlow,globalFlowDict[key]["seqOffset"],globalFlowDict[key]["ackOffset"])))
				print "\t".join(tmpFlow)
