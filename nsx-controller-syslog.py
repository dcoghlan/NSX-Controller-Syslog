# Author:   Dale Coghlan (www.sneaku.com)
# Date:     28 May 2015
# Version:  1.0.1

# ------------------------------------------------------------------------------------------------------------------
# Set some variables. No need to change anything else after this section

# Sets a variable to save the HTTP/XML reponses and debug logs.
_logFilePrefix = 'controller-'

# Uncomment the following line to hardcode the password. This will remove the password prompt.
#_password = 'default'
#
# ------------------------------------------------------------------------------------------------------------------

import requests                         # Needed to interact with the NSX REST API
import argparse                         # Needed for command line arguements
import getpass                          # Needed to prompt for password if one isn't hard coded
import xml.etree.ElementTree as ET      # Needed to parse XML
import datetime                         # Needed to generate datestamp

try:
    # Only needed to disable anoying warnings self signed certificate warnings from NSX Manager.
    import urllib3
    requests.packages.urllib3.disable_warnings()
except ImportError:
    # If you don't have urllib3 we can just hide the warnings
    import logging
    logging.captureWarnings(True)

# Main parser for global arguments
parser = argparse.ArgumentParser(description='List/Add/Delete NSX-v Controller syslog server configuration.')
parser.add_argument('-nsxmgr', help='NSX Manager hostname, FQDN or IP address', metavar='nsxmgr', dest='_nsxmgr', type=str, required=True)
parser.add_argument('-user', help='OPTIONAL - NSX Manager username (default: %(default)s)', metavar='user', dest='_user', nargs='?', const='admin')
parser.set_defaults(_user='admin')

# Parser arguments for 'add' sub-parser defined below
addParser = argparse.ArgumentParser(add_help=False)
addParser.add_argument('--add', help=argparse.SUPPRESS, dest='_addServers', action='store_true')
addParser.add_argument('-dest', help='syslog server IP or FQDN', metavar='IP/FQDN', dest='_syslogDest', required=True)
addParser.add_argument('-protocol', help='OPTIONAL - UDP | TCP (default: %(default)s)', choices=['UDP', 'TCP'], metavar='protocol', dest='_syslogProtocol', nargs='?', const='UDP')
addParser.add_argument('-port', help='OPTIONAL - Port number (default: %(default)s)', metavar='port', dest='_syslogPort', nargs='?', const='514')
addParser.add_argument('-level', help='OPTIONAL - Syslog Level (default: %(default)s)', metavar='Level', dest='_syslogLevel', nargs='?', const='INFO')
addParser.set_defaults(_syslogProtocol='UDP')
addParser.set_defaults(_syslogPort='514')
addParser.set_defaults(_syslogLevel='INFO')

# Parser arguments for 'list' sub-parser defined below
listParser = argparse.ArgumentParser(add_help=False)
listParser.add_argument('--list', help=argparse.SUPPRESS, dest='_listControllers', action='store_true')

# Parser arguments for 'del' sub-parser defined below
delParser = argparse.ArgumentParser(add_help=False)
delParser.add_argument('--del', help=argparse.SUPPRESS, dest='_delServers', action='store_true')

# Sub-Parsers defined
sp = parser.add_subparsers()
sp_add = sp.add_parser('add', help='Add syslog servers on all controllers', parents=[addParser])
sp_list = sp.add_parser('list', help='List all controllers', parents=[listParser])
sp_del = sp.add_parser('del', help='Delete all syslog servers on all controllers', parents=[delParser])

# Load the parser into a variable
args = parser.parse_args()

# Check to see if the password is hard coded
try:
    _password
except NameError:
    _password = getpass.getpass(prompt='NSX Manager password:')

# Reads command line flags and saves them to variables
_user = args._user
_nsxmgr = args._nsxmgr

