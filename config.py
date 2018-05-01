#!/usr/bin/env python
from netmiko import ConnectHandler
import yaml
import re
from datetime import datetime

inv="""
device:
- access: {device_type: cisco_ios, ip: 192.168.100.1, password: admin, port: 22, username: admin, secret: admin}
  savemem: 'true'
#  disable: 'true'  
  name: sw1
  rmints:
    - {int: eth3/0-1}
    - {int: eth0}
- access: {device_type: cisco_ios, ip: 192.168.11.3, password: admin, port: 22, username: admin, secret: admin}
  savemem: 'true'
#  disable: 'true'
  ints:
  - {int: range e0/1, fip: 10.10.10.254 255.255.255.0}
  name: router3
  ospf:
    id: 3.3.3.3
    route:
    - {network: 192.168.0.0 0.0.255.255, area: '0'}
    - {network: 10.10.10.0 0.0.0.255, area: '0'}
  dhcp:
    - {name: dhcp02, fip: 10.10.10.0 255.255.255.0, gw: 10.10.10.254}
  exclude:
    - {range: 10.10.10.1 10.10.10.100}
- access: {device_type: cisco_ios, ip: 192.168.100.1, password: admin, port: 22, username: admin}
  savemem: 'true'
#  disable: 'true'
  ints:
  - {int: range e0/0-3, portfast: 'true', vlan: '1'}
  - {int: range e1/0-3, portfast: 'true', vlan: '10'}
  - {int: range e2/0-3, portfast: 'true', vlan: '50'}
  name: sw1
  trunk: [e3/2, e3/3]
  vlans:
  - {desc: vlan 10, fip: 192.168.1.1 255.255.255.0, vlan: '10'}
  - {desc: vlan 50, fip: 192.168.50.1 255.255.255.0, vlan: '50'}
  vtp: transparent
- access: {device_type: cisco_ios, ip: 192.168.100.2, password: admin, port: 22, username: admin}
  savemem: 'true'
#  disable: 'true'
  ints:
  - {int: range e0/0-3, portfast: 'true', vlan: '1'}
  - {int: range e1/0-3, portfast: 'true', vlan: '10'}
  - {int: range e2/0-3, portfast: 'true', vlan: '50'}
  name: sw2
  trunk: [e3/2, e3/3]
  vlans:
  - {desc: vlan 10, fip: 192.168.1.2 255.255.255.0, vlan: '10'}
  - {desc: vlan 50, fip: 192.168.50.2 255.255.255.0, vlan: '50'}
  vtp: transparent
"""

inventory=yaml.load(inv)
net_connect=None
#==========================================
def open(access):
  global net_connect
  net_connect = ConnectHandler(**access)
  net_connect.enable()
#==========================================
def close():
  global net_connect
  if net_connect:
    net_connect.disconnect()
#==========================================
def run(cmd):
  global net_connect
  output=""
  if cmd:
    print cmd
    output = net_connect.send_config_set(cmd)
#    print output
  return output
#==========================================
def vtp(action):
  global net_connect
  cmd=[]
  print('processing vtp.......')
  cmd.append('vtp mode '+action)
  run(cmd)
#==========================================
def vlans(action):
  global net_connect
  cmd=[]
  print(' processing vlans.......')
  for ii in range(len(action)):
    if(action[ii].has_key('vlan')):
      cmd.append('interface vlan '+action[ii]['vlan'])
    if(action[ii].has_key('desc')):
      cmd.append('description '+action[ii]['desc'])
    if(action[ii].has_key('fip')):
      cmd.append('ip address '+action[ii]['fip'])
    cmd.append('no shutdown')
  run(cmd)
#==========================================
def trunk(action):
  global net_connect
  cmd=[]
  print('processing trunk.......')
  for ii in range(len(action)):
    cmd.append('interface '+action[ii])
    cmd.append('switchport trunk encapsulation dot1q')
    cmd.append('switchport mode trunk')
    cmd.append('no shutdown')
  run(cmd)
#==========================================
def dhcp(action):
  global net_connect
  cmd=[]
  print('processing dhcp.......')
  for ii in range(len(action)):
    if(action[ii].has_key('name')):
      cmd.append('ip dhcp pool '+action[ii]['name'])
    if(action[ii].has_key('fip')):
      cmd.append('network '+action[ii]['fip'])
    if(action[ii].has_key('gw')):
      cmd.append('default-router '+action[ii]['gw'])
  run(cmd)
