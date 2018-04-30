#!/usr/bin/env python
from netmiko import ConnectHandler
import yaml
import re


inv="""
device:
- access: {device_type: cisco_ios, ip: 192.168.100.1, password: admin, port: 22, username: admin, secret: admin}
  ints:
  - {int: range e0/1, fip: 10.10.10.254 255.255.255.0}
  name: sw1
  rmints:
    - {int: eth3/0-1}
    - {int: eth0}
"""

inventory=yaml.load(inv)


for i in range(len(inventory['device'])):
  net_connect = ConnectHandler(**(inventory['device'][i]['access']))
  net_connect.enable()

  if(inventory['device'][i].has_key('rmints')):
    print(inventory['device'][i]['name']+': processing interface config removal.......')
    output = net_connect.send_command_expect("show running")
    configlist=output.split('\n')

    for ii in range(len(inventory['device'][i]['rmints'])):
      if(inventory['device'][i]['rmints'][ii].has_key('int')):
        input=inventory['device'][i]['rmints'][ii]['int']

        il=re.findall(r'(\w+?)(\d+.*)', input)
        if len(il) > 0:
          iil=il[0][1].split('/')
        else:
          print "input error"
          exit(0)
        print iil
        if len(iil) > 0:
          search='(\\binterface\\b) ('+ il[0][0]+'[a-z]+)(['+ iil[0]+'])'
        for i3 in range(1,len(iil)):
          search=search+'/['+ iil[i3]+']'
        search=search+'.*'
        print search

        cmd=[]
        state=0
        for i4 in range(len(configlist)):
          str=configlist[i4]
          if state==0:
            result=re.findall(search,configlist[i4],re.IGNORECASE)
            if result:
              cmd.append(configlist[i4])
              state=1
          elif configlist[i4] != "!":
            result=re.findall(r'(^\s*(no|shutdown)).*',configlist[i4],re.IGNORECASE)
            if not result:
              cmd.append('no'+configlist[i4])
          else:
            state=0

        print cmd
        output = net_connect.send_config_set(cmd)
        print output

  print(inventory['device'][i]['name']+': saving configuration.......')
  output=net_connect.send_command_expect('write mem')
  print output
  net_connect.disconnect()
