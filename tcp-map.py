#!/usr/bin/python

'''
	Morgan Phillips @2013
	winter2718@gmail.com

	Don't forget, this is a hacked up prototype. :]
'''

import sys

def makeIpPortCombo(src,src_port,dst,dst_port):
        combo = "NULL"
	'''direction is set to store flow information lost in normalization'''
	direction = "NULL"
	if src_port > dst_port:
                combo = src+":"+src_port+":"+dst+":"+dst_port
		direction = "dst"
        else:
                combo = dst+":"+dst_port+":"+src+":"+src_port
		direction = "src"
	return [combo,direction]

for line in sys.stdin:
	line = line.strip()
	fields = line.split("\t")
	
	ts = fields[0]
	tsmicros = fields[1]
	tcp_seq = fields[2]
	tcp_ack = fields[3]
	src = fields[4]
	src_port = fields[5]
	dst = fields[6]
	dst_port = fields[7]	
	tcp_flag_syn = fields[8]
	tcp_flag_ack = fields[9]
	protocol = fields[10]

	combo = makeIpPortCombo(src,src_port,dst,dst_port)
	
	print "\t".join([combo[0],ts,tsmicros,tcp_seq,tcp_ack,tcp_flag_syn,tcp_flag_ack,protocol,combo[1]])