try:
    _addServers = args._addServers
    _syslogDest = args._syslogDest
    _syslogProtocol = args._syslogProtocol
    _syslogPort = args._syslogPort
    _syslogLevel = args._syslogLevel
except AttributeError:
    _addServers = None
    _syslogDest = None
    _syslogProtocol = None
    _syslogPort = None
    _syslogLevel = None

try:
    _listControllers = args._listControllers
except AttributeError:
    _listControllers = None

try:
    _delServers = args._delServers
except AttributeError:
    _delServers = None


# Initialise the logging file
_logFileName = _logFilePrefix + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + '.txt'
_logfile = open('%s' % _logFileName, 'w')
_logfile.close()
_logfile = open(_logFileName, 'a+')

# Set the application content-type header value
_nsx_api_headers = {'Content-Type': 'application/xml'}

# Set output formatting
_outputHeaderRow = '{0:15} {1:13} {2:8} {3:27} {4:5} {5:8} {6:6}'
_outputDataRow = '{0:15} {1:13.29} {2:8} {3:27} {4:5} {5:8} {6:6}'
_outputSectionRow = '{0:89}'
_outputSectionTitle = '{0:^89}'

def f_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')

def f_log(data):
    _logfile.write('\n' + f_timestamp() + ': ' + data)

def f_cache_all_controllers():
    _cache_all_controllers_url = 'https://%s/api/2.0/vdn/controller' % (_nsxmgr)
    _cache_all_controllers_reponse = requests.get((_cache_all_controllers_url), headers=_nsx_api_headers, auth=(_user, _password), verify=False)
    _cache_all_controllers_data = _cache_all_controllers_reponse.content
    _cache_all_controllers_root = ET.fromstring(_cache_all_controllers_data)

    if int(_cache_all_controllers_reponse.status_code) != 200:
        print('ERROR: Cannot retrieve list of conrollers')
        f_log('ERROR: Cannot retrieve list of conrollers')
        f_log('ERROR: STATUS CODE | ' + str(_cache_all_controllers_reponse.status_code))
        f_log(_cache_all_controllers_reponse.text)
        return
    else:
        f_log('SUCCESS: Retrieved cache list of controllers')
        return _cache_all_controllers_root

def f_query_controller_syslog(id):
    _query_controller_syslog_url = 'https://%s/api/2.0/vdn/controller/%s/syslog' % (_nsxmgr,id)
    _query_controller_syslog_reponse = requests.get((_query_controller_syslog_url), headers=_nsx_api_headers, auth=(_user, _password), verify=False)
    _query_controller_syslog_data = _query_controller_syslog_reponse.content
    _query_controller_syslog_root = ET.fromstring(_query_controller_syslog_data)

    if int(_query_controller_syslog_reponse.status_code) == 500:
        if _query_controller_syslog_root:
            errorcode = _query_controller_syslog_root.find('errorCode').text
            if int(errorcode) == 100:
                return 'Not set'
            else:
                return
    elif int(_query_controller_syslog_reponse.status_code) != 200:
        print('ERROR: Cannot retrieve syslog exporter details on controller %s' %(id))
        f_log('ERROR: Cannot retrieve syslog exporter details on controller %s' %(id))
        f_log('ERROR: STATUS CODE | ' + str(_query_controller_syslog_reponse.status_code))
        f_log(_query_controller_syslog_reponse.text)
        return
    else:
        return _query_controller_syslog_root