#==========================================
def commands(action):
  global net_connect
  cmd=[]
  print('processing commands.......')
  for ii in range(len(action)):
    if(action[ii].has_key('command')):
      cmd.append(action[ii]['command'])
  run(cmd)
#==========================================
def exclude(action):
  global net_connect
  cmd=[]
  print('processing dhcp exclude.......')
  for ii in range(len(action)):
    if(action[ii].has_key('range')):
      cmd.append('ip dhcp excluded-address '+action[ii]['range'])
  run(cmd)
#==========================================
def savefile(name):
  global net_connect
  print('saving config to file .......')
  output = run("show running")
  with open(name+datetime.strftime(datetime.now(),
  '_%d-%m-%y_%H:%H:%S')+'.conf','w') as file:
      file.write(output)
#==========================================
def savemem():
  global net_connect
  print('saving config to mem.......')
  output=net_connect.send_command_expect('write mem')
  print output
#==========================================
def ints(action):
  global net_connect
  cmd=[]
  print('processing interfaces.......')
  for ii in range(len(action)):
    if(action[ii].has_key('int')):
      cmd.append('interface '+action[ii]['int'])
    if(action[ii].has_key('fip')):
      cmd.append('ip address '+action[ii]['fip'])
    if(action[ii].has_key('vlan')):
      cmd.append('switchport access vlan '+action[ii]['vlan'])
    if(action[ii].has_key('portfast')):
      cmd.append('switchport mode access')
      cmd.append('spanning-tree portfast')
      cmd.append('spanning-tree bpduguard enable')
    cmd.append('no shutdown')
  run(cmd)
#==========================================
def ospf(action):
  global net_connect
  print('processing opsf.......')
  cmd=[]
  cmd.append('router ospf 1')
  if(action.has_key('id')):
    cmd.append('router-id '+action['id'])
  if(action.has_key('route')):
    for ii in range(len(action['route'])):
      cmd.append('network '+action['route'][ii]['network']+ ' area ' +
             action['route'][ii]['area'])
  run(cmd)
#==========================================
def rmints(action):
  global net_connect

  print('processing interface config removal.......')
  output = net_connect.send_command_expect("show running")
  configlist=output.split('\n')

  for ii in range(len(action)):
    if(action[ii].has_key('int')):
      input=action[ii]['int']

      il=re.findall(r'(\w+?)(\d+.*)', input)
      iil=il[0][1].split('/')
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
      run(cmd)
#==========================================
def main():
  for i in range(len(inventory['device'])):
    try:
      if(inventory['device'][i].has_key('disable')):
        print inventory['device'][i]['name']+" :Bypassing configuration...... "
        continue
      print inventory['device'][i]['name']+" :Processing configuration....... "
      open(inventory['device'][i]['access'])
      if(inventory['device'][i].has_key('savefile')):
        savefile(inventory['device'][i]['name'])
      if(inventory['device'][i].has_key('vtp')):
        vtp(inventory['device'][i]['vtp'])
      if(inventory['device'][i].has_key('vlans')):
        vlans(inventory['device'][i]['vlans'])
      if(inventory['device'][i].has_key('trunk')):
        trunk(inventory['device'][i]['trunk'])
      if(inventory['device'][i].has_key('ints')):
        ints(inventory['device'][i]['ints'])
      if(inventory['device'][i].has_key('ospf')):
        ospf(inventory['device'][i]['ospf'])
      if(inventory['device'][i].has_key('dhcp')):
        dhcp(inventory['device'][i]['dhcp'])
      if(inventory['device'][i].has_key('exclude')):
        exclude(inventory['device'][i]['exclude'])
      if(inventory['device'][i].has_key('rmints')):
        rmints(inventory['device'][i]['rmints'])
      if(inventory['device'][i].has_key('commands')):
        commands(inventory['device'][i]['commands'])
      if(inventory['device'][i].has_key('savemem')):
        savemem()
    except Exception as e: print '%s: %s' %(inventory['device'][i]['name'],e)

    close()

if __name__ == '__main__':
    main()
