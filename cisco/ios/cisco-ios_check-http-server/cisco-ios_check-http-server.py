import os
from netmiko import ConnectHandler
from getpass import getpass
from datetime import datetime

#
# MUST HAVE VALID IP LIST FILE - devices.txt - ONE IP ADDRESS OR RESOLVABLE HOSTNAME PER LINE, should live in same folder as this script
# Credentials will be entered once manually using input and GetPass
#
# Comments in the devices.txt file are ok with line starting with the "#" character
# ONE IP address or resolvable hostname per line
#
# This script currently runs serially, one device at a time.
#
# If connection fails for any reason, script will stop at that point.
#
#

working_dir = os.getcwd()
list_of_ip = []
httpCount = 0
httpList = []
username = input("Username:")
password = getpass()

if __name__ == "__main__":

    # pull device list from devices.txt file into list_of_ip list.
    try:
        with open(working_dir + '/devices.txt', 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                line = line.strip()
                line = line.strip('\"')
                line = line.strip("\'")
                if line.startswith('#'):
                    pass
                else:
                    list_of_ip.append(line)
            if len(list_of_ip) == 0:
                raise ValueError('The devices.txt file has zero entries or is otherwise invalid.')
    except Exception as e:
       print()
       print()
       print("*" * 60)
       print("** FAILURE! **")
       print()
       print('A problem occurred related to the devices.txt file.')
       print()
       print(e)
       print()
       print()

    # Connect to devices and make a list if any have ip http server enabled
    try:
            for ip in list_of_ip:

                device = {
                    'device_type': 'cisco_ios',
                    'ip': ip,
                    'username': username,
                    'password': password
                }

                net_connect = ConnectHandler(**device)

                command1 = "show running-config | include hostname"
                command2 = "show running-config | include ip http"
                if net_connect.send_command(command2, use_textfsm=True).startswith("ip http"):
                    httpCount += 1
                    httpList.append(device['ip'])
                net_connect.disconnect()

    except Exception as e:
        print()
        print()    
        print("#" * 80)
        print("FAILURE! - it is possible partial output was successful - check your devices.txt IP address list and formatting")
        print("List of IP addresses, one per line, no quotes, no commas.  If hostname is used, it must be resolvable from the machine running this script")
        print("#" * 80)
        print()
        print("Python Exception message: ")
        print()
        print(e)
        print()
        print()

if len(list_of_ip) > 0:
    print()
    print()
    print("*" * 60)
    print()
    print(str(len(list_of_ip)) + " devices were checked...")
    print()
    print(str(httpCount) + " devices were found with \"ip http(s) servers\" enabled!")
    print()
    print("*" * 60)
    if len(httpList) > 0:
        with open("{:output_%Y-%B-%d_%H-%M-%S%z.txt}".format(datetime.now()), "a") as outfile:
            print("# List of offending devices below", file=outfile)
            print()
            print(" ** List of offending devices below **")
            print()
            print("*" * 16)
            for i in httpList:
                print(i)
                print(i, file=outfile)
            print("*" * 16)
            print()
            print("An output file has also been created with this list of offending devices.")
    print()
    print()