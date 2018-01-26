#!/usr/bin/python3

import sys
import re
import pexpect
import getopt
import os
import getpass
#from itertools import groupby

#pattren for catching necessery strings of pexpect's output
pattern = 'port vlan-stacking vlan (\d*)\s?\w*?\s(\d*)\s?stack-vlan\s+(\d*)\r\n'

PROMPT = '\<[\w\-]*\>'

help_msg = '''Help:
-h  hostname or host's ip address
-u  username for authentication on the host
-p  user's password
-?  help '''


def help():
	print(help_msg)
	os._exit(1)


#make list of vlan's ranges /for print/
def make_ranges(a):
	endl = []
	startl = []
	a.sort()
	for i in range(len(a)):
		if a[i] == max(a):
			endl.append(a[i])
			break
		else:
			if a[i] == min(a):
				startl.append(a[i])
			if not (a[i] == a[i+1] - 1):
				endl.append(a[i])
				startl.append(a[i+1])
	return list(zip(startl, endl))


#calculate free inner-vlans in QinQ stack
def calc_free(vlist):
	return list(set([vlan for vlan in range(2, 4095)])-set(vlist))

#generate list, wich consist of all outer vlans found in the pexpect's output
def get_unified_item(result):
	return list(set([i[2] for i in result]))

#decode all tuples' elements into utf-8
#def convert(tup):
#	return list(map((lambda i: i.decode('utf-8')),tup))


def dict_used_vlans(outers,vlan_list):
	douters = { x:[] for x in outers }
	for outer in outers:
		for i in vlan_list:
			if outer == i[2]:
				if i[1] == '':
					douters[outer].append(int(i[0]))
				else:
					s = int(i[0])
					e = int(i[1]) + 1
					douters[outer] += list(range(s, e))
		tmp_list = list(set(douters[outer]))
		tmp_list.sort()
		douters[outer] = tmp_list
	return douters

def print_ranges(inner_list):
	tmp_list = make_ranges(inner_list)
	str_out = "        "
	for rang in tmp_list:
		if (rang[0] == rang[1]): 
			str_out += "%d, " % (rang[0])
		else:
			str_out += "%d-%d, " % rang
	str_out += "\n"
	return str_out

def print_all(outers, vldict):
	outers.sort()
	msg = "\n"
	for outer in outers:
		msg += "    %s:\n" % outer
		msg += "      Used:\n"
		msg += print_ranges(vldict[outer])
		msg += "      Free:\n"
		msg += print_ranges(calc_free(vldict[outer])) + "\n"
	print(msg)


def main():
	try:
		optlist, args = getopt.getopt(sys.argv[1:],'?h:up')
	except Exception as error:
		print(str(error))
		os._exit(1)
	options = dict(optlist)

	if '-?' in options:
		help()

	if '-h' in options:
		host = options['-h']
	else:
		help()

	conn = pexpect.spawn('telnet ' + host, timeout = 20, maxread = 7000, encoding = 'utf-8')
	
	try:
		conn.expect('Username:', timeout = 2)
		if '-u' in options:
			username = options['-u']
		else:
			username = input('username: ')
		conn.send(username+'\n')
	except pexpect.TIMEOUT:
		pass
	
	try:
		conn.expect('Password:\s?', timeout = 2)
	except pexpect.TIMEOUT as error:
		conn.close()
		print("Connection error. Exceed timeout")
		os._exit(1)

	if '-p' in options:
		password = options['-p']
	else:
		password = getpass.getpass('password: ')
	

	print("Please, wait ...")


	conn.send(password + '\n')
	conn.expect(PROMPT)
	conn.send('screen-length 0 temporary\n')
	conn.expect(PROMPT)
	conn.send('disp cur | i stack-vlan \n')

	vlan_list = []

	try:
		while True:
			line = conn.expect([PROMPT, pattern])
			if line == 0:
				break
			vlan_list.append(conn.match.groups())
	except:
		pass

	conn.close()

	#vlan_list = list(map(convert,vlan_list))

	outers = get_unified_item(vlan_list)
	vlqinq = dict_used_vlans(outers, vlan_list)
	

	print_all(outers, vlqinq)



if __name__ == '__main__':
	main()