def f_list_controllers(version):
    print('')
    print(_outputSectionRow.format("#"*89))
    print(_outputSectionTitle.format(version))
    print(_outputSectionRow.format("#"*89))
    ctrlXmlRoot = f_cache_all_controllers()
    print(_outputHeaderRow.format('Object ID', 'IP Address', 'Status', 'Syslog Server', 'Port', 'Protocol', 'Level'))
    print(_outputHeaderRow.format('-'*15, '-'*13, '-'*8, '-'*27, '-'*5, '-'*8, '-'*6))
    for controller in ctrlXmlRoot.findall('controller'):
        syslogXml = f_query_controller_syslog(controller.find('id').text)
        if (syslogXml == 'Not set'):
            print(_outputDataRow.format(controller.find('id').text,\
                    controller.find('ipAddress').text,\
                    controller.find('status').text,\
                    '',\
                    '',\
                    '',\
                    ''\
                    ))
        else:
            print(_outputDataRow.format(controller.find('id').text,\
                    controller.find('ipAddress').text,\
                    controller.find('status').text,\
                    syslogXml.find('syslogServer').text,\
                    syslogXml.find('port').text,\
                    syslogXml.find('protocol').text,\
                    syslogXml.find('level').text\
                    ))
    f_log('SUCCESS: Displayed list of controllers.')
    print('')

def f_delete_controller_syslog(id):
    _del_controller_syslog_url = 'https://%s/api/2.0/vdn/controller/%s/syslog' % (_nsxmgr,id)
    _del_controller_syslog_reponse = requests.delete((_del_controller_syslog_url), headers=_nsx_api_headers, auth=(_user, _password), verify=False)

    if int(_del_controller_syslog_reponse.status_code) == 200:
        print('SUCCESS: Deleted syslog server configuration on %s' % id)
        f_log('SUCCESS: Deleted syslog server configuration on %s' % id)
    else:
        print('ERROR: Something went wrong deleting the syslog server configuration on %s - Check log file.' % id)
        f_log('ERROR: Something went wrong deleting the syslog server configuration on %s - Check log file.' % id)
        f_log(_del_controller_syslog_reponse.content)

def f_add_controller_syslog(id,server,port,protocol,level):
    _add_controller_syslog_xml = '<controllerSyslogServer>'\
                                    '<syslogServer>' + server + '</syslogServer>'\
                                    '<port>' + port + '</port>'\
                                    '<protocol>' + protocol + '</protocol>'\
                                    '<level>' + level + '</level>'\
                                    '</controllerSyslogServer>'

    _add_controller_syslog_url = 'https://%s/api/2.0/vdn/controller/%s/syslog' % (_nsxmgr, id)
    _add_controller_syslog_reponse = requests.post((_add_controller_syslog_url), data=_add_controller_syslog_xml, headers=_nsx_api_headers, auth=(_user, _password), verify=False)

    if int(_add_controller_syslog_reponse.status_code) != 200:
        _add_controller_syslog_data = _add_controller_syslog_reponse.content
        _add_controller_syslog_root = ET.fromstring(_add_controller_syslog_data)
        if (_add_controller_syslog_root.find('details').text == '409 Conflict'):
            print('ERROR: Syslog servers are already set on %s. Delete settings before trying to add new ones.' % id)
            f_log('ERROR: Syslog servers are already set on %s. Delete settings before trying to add new ones.' % id)
            f_log('ERROR: %s' % ET.tostring(_add_controller_syslog_root))
            return 'Conflict'
        return
    else:
        print ('SUCCESS: Configured syslog server %s on %s' % (server,id))
        f_log ('SUCCESS: Configured syslog server %s on %s' % (server,id))

f_log('Script start.')

if _listControllers != None:
    f_list_controllers('Current Settings')

elif _addServers != None:
    f_list_controllers('Old Settings')
    ctrlXmlRoot = f_cache_all_controllers()
    for controller in ctrlXmlRoot.findall('controller'):
        f_add_controller_syslog(controller.find('id').text,_syslogDest,_syslogPort,_syslogProtocol,_syslogLevel)
    f_list_controllers('New Settings')

elif _delServers != None:
    f_list_controllers('Old Settings')
    ctrlXmlRoot = f_cache_all_controllers()
    for controller in ctrlXmlRoot.findall('controller'):
        f_delete_controller_syslog(controller.find('id').text)
    f_list_controllers('New Settings')

print('')
f_log('Script end.')

