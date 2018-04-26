#!/usr/bin/env python
from netmiko import ConnectHandler
from datetime import datetime

inventory={
  'device':[
     {
      'access':{
        'device_type': 'cisco_ios',
        'ip': '192.168.100.1',
        'username': 'admin',
        'password': 'admin',
        'port': 22
       },
        'name':'sw1'
      },

    {
      'access':{
        'device_type': 'cisco_ios',
        'ip': '192.168.100.24',
        'username': 'admin',
        'password': 'admin',
        'secret':'admin',
        'port': 22
       },
        'name':'router1'
    },

    {
      'access':{
        'device_type': 'cisco_ios',
        'ip': '192.168.100.2',
        'username': 'admin',
        'password': 'admin',
        'port': 22
       },
        'name':'sw2'
    }

 ]
}

for i in range(len(inventory['device'])):
  try:
    print(inventory['device'][i]['name']+': processing.......')
    net_connect = ConnectHandler(**(inventory['device'][i]['access']))
    net_connect.enable()
    output = net_connect.send_command_expect("show running")
    net_connect.disconnect()
    with open(inventory['device'][i]['name']+datetime.strftime(datetime.now(),
    '_%d-%m-%y_%H:%H:%S')+'.conf','w') as file:
        file.write(output)
  except Exception as e: print '%s: %s' %(inventory['device'][i]['name'],e)
  
  
