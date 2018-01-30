#!/usr/bin/python3

import sys
import re
import pexpect
import getopt
import os
import getpass
from itertools import groupby 

PROMPT = '\<([\w\-]*)\>'

VLAN_RANGE = [vlan for vlan in range(2, 4095)]

PRINT_MSG = ''

username = ''
password = ''
host = ''

help_msg = '''Help:
-h  hostname or host's ip address
-u  username for authentication on the host
-p  user's password
-?  help '''

def exit_with_error(error):
    print('ERROR!\n'+ error)
    os._exit(1)

def request_conf(pexpect_obj, cmd, error_msg = ''):
    pexpect_obj.send(cmd)
    try:
        pexpect_obj.expect(PROMPT, timeout = 20)
    except pexpect.TIMEOUT:
        pexpect_obj.close()
        error = '#\n' + error_msg + pexpect.TIMEOUT + '\n#'
        exit_with_error(error)
    return pexpect_obj.before

def make_list(text, regex):
    text = '\n'.join(text.splitlines())
    re_obj = re.compile(regex, re.MULTILINE)
    return re_obj.findall(text)

def print_list(list):
    for item in list:
        print(item)

def vl_range_from_tup(tup):
    start, end  = tup[0], tup[1]
    if end == '':
        end = start
    start = int(start)
    end = int(end) + 1
    return list(range(start, end))

def integer(vlist):
    return [int(item) for item in vlist]

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

def print_ranges(inner_list):
    str_out = ''
    tmp_list = make_ranges(inner_list)
    for rang in tmp_list:
        if (rang[0] == rang[1]): 
            str_out += "%d, " % (rang[0])
        else:
            str_out += "%d-%d, " % rang
    return str_out

def calc_free(vlist):
    return list(set(VLAN_RANGE)-set(vlist))

def auth(pexpect_obj, options):
    try:
        pexpect_obj.expect('Username:', timeout = 2)
        if '-u' in options:
            username = options['-u']
        else:
            username = input('username: ')
        pexpect_obj.send(username+'\n')
    except pexpect.TIMEOUT:
        pass
    except pexpect.EOF:
        pexpect_obj.close()
        exit_with_error(pexpect_obj.before)
    
    try:
        pexpect_obj.expect('Password:\s?', timeout = 2)
    except pexpect.TIMEOUT as error:
        pexpect_obj.close()
        exit_with_error('Connection error. Exceed timeout')

    if '-p' in options:
        password = options['-p']
    else:
        password = getpass.getpass('password: ')

    pexpect_obj.send(password + '\n')
    try:
        pexpect_obj.expect(PROMPT, timeout = 2)
    except pexpect.TIMEOUT:
        pexpect_obj.close()
        exit_with_error(pexpect_obj.before)

    pexpect_obj.send('screen-length 0 temporary\n')
    

