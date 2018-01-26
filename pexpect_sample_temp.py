conn = pexpect.spawn('telnet ' + host)

conn.expect('Username:')
conn.send(username+'\n')
conn.expect('Password: ')
conn.send(password + '\n')
conn.expect(PROMPT)
conn.send('screen-length 0 temporary\n')
conn.expect(PROMPT)
conn.send('disp cur | i stack-vlan \n')

result = []
while True:
	line = conn.expect([PROMPT, pattern])
	if line == 0:
		break
	out = conn.match.groups()
	result.append(out)





result = [(b'600', b'', b'3305'), (b'602', b'603', b'3505'), (b'604', b'', b'3305'), (b'606', b'607', b'3505'), (b'608', b'', b'3305'), (b'610', b'611', b'3505'), (b'612', b'', b'3305'), (b'614', b'615', b'3505'), (b'616', b'', b'3305'), (b'618', b'619', b'3505'), (b'620', b'', b'3305'), (b'622', b'623', b'3505'), (b'628', b'', b'3305'), (b'629', b'630', b'3505'), (b'631', b'', b'3705'), (b'632', b'', b'3305'), (b'633', b'635', b'3505'), (b'636', b'', b'3305'), (b'637', b'639', b'3505'), (b'640', b'', b'3305'), (b'641', b'643', b'3505'), (b'644', b'', b'3305'), (b'645', b'647', b'3505'), (b'664', b'', b'3305'), (b'665', b'667', b'3505'), (b'668', b'', b'3305'), (b'669', b'671', b'3505'), (b'672', b'', b'3305'), (b'673', b'675', b'3505'), (b'676', b'', b'3305'), (b'677', b'679', b'3505'), (b'648', b'', b'3305'), (b'649', b'651', b'3505'), (b'652', b'', b'3305'), (b'653', b'655', b'3505'), (b'656', b'', b'3305'), (b'657', b'659', b'3505'), (b'680', b'', b'3305'), (b'681', b'682', b'3505'), (b'683', b'', b'3705'), (b'100', b'123', b'3305'), (b'624', b'', b'3305'), (b'124', b'147', b'3505'), (b'625', b'627', b'3505'), (b'660', b'', b'3305'), (b'661', b'663', b'3505'), (b'664', b'671', b'3305')]




list(map((lambda i: i.decode('utf-8')),a))


def make_dict(result,outers):



douters={x:[] for x in outers}

for outer in outers:
    for i in result:
        if outer==i[2]:
            if i[1]=='':
                douters[outer].append(int(i[0]))
            else:
                s = int(i[0])
                e = int(i[1])+1
                douters[outer]+=list(range(s,e))





def conv(tup):
    return tuple(map((lambda i: i.decode('utf-8')),tup))
    




for key in douters.keys():
    for i, el in enumerate(douters[key]):
        if type(el) is tuple:
            sr = int(douters[key][i][0])
            er = int(douters[key][i][1])+1
            douters[key] = douters[key] + list(range(sr,er))
            del douters[key][i]
            


def dict_vlans(outers,vlan_list):
	douters={x:[] for x in outers}
	for outer in outers:
		for i in vlan_list:
			if outer==i[2]:
					douters[outer].append([x in i])



def make_ranges(vlist):
    endl=[]
    startl=[]
    vlist.sort()
    for i in range(len(vlist)):
        if vlist[i]==max(vlist):
            endl.append(vlist[i])
            break
        else:
            if vlist[i]==min(vlist):
                startl.append(vlist[i])
            if not (vlist[i]==vlist[i+1]-1):
                endl.append(vlist[i])
                startl.append(vlist[i+1])
    print(startl, endl)
    return list(zip(startl, endl))







   """
def print_per_outer(D):
	for key in douters.keys():
		for i, el in enumerate(douters[key]):
			if type(el) is tuple:
				sr = int(douters[key][i][0])
				er = int(douters[key][i][1]) + 1
				print(list(range(sr, er)))

"""


def print_all(vldict):
	for outer in vldict:
		print("  Used inner-vlans of:\n  %s:" % outer)
		print(printRange(vldict[outer]))





def printRange(inner_list):
	new_list = make_ranges(inner_list)
	out = "    "
	for rang in new_list:
		if (rang[0] == rang[1]): 
			out += "%d, " % (rang[0])
		else:
			out += "%d-%d, " % rang
	out += "\n"
	return out






PROMPT = '\<[\w\-]*\>'
pattern2 = 'vlan\s+(\d*)\r\n+\s*\w*\s+([\w]*\-QinQ[\#\.]+([\w\/\-]*))'
username = 'denis'
password = '17292205'
host = 'cat3-dbk.net.loc'

c = pexpect.spawn('telnet ' + host, encoding = 'utf-8')

c.expect('Username:')
c.send(username+'\n')
c.expect('Password:\s?')
c.send(password + '\n')
c.expect(PROMPT)
c.send('screen-length 0 temporary\n')
c.expect(PROMPT)
c.send('disp cur conf vlan\n')

groups = []

try:
	while True:
		line = c.expect([PROMPT, pattern2])
		if line == 0:
			break
		groups.append(c.match.groups())
except:
	pass

c.close()



for i in groups:
	print({i[2]: {i[0]:i[1]}})


[{i[2]: {i[0]:i[1]}} for i in groups]




