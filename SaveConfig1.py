#!/usr/bin/env python
from netmiko import ConnectHandler
from datetime import datetime
import yaml
import re

inv="""
device:
- access: {device_type: paloalto_panos, ip: 192.168.168.1, password: xxxxxxxx, port: 22, username: xxxxxxxx}
  savemem: 'true'
  disable: 'true'
  name: pa3020_25e
- access: {device_type: aruba_os, ip: 192.168.168.153, password: xxxxxxxx, port: 22, username: xxxxxxxx}
  savemem: 'true'
  disable: 'true'
  name: aruba_25e
- access: {device_type: checkpoint_gaia, ip: 192.168.35.1, password: xxxxxxxx, port: 22, username: xxxxxxxx}
  savemem: 'true'
  disable: 'true'
  name: checkpoint_55KC
- access: {device_type:  hp_procurve, ip: 192.168.168.253, password: xxxxxxxx, port: 22, username: xxxxxxxx}
  savemem: 'true'
  disable: 'true'
  enable512: 'true'
  name: hp_procurve_25e_253
- access: {device_type:  cisco_ios_telnet, ip: 192.168.168.251, password: xxxxxxxx, port: 23, username: xxxxxxxx}
  savemem: 'true'
  disable: 'true'
  enablejin: 'true'
  name: hp_procurve_25e_251
"""

inventory=yaml.load(inv)


for i in range(len(inventory['device'])):
  try:
    print(inventory['device'][i]['name']+': processing.......')
    net_connect = ConnectHandler(**(inventory['device'][i]['access']))
    if(inventory['device'][i].has_key('enable')):
      net_connect.enable()

    result=re.findall(r'cisco_ios', inventory['device'][i]['access']['device_type'])
    if result:
      output = net_connect.send_command_expect("show running")

    result=re.findall(r'hp_procurve', inventory['device'][i]['access']['device_type'])
    if result:
      if(inventory['device'][i].has_key('enable512')):
        net_connect.send_command_timing("_cmdline-mode on\nY\n512900\nscreen-length disable\n")
      if(inventory['device'][i].has_key('enablejin')):
        net_connect.send_command_timing("_cmdline-mode on\nY\nJinhua1920unauthorized\nscreen-length disable\n")
      output = net_connect.send_command_expect("display current")

    result=re.findall(r'cisco_ios_telnet', inventory['device'][i]['access']['device_type'])
    if result:
      show=0
      if(inventory['device'][i].has_key('enable512')):
        net_connect.send_command_timing("_cmdline-mode on\nY\n512900\nscreen-length disable\n")
        show=1
      if(inventory['device'][i].has_key('enablejin')):
        net_connect.send_command_timing("_cmdline-mode on\nY\nJinhua1920unauthorized\nscreen-length disable\n")
        show=1
      if show==0:
        output = net_connect.send_command_expect("show running")
      elif show==1:
        output = net_connect.send_command_expect("display current") 

    result=re.findall(r'paloalto_panos', inventory['device'][i]['access']['device_type'])
    if result:
      output = net_connect.send_command_expect("show config running")

    result=re.findall(r'aruba_os', inventory['device'][i]['access']['device_type'])
    if result:
      output = net_connect.send_command_expect("show configuration")

    result=re.findall(r'checkpoint_gaia', inventory['device'][i]['access']['device_type'])
    if result:
      output = net_connect.send_command_expect("show configuration")

    net_connect.disconnect()
    with open(inventory['device'][i]['name']+datetime.strftime(datetime.now(),
      '_%d-%m-%y')+'.conf','w') as file:
#      '_%d-%m-%y_%H:%H:%S')+'.conf','w') as file:
      file.write(output)
  except Exception as e: print '%s: %s' %(inventory['device'][i]['name'],e)
