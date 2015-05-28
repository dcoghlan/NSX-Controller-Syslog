# NSX-Controller-Syslog
A script to list, add or delete syslog server details on NSX-v controllers using the REST API.

##Prerequisites
Requires the Requests libraby to be installed. Requests can be downloaded a from the following URL
http://docs.python-requests.org/en/latest/

##Usage
###Help
```
python nsx-controller-syslog.py -h
```
Output:
```
usage: nsx-controller-syslog.py [-h] -nsxmgr nsxmgr [-user [user]]
                                {add,list,del} ...

List/Add/Delete NSX-v Controller syslog server configuration.

positional arguments:
  {add,list,del}
    add           Add syslog servers on all controllers
    list          List all controllers
    del           Delete all syslog servers on all controllers

optional arguments:
  -h, --help      show this help message and exit
  -nsxmgr nsxmgr  NSX Manager hostname, FQDN or IP address
  -user [user]    OPTIONAL - NSX Manager username (default: admin)
```
###list
```
python nsx-controller-syslog.py list -h
```
Output:
```
usage: nsx-controller-syslog.py list [-h]

optional arguments:
  -h, --help  show this help message and exit
```
###add
```
python nsx-controller-syslog.py add -h
```
Output:
```
usage: nsx-controller-syslog.py add [-h] -dest IP/FQDN [-protocol [protocol]]
                                    [-port [port]] [-level [Level]]

optional arguments:
  -h, --help            show this help message and exit
  -dest IP/FQDN         syslog server IP or FQDN
  -protocol [protocol]  OPTIONAL - UDP | TCP (default: UDP)
  -port [port]          OPTIONAL - Port number (default: 514)
  -level [Level]        OPTIONAL - Syslog Level (default: INFO)
```
###del
```
python nsx-controller-syslog.py del -h
```
Output:
```
usage: nsx-controller-syslog.py del [-h]

optional arguments:
  -h, --help  show this help message and exit
```
##Examples
###list
This will display the current syslog settings on all controllers.
```
python nsx-controller-syslog.py -nsxmgr 10.29.4.11 list
NSX Manager password:

#########################################################################################
                                    Current Settings                                     
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING  splunk.sneaku.com           514   UDP      INFO  
controller-2    10.29.4.42    RUNNING  splunk.sneaku.com           514   UDP      INFO  
controller-3    10.29.4.43    RUNNING  splunk.sneaku.com           514   UDP      INFO  
```
###add
If you just specify the destination to send the syslog data to, it will use the default of UDP/514 and set the logging level to INFO.  It will show you the details both before and after the new configuration occurs.
```
python nsx-controller-syslog.py -nsxmgr 10.29.4.11 add -dest splunk.sneaku.com
NSX Manager password:

#########################################################################################
                                      Old Settings                                       
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING                                                   
controller-2    10.29.4.42    RUNNING                                                   
controller-3    10.29.4.43    RUNNING                                                 

SUCCESS: Configured syslog server splunk.sneaku.com on controller-1
SUCCESS: Configured syslog server splunk.sneaku.com on controller-2
SUCCESS: Configured syslog server splunk.sneaku.com on controller-3

#########################################################################################
                                      New Settings                                       
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING  splunk.sneaku.com           514   UDP      INFO  
controller-2    10.29.4.42    RUNNING  splunk.sneaku.com           514   UDP      INFO  
controller-3    10.29.4.43    RUNNING  splunk.sneaku.com           514   UDP      INFO 
```
###add
You can also specify the port, protocol and logging level if required. It will show you the details both before and after the new configuration occurs.
```
python nsx-controller-syslog.py -nsxmgr 10.29.4.11 add -dest splunk.sneaku.com -protocol TCP -port 5514 -level INFO
NSX Manager password:

#########################################################################################
                                      Old Settings                                       
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING                                                   
controller-2    10.29.4.42    RUNNING                                                   
controller-3    10.29.4.43    RUNNING                                                 

SUCCESS: Configured syslog server splunk.sneaku.com on controller-1
SUCCESS: Configured syslog server splunk.sneaku.com on controller-2
SUCCESS: Configured syslog server splunk.sneaku.com on controller-3

#########################################################################################
                                      New Settings                                       
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING  splunk.sneaku.com           5514  TCP      INFO  
controller-2    10.29.4.42    RUNNING  splunk.sneaku.com           5514  TCP      INFO  
controller-3    10.29.4.43    RUNNING  splunk.sneaku.com           5514  TCP      INFO 
```

###del
This will delete all syslog information on all controllers. It will show you the details both before and after the delete occurs.
```
python nsx-controller-syslog.py -nsxmgr 10.29.4.11 del
NSX Manager password:

#########################################################################################
                                      Old Settings                                       
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING  splunk.sneaku.com           514   UDP      INFO  
controller-2    10.29.4.42    RUNNING  splunk.sneaku.com           514   UDP      INFO  
controller-3    10.29.4.43    RUNNING  splunk.sneaku.com           514   UDP      INFO 

SUCCESS: Deleted syslog server configuration on controller-1
SUCCESS: Deleted syslog server configuration on controller-2
SUCCESS: Deleted syslog server configuration on controller-3

#########################################################################################
                                      New Settings                                       
#########################################################################################
Object ID       IP Address    Status   Syslog Server               Port  Protocol Level 
--------------- ------------- -------- --------------------------- ----- -------- ------
controller-1    10.29.4.41    RUNNING                                                   
controller-2    10.29.4.42    RUNNING                                                   
controller-3    10.29.4.43    RUNNING
```