GG = list(set([i[2] for i in groups]))






from itertools import groupby

x = ['a', 'a', 'a', 'f', 'h', 'k', 'k']

new_x = [el for el, _ in groupby(x)]

print(new_x)    # ['a', 'f', 'h', 'k']




D={x:[] for x in GG}
for gr in GG:
	for tup in groups:
		if gr in tup:
			D[gr].append(tup[0])



D={x:[] for x in GG}
for gr in GG:
	for tup in groups:
		if gr in tup:
			D[gr].append({tup[0]:tup[1]})


for j, key in enumerate(D.keys()):
    for i, el in enumerate(D[key]):
        if '2201' in D[key][i]:
            print("Yes!")
            print(D[key][i])







PROMPT = '\<[\w\-]*\>'
pattern3 = "port hybrid untagged vlan\s?\s?([0-9 ]*)\r?\n?|vlan-mapping vlan\s([0-9]*)"
username = 'denis'
password = '17292205'
host = 'cat3-dbk'

c = pexpect.spawn('telnet ' + host, timeout = 20, maxread = 7000, encoding = 'utf-8')

c.expect('Username:')
c.send(username+'\n')
c.expect('Password:\s?')
c.send(password + '\n')
c.expect(PROMPT)
c.send('screen-length 0 temporary\n')
c.expect(PROMPT)
c.send('disp cur int\n')

NEWD = {x:[] for x in GG}
interfaces = []
p_outers = ""
try:
	while True:
		line = c.expect([PROMPT, pattern3])
		if line == 0:
			break
		#print(c.match.groups())
		if not (c.match.groups()[0] == None):
			p_outers = c.match.groups()[0]
		else: 
			for gr in D:
				for item in D[gr]:
					if item in p_outers: 
						NEWD[gr].append(c.match.groups()[1])
						break
except:
	pass

c.close()



PROMPT = '\<[\w\-]*\>'
pattern3 = "(i)nterface\s|port hybrid untagged vlan\s?\s?([0-9 ]*)\r?\n?|vlan-mapping vlan\s([0-9]*)"
username = 'denis'
password = '17292205'
host = 'cat3-dbk'

c = pexpect.spawn('telnet ' + host, timeout = 20, maxread = 7000, encoding = 'utf-8')

c.expect('Username:')
c.send(username+'\n')
c.expect('Password:\s?')
c.send(password + '\n')
c.expect(PROMPT)
c.send('screen-length 0 temporary\n')
c.expect(PROMPT)
c.send('disp cur int\n')

NEWD = {x:[] for x in GG}
interfaces = []
p_outers = ""
next_flag = 0
try:
	while True:
		line = c.expect([PROMPT, pattern3])
		if line == 0:
			break
		#print(c.match.groups())
		if (c.match.groups()[0] == "i"):
			next_flag = 1
			continue
		else:
			if not (c.match.groups()[1] == None):
				p_outers = c.match.groups()[1]
			elif next_flag:  
				for gr in D:
					for item in D[gr]:
						if item in p_outers: 
							NEWD[gr].append(c.match.groups()[2])
							break
except:
	pass

c.close()





PROMPT = '\<[\w\-]*\>'
pattern = "([X]?GigabitEthernet[\d\/]*)"
username = 'denis'
password = '17292205'
host = 'cat3-dbk'

c = pexpect.spawn('telnet ' + host, timeout = 60, maxread = 7000, encoding = 'ascii' )

c.expect('Username:')
c.send(username+'\n')
c.expect('Password:\s?')
c.send(password + '\n')
c.expect(PROMPT)
c.send('screen-length 0 temporary\n')
c.expect(PROMPT)
c.send('disp cur int\n')

pt_outers = "port hybrid untagged vlan\s?\s?([0-9 ]*)\r?\n?"
pt_map = "vlan-mapping vlan\s([0-9]*)"

interfaces = []
NEWD = {x:[] for x in GG}

try:
	while True:
		line = c.expect([PROMPT, pattern])
		if line == 0:
			break
		#print(c.match.groups())
		interfaces.append(c.match.groups()[0])
except:
	pass

for i in interfaces:
	c.send('disp cur int ' + i + '\n')
	rec_b = c.expect([PROMPT, pt_outers])
	if rec_b == 0:
		continue
	p_outers = c.match.groups()[0]
	while True:
		rec_b = c.expect([PROMPT, pt_map])
		if rec_b == 0:
			break
		for gr in D:
			for item in D[gr]:
				if item in p_outers:
					NEWD[gr].append(c.match.groups()[0])
					break


c.close()











PROMPT = '\<[\w\-]*\>'
username = 'denis'
password = '17292205'
host = 'cat3-dbk'

c = pexpect.spawn('telnet ' + host, timeout = 60, maxread = 7000, encoding = 'utf-8' )

c.expect('Username:')
c.send(username+'\n')
c.expect('Password:\s?')
c.send(password + '\n')
c.expect(PROMPT)
c.send('screen-length 0 temporary\n')
c.expect(PROMPT)
c.send('disp cur int\n')
c.expect(PROMPT)

res = c.before

c.close()

res = "\n".join(res.splitlines())
m = re.compile(r"\#\s?interface\s+(X?GigabitEthernet[\s\n\/\-\:0-9\w\.]*)", re.MULTILINE)
e = m.findall(res)

for i in e:
	print(i)


