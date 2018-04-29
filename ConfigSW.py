#!/usr/bin/env python
from netmiko import ConnectHandler

inventory={
  'device':[
     {
      'access':{
        'device_type': 'cisco_ios',
        'ip': '192.168.100.3',
        'username': 'admin',
        'password': 'admin',
        'port': 22
       },
        'name':'sw1',
        'vlans':[{'vlan':'10','desc':'vlan 10','fip':'192.168.1.3 255.255.255.0'},
                        {'vlan':'50','desc':'vlan 50','fip':'192.168.50.3 255.255.255.0'}
                  ],
        'ints':[{'int':'range e0/0-3','vlan':'10','portfast':'true'},
                {'int':'range e1/0-3','vlan':'10','portfast':'true'}
            ],
        'trunk':['e3/2','e3/3'],
        'vtp':'transparent'
      }
 ]
}

for i in range(len(inventory['device'])):
  net_connect = ConnectHandler(**(inventory['device'][i]['access']))
  net_connect.enable()

  if(inventory['device'][i].has_key('vtp')):
    print(inventory['device'][i]['name']+': processing vtp.......')
    cmd=[]
    cmd.append('vtp mode '+inventory['device'][i]['vtp'])
    print cmd
    output=net_connect.send_config_set(cmd)
    print output

  if(inventory['device'][i].has_key('vlans')):
    print(inventory['device'][i]['name']+': processing vlans.......')
    for ii in range(len(inventory['device'][i]['vlans'])):
        cmd=[]
        if(inventory['device'][i]['vlans'][ii].has_key('vlan')):
                cmd.append('interface vlan '+inventory['device'][i]['vlans'][ii]['vlan'])
        if(inventory['device'][i]['vlans'][ii].has_key('desc')):
                cmd.append('description '+inventory['device'][i]['vlans'][ii]['desc'])
        if(inventory['device'][i]['vlans'][ii].has_key('fip')):
                cmd.append('ip address '+inventory['device'][i]['vlans'][ii]['fip'])
        cmd.append('no shutdown')
        print cmd
        output = net_connect.send_config_set(cmd)
        print output

  if(inventory['device'][i].has_key('trunk')):
    print(inventory['device'][i]['name']+': processing trunk.......')
    for ii in range(len(inventory['device'][i]['trunk'])):
        cmd=[]
        cmd.append('interface '+inventory['device'][i]['trunk'][ii])
        cmd.append('switchport trunk encapsulation dot1q')
        cmd.append('switchport mode trunk')
        cmd.append('no shutdown')
        print cmd
        output=net_connect.send_config_set(cmd)
        print output

  if(inventory['device'][i].has_key('ints')):
    print(inventory['device'][i]['name']+': processing interfaces.......')
    for ii in range(len(inventory['device'][i]['ints'])):
        cmd=[]
        if(inventory['device'][i]['ints'][ii].has_key('int')):
                cmd.append('interface '+inventory['device'][i]['ints'][ii]['int'])
        if(inventory['device'][i]['ints'][ii].has_key('vlan')):
                cmd.append('switchport access vlan '+inventory['device'][i]['ints'][ii]['vlan'])
        if(inventory['device'][i]['ints'][ii].has_key('portfast')):
                cmd.append('switchport mode access')
                cmd.append('spanning-tree portfast')
                cmd.append('spanning-tree bpduguard enable')
        cmd.append('no shutdown')
        print cmd
        output = net_connect.send_config_set(cmd)
        print output

print(inventory['device'][i]['name']+': saving configuration.......')
output=net_connect.send_command_expect('write mem')
print output
net_connect.disconnect()

