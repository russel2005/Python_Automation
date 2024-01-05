from pyzabbix.api import ZabbixAPI
from sys import path
import os
project_root = os.path.dirname(os.path.realpath(__file__))
path.append(os.path.join(project_root, '..'))
from utils.config import read_config
from utils.devices import read_devices_name, update_device_status, update_devie_group, update_device_status_problem
from utils.util import extract_number_from_sitename
import ipaddress
from utils.logging_utils import setup_logging


logger = setup_logging('zabbix_api.log', 'zabbix_api')
# Define a custom exception class
class NoSiteDetailsError(Exception):
    pass


class ZabbixApiClient:
    def __init__(self):
        self.config = read_config()
        self.zabbix_api_conn = self.api_connect(self.config)

    def api_connect(self,config):
        UserName = config.get('Zabbix', 'UserName')
        Password = config.get('Zabbix', 'Password')
        URL = config.get('ZabbixAPI', 'URL')
        # print("Value of U and P: ", UserName, Password)

        try:
            zapi = ZabbixAPI(url=URL, user=UserName, password=Password)
            logger.info("Zabbix API connected successfully...")
            return zapi
        except Exception as e:
            print(f"Error connecting to Zabbix API: {e}")
            logger.error(f"Error connecting to Zabbix API: {e}")
            return None

    def get_site_level_details(self, zabbix_api_conn, site_name):
        try:
            site_level_details = zabbix_api_conn.host.get(
                output='extend',
                search={'name': site_name},
                selectItems=["name", "key_", "status", "value_type", 'lastcheck', 'lastvalue', 'valuemapid'],
                selectTriggers=["expression", "description", "value"],
                selectInventory='extend',
                selectInterfaces='extend'
            )

            # Check if site_level_details is empty or None
            if not site_level_details:
                raise NoSiteDetailsError(f"No site-level details found for site: {site_name}")

            return site_level_details
        except Exception as e:
            print(f"Error retrieving site level details: {e}")
            logger.error(f"Error retrieving site level details: {e}")
            # You can choose to log the error or raise it again, depending on your application's needs
            raise NoSiteDetailsError(f"Error retrieving site level details: {e}")


    def get_device_list_for_site(self,zabbix_api_conn, site_name):
        site_level_details = self.get_site_level_details(zabbix_api_conn, site_name)

        if site_level_details:
            # Create a list of device names
            device_list = [device.get('name') for device in site_level_details]        
            return device_list
        else:
            # Retry with a modified siteName containing only numerical values
            # numeric_sitename = ''.join(c for c in site_name if c.isdigit())
            modified_site_name = extract_number_from_sitename(site_name)
            print(f"Failed to retrieve site level details for {site_name} . Now Retry with only numeric values {modified_site_name}.")
            if modified_site_name.isdigit():            
                print(f"Retrying with modified site name: {modified_site_name}")
                site_level_details = self.get_site_level_details(zabbix_api_conn, modified_site_name)
                print(site_level_details)
                if site_level_details:
                    # Create a list of numeric device names
                    device_list = [device.get('name') for device in site_level_details]        
                    return device_list
            else:
                print("No numeric part found in site name. Cannot retry.")
                return []
    

    def get_maintenance_details_for_site(zabbix_api_conn, site_name):
        try:
            maintenance_details = zabbix_api_conn.maintenance.get(
                                                output='extend', selectHostGroups='extend',
                                                selectTimeperiods='extend', selectTags='extend'
            )
            return maintenance_details
        except Exception as e:
            print(f"Error retrieving maintenance details: {e}")
            return None

    def get_device_status(self, zabbix_api_conn, hostValueMapId, HostItemLastValue):
        """
        rules:
        1) A bad device status will show Down
        2) A good device status will show 'ok or online or up'
        3) an empty "Latest data" also is BAD device
        """

        #Original template to map all values to exact keyword meaning up or down or warning or altering or online 
        ValuemapDetails = zabbix_api_conn.valuemap.get(output='extend', selectMappings='extend', valuemapids=hostValueMapId)
        print("ValuemapDetails:", ValuemapDetails)
        logger.info(f"ValuemapDetails: {ValuemapDetails}")
        host_status = ''

        if ValuemapDetails:
            HostLastValue = ''        
            # first element ValueMapData = ValuemapDetails[0]
            ValueMapData = ValuemapDetails[0]
            # print("Value of ValueMapData: ", ValueMapData)
            Mappings = ValueMapData.get('mappings')
            if Mappings:
                HostLastValue = next((x.get('newvalue') for x in Mappings if x.get('value') == HostItemLastValue), None)
                print("HostLastValue: ", HostLastValue)
                logger.info(f"HostLastValue: {HostLastValue}")
            if HostLastValue and ("ok" in HostLastValue.lower() or "online" in HostLastValue.lower() or "up" in HostLastValue.lower()):
                host_status = "Up"
            # LATER if needed then we can check     
            # elif "Device In Maintenance" in HostMaintenance:
            #     HostStatus = "In Maintenance"
            else:
                host_status = "Down"
        else:
            print("Value Map Details Not Found")
            logger.warn("Value Map Details Not Found")
        
        # print('host_status:', host_status)
        return host_status

    def find_device_problem_exist(self, zabbix_api_conn, triggerid):
        problem_exist = False
        try:
            trigger_problem_events = zabbix_api_conn.problem.get(
                output='extend', selectAcknowledges='extend',
                selectTags='extend', selectSuppressionData='extend',
                objectids=str(triggerid),
                recent='true',
                sortfield=["eventid"],
                sortorder='DESC'
            )
            if trigger_problem_events and isinstance(trigger_problem_events, list):
                first_event = trigger_problem_events[0]
                recovery_eventid = first_event.get('r_eventid') if first_event else None

                if recovery_eventid is not None and len(recovery_eventid) > 1:
                    problem_exist = True

            return problem_exist, trigger_problem_events
        except Exception as e:
            print(f"Error retrieving trigger problem events: {e}")
            logger.debug(f"Error retrieving trigger problem events: {e}")
            return None, None


    def find_device_problem_unresolved(self, zabbix_api_conn, triggerid):
        problem_exist = False
        try:
            trigger_problem_events = zabbix_api_conn.problem.get(
                output='extend', selectAcknowledges='extend',
                selectTags='extend', selectSuppressionData='extend',
                objectids=str(triggerid),
                recent='false',
                sortfield=["eventid"],
                sortorder='DESC'
            )
            if trigger_problem_events and isinstance(trigger_problem_events, list):
                first_event = trigger_problem_events[0]
                recovery_eventid = first_event.get('r_eventid') if first_event else None

                if recovery_eventid is not None and len(recovery_eventid) > 1:
                    problem_exist = True

            return problem_exist, trigger_problem_events
        except Exception as e:
            print(f"Error retrieving trigger problem events: {e}")
            logger.debug(f"Error retrieving trigger problem events: {e}")
            return None, None
    
    def validate_ip(self, ip):
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            # Check if the IP address is not 0.0.0.0
            if ip_obj != ipaddress.IPv4Address('0.0.0.0'):
                return True
            else:
                return False
        except ipaddress.AddressValueError:
            # Raised when the IP address is not a valid IPv4 address
            return False


    def checking_device_dns_ip_port(self,device_interface):
        useip = device_interface[0].get('useip')
        if useip != '':            
            if useip == '1':
                ip = device_interface[0].get('ip')
                port = device_interface[0].get('port')
                dns = device_interface[0].get('dns')

                if ip:
                    print('Device IP is populated:', ip)
                    logger.debug(f'Device IP is populated:{ip}')
                    if self.validate_ip(ip):
                        print(f"{ip} is a valid and not '0.0.0.0'")
                        logger.info(f"IP:{ip} is a valid.")
                    else:
                        print(f"Error: {ip} is either invalid or '0.0.0.0'")
                        logger.error(f"IP: {ip} is either invalid or '0.0.0.0'")
                else:
                    logger.error('Error: Device IP is empty when useip={useip}.')

                if port:
                    print('Device Port is populated:', port)
                    logger.debug(f'Device Port is populated:{port}')
                else:
                    logger.error('Error: Device Port is empty when useip=1.')

                if not dns:
                    logger.debug('Device DNS is empty as expected because ip is populated')
                else:
                    logger.error('Error: Device DNS is populated when useip=1.')

            elif useip == '0':
                ip = device_interface[0].get('ip')
                port = device_interface[0].get('port')
                dns = device_interface[0].get('dns')

                if not ip:
                    print('Device IP is empty.')
                else:
                    print('Error: Device IP is populated when useip=0.')

                if not port:
                    print('Device Port is empty.')
                else:
                    print('Error: Device Port is populated when useip=0.')

                if dns:
                    print('Device DNS is populated:', dns)
                else:
                    print('Error: Device DNS is empty when useip=0.')
        else:
            print('Error: useip could not find in the host interface.')



    def checking_site_devices_status(self):
        
        # config = read_config()
        # zabbix_api_conn = api_connect(config)
        
        site_name_list = read_devices_name()
        print(site_name_list)

        # Create a dictionary to store device status information
        device_status_dict = {}
        device_problem_dict = {}

        # siteName = 'KFC#1435'
        for siteName in site_name_list:
            print("Find all Devices by Device/Host name: ", siteName)
            logger.info(f"Find all Devices by Device/Host name: {siteName}")

            device_list_for_site = self.get_device_list_for_site(self.zabbix_api_conn, siteName)
            print("List of Available Device Names for the Site:", device_list_for_site)
            logger.info(f"List of Available Device Names for the Site: {device_list_for_site}")

            print("=" * 60)
            try:
                SiteLevelDetails = self.get_site_level_details(self.zabbix_api_conn, siteName)
                print("Value of Site Level Details: ", SiteLevelDetails)
                logger.debug(f'Value of Site Level Details: {SiteLevelDetails}')
            except NoSiteDetailsError as e:
                logger.error(f"NoSiteDetailsError: {e}")
            except Exception as e:
                logger.error(f"SiteLevelDetials Unexpected Exception: {e}")

            device_list = []          

            for EachDevice in SiteLevelDetails:
                print("*" * 60)
                device_name = EachDevice.get('name')
                print("Checking Status for Device/Host name: ", device_name)
                logger.info(f"Checking Status for Device/Host name: {device_name}")
                device_list.append(EachDevice.get('name'))

                # # Find the each device items_lastdata
                # items_lastdata = (EachDevice.get('items'))[-1]
                # print(f'Items_lastdata:{items_lastdata}')

                
                logger.info('Verify the status of the device (Up or Down).')
                items = EachDevice.get('items', []) #### what will be the status for eachDevice when find empty items? is that device bad when empty items return?
                
                if items:
                    # Find items first and last data
                    ItemFirstData = items[0]  ## output: {'name': 'ICMP ping', 'key_': 'icmpping', 'status': '0', 'value_type': '3', 'valuemapid': '1', 'lastvalue': '1'}
                    print("Each Device first element of items: ", ItemFirstData)
                    ## below will return latest data
                    ItemLastData = items[-1]    ## output : {'name': 'ICMP response time', 'key_': 'icmppingsec', 'status': '0', 'value_type': '0', 'valuemapid': '0', 'lastvalue': '0.06991000000000001'}
                    print("Each Device  last element of items: ", ItemLastData)
                    
                    # Verify device is Up or Down
                    d_valuemapid = ItemLastData.get('valuemapid')
                    d_lastvalue = ItemLastData.get('lastvalue')
                    print(f"valuemapid:{d_valuemapid} and lastvalue:{d_lastvalue}")
                    device_status = self.get_device_status(self.zabbix_api_conn, d_valuemapid, d_lastvalue)   

                    # Assign device status to the dictionary
                    device_status_dict[device_name] = 'Good' if device_status == 'Up' else ('Bad - no data found' if device_status=='' else 'Bad')                 
                    
                    # Update CSV file with the status                    
                    # update_device_status(device_name, 'Good' if device_status == 'Up' else ('Bad - no data found' if device_status=='' else 'Bad'))
                    # update_device_status(device_name, 'good' if device_status == 'Up' else 'bad')
                    if device_status=='':
                        logger.info('Device Status: Bad - no data found')
                    else:
                        logger.info(f'Device Status: {device_status}')
                else:
                    logger.error(f"Items is empty in the SiteDetails response: {device_name}.") 

                # Verify if the device has any problems.
                logger.info(f'Verify if the device:{device_name} has any problems or not.')
                triggers = EachDevice.get('triggers', []) 
                if triggers:
                    total_triggers = len(EachDevice.get('triggers'))
                    print('total_triggers:', total_triggers)
                    triggers = EachDevice.get('triggers')
                    print('triggers:', triggers)
                    # find the triggerid of each device
                    TriggerFirstId = EachDevice.get('triggers')[0].get('triggerid')
                    print('first triggerid: ', TriggerFirstId)
                    TriggerLastId = EachDevice.get('triggers')[-1].get('triggerid')
                    print('last triggerid: ', TriggerLastId)
                    print("*" * 60) ### find how problem configured in zabbix UI, anc check param 'resent' =true/false, true - return PROBLEM and recently RESOLVED problems , Default: false - UNRESOLVED problems only
                    problem1, trigger1 = self.find_device_problem_exist(self.zabbix_api_conn, TriggerFirstId)
                    print('problem1:',problem1 , '-trigger1:',trigger1)
                    problem2, trigger2 = self.find_device_problem_exist(self.zabbix_api_conn, TriggerLastId)
                    print('problem2:',problem2 , '-trigger2:',trigger2)
                    problem_status = 'No Problems found' if problem2 == False else 'Problems found'

                    device_problem_dict[device_name] = problem_status

                    print(f'problem status:{problem_status}')
                    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

                    problem1, trigger1 = self.find_device_problem_unresolved(self.zabbix_api_conn, TriggerFirstId)
                    print('problem1_unresolved:',problem1 , '-trigger1:',trigger1)
                    problem2, trigger2 = self.find_device_problem_unresolved(self.zabbix_api_conn, TriggerLastId)
                    print('problem2_unresolved:',problem2 , '-trigger2:',trigger2)
                else:
                    print("No Triggers found for the device.")
                    logger.error(f'No Triggers found for the device:{device_name}....')

                ## find problem another way to use trigger
                trigger_response_for_problem0 = self.zabbix_api_conn.trigger.get(triggerids=TriggerFirstId, output='extend', selectFuntions='extend', only_true='0') ### its return empty list, with 'First trigger id', either user only_true == 1 or 0. same output
                print(f"trigger_response0:{trigger_response_for_problem0}")
                trigger_response_for_problem1 = self.zabbix_api_conn.trigger.get(triggerids=TriggerLastId, output='extend', selectFuntions='extend', only_true='1')
                print(f"trigger_response1:{trigger_response_for_problem1}")
            
                  
            print(device_list)    
            
            # break
            # Update CSV file with the status 
            # update_device_status(device_status_dict)  
            update_device_status_problem(device_status_dict,device_problem_dict)  
            print("=" * 60)
            print(f"Device:{device_name} Status checking Done.")
            logger.info(f"Done Device:{device_name} Status checking.....")

    def checking_site_devices_configuration(self):
        logger.info("Checking Device configuration....")
        # config = read_config()
        # zabbix_api_conn = self.api_connect(config)
        
        host_name_list = read_devices_name()
        print(host_name_list)

        # siteName = 'KFC#1435'
        for siteName in host_name_list:
            print("Checking Status for Device/Host name: ", siteName)
            logger.info(f"Find all Devices by Device/Host name: {siteName}")

            device_list_for_site = self.get_device_list_for_site(self.zabbix_api_conn, siteName)
            logger.info(f"Device List for Site:{device_list_for_site}")


            print("*" * 60)
            SiteLevelDetails = self.get_site_level_details(self.zabbix_api_conn, siteName)
            print("Value of Site Level Details: ", SiteLevelDetails)
            logger.info(f"Find Site Level response for the SITENAME: {siteName}")

            device_list = []
            groupsid = set()
            groupsname = set()
            device_name_to_group = {}
            # ip = None
            # port = None
            # dns = None
            for EachDevice in SiteLevelDetails:
                print("*" * 60)
                device_name = EachDevice.get('name')
                print("Device/Host name: ", device_name)
                logger.info(f'Device/Host name: {device_name}.')
                device_list.append(EachDevice.get('name'))
                
                # find hostid, ip, dns, port  ##### how can i validate ip, dns and port? 
                device_interface = EachDevice.get('interfaces')
                print('device_interface:',device_interface)
                # device_interface_len = len(EachDevice.get('interfaces'))
                # print('device_interface length:',device_interface_len)
                if device_interface:

                    #  Checking IP, DNS and PORT
                    self.checking_device_dns_ip_port(device_interface)

                    hostid = device_interface[0].get('hostid')
                    print('hostid:',hostid)
                    hostGroupDetails =self.zabbix_api_conn.hostgroup.get(output='extend', hostids = [hostid])
                    print("Value of hostGroup Details: ", hostGroupDetails)

                    # find the host interface with hostid
                    # hostInterface = zabbix_api_conn.hostinterface.get(output='extend', hostids = hostid)
                    # print("host interface:", hostInterface)
                    
                    # find the devices are in the same group or not
                    host_groupid = hostGroupDetails[0].get('groupid')
                    print('groupid:',host_groupid)
                    groupsid.add(host_groupid)

                    host_groupname = hostGroupDetails[0].get('name')
                    print('group name:',host_groupname)
                    groupsname.add(host_groupname)

                    # update csv file with device group
                    device_name_to_group[device_name] = {host_groupid}

                    #find the list device list by groupid and device_name
                    # hostGroupDetails = zabbix_api_conn.host.get(output=['host'], groupids = host_groupid)
                    # print("devie list by hostgroup: ", hostGroupDetails)

            update_devie_group(device_name_to_group)
            print(device_list)

            if len(groupsid) > 1:
                print("all devices are not in the same group")

            print("*"*60)
            # Verify all devices are in the same group or not
            # hostGroupDetails = zabbix_api_conn.hostgroup.get(output='extend', hostids = ['11638'])
            logger.info(f"Done Device:{device_name} Configuration checking.....")
            break
    
    def run_checks(self):
        self.checking_site_devices_status()
        # self.checking_site_devices_configuration()    

    