def main():
    global PROMPT

    try:
        optlist, args = getopt.getopt(sys.argv[1:],'?h:up')
    except Exception as error:
        print(str(error))
        os._exit(1)

    options = dict(optlist)

    if '-?' in options:
        exit_with_error(help_msg)

    if '-h' in options:
        host = options['-h']
    else:
        exit_with_error(help_msg)

    telnet = pexpect.spawn(
        'telnet ' + host, 
        timeout = 90, 
        maxread = 7000, 
        encoding = 'utf-8'
        )


    auth(telnet, options)
    telnet.expect(PROMPT)
    hostname = telnet.match.groups()[0]
    PROMPT = r'\<' + hostname + '\>'

    intf_conf = request_conf(
        telnet, 
        cmd = 'disp cur int\n',
        error_msg = 'Unable to get interface configuration data:\n'
        )
    vl_outers_conf = request_conf(
        telnet,
        cmd = 'disp cur conf vlan\n',
        error_msg = 'Unable to get vlan configuration data:\n'
        )

    telnet.close()

    intf_list = make_list(
        text = intf_conf,
        regex = r'(?<=\#\n)([\s\n\/\-\:\d\w\.\(\)\,\>\<]*?\#?\s?[\s\n\/\-\:\d\w\.\(\)\,\>\<]*)\#+\n+'
        )
    vl_outers_list = make_list(
        text = vl_outers_conf,
        regex = r'vlan\s+(\d*)\s*\w*\s+([\w]*\-QinQ[\#\.]+([\w\/\-]*))'
        )
    vl_outers_d = { } 

    for intf in intf_list:
        vl_stack_list = make_list(
            text = intf,
            regex = r'port vlan-stacking vlan (\d*)\s?\w*?\s(\d*?)\s?stack-vlan\s+(\d*)\n'
            )
        #print(vl_stack_list)
        if not (len(vl_stack_list) == 0 ):
            vl_map_list = make_list(
                text = intf,
                regex = r'vlan-mapping vlan\s+(\d*)'
                )
            for tup in vl_stack_list:
                global PRINT_MSG
                if tup[0] == '2' and tup[1] == '4094':
                    int_reg = re.search(r'X?GigabitEthernet\d+/+\d+/+\d*', intf)
                    print("\n  WARNING! Excepted interface " + int_reg[0])
                    continue
                if not tup[2] in vl_outers_d.keys():
                    vl_outers_d.update({tup[2]:[]}) 
                vl_outers_d[tup[2]] += vl_range_from_tup(tup) + integer(vl_map_list)
                tmp_l = [el for el, _ in groupby(vl_outers_d[tup[2]])]
                tmp_l.sort()
                vl_outers_d[tup[2]] = tmp_l

    #vl_groups - list of all QinQ outer-vlans group finded on host 
    #one group consist of PPPoE, LV, GV outer-vlans
    #
    #vl_groups_d is the dictionary which includes below data:
    # - finded groups
    # -- outer-vlans group list
    # ---- every group includes:
    # ----- outer-vlan description
    # ----- all inner-vlans used by the outer-vlan, just inludes map-vlans
    # -- used inner-vlans per group (key: 'used')

    vl_groups = list(set([item[2] for item in vl_outers_list if item[0] in vl_outers_d.keys()]))
    vl_groups.sort()

    vl_groups_d = { key: {
    'outers':[{tup[0]:{'desc': tup[1],
    'inners':[vlan for vlan in vl_outers_d[tup[0]]]}}
    for tup in vl_outers_list if key in tup and tup[0] in vl_outers_d.keys()]} 
    for key in vl_groups }
    
    for gr_key in vl_groups_d.keys():
        vl_inners = list()
        for i, vdict in enumerate(vl_groups_d[gr_key]['outers']):
            for vl_key in vdict.keys():
                vl_inners += vl_groups_d[gr_key]['outers'][i][vl_key]['inners']
                vl_inners = list(set(vl_inners))
        str_used = print_ranges(vl_inners)
        str_free = print_ranges(calc_free(vl_inners))
        vl_groups_d[gr_key].update({'used': str_used})
        vl_groups_d[gr_key].update({'free': str_free})

    PRINT_MSG += '\n' + ' '*4 + 'HOST: ' + hostname
    PRINT_MSG += '\n' + ' '*4 + 'OUTER-VLAN groups:\n'

    for gr in vl_groups:
        PRINT_MSG += '\n' + ' '*6 + ('%s:\n' % gr)
        for item in vl_outers_list:
            if gr in item[2]:
                PRINT_MSG += ' '*8 + 'vlan id: ' + item[0] + ', description: ' + item[1] + '\n' 
        PRINT_MSG += '\n' 
        PRINT_MSG += ' '*8 + 'used:\n' + ' '*8 + '%s\n' % vl_groups_d[gr]['used'] + '\n' 
        PRINT_MSG += ' '*8 + 'free:\n' + ' '*8 + '%s\n' % vl_groups_d[gr]['free'] + '\n'

    print(PRINT_MSG)



if __name__ == '__main__':
    main()