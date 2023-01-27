#import-data
import pyfiglet
from pyfiglet import Figlet
import ip2geotools
from ip2geotools.databases.noncommercial import DbIpCity
#ascii_banner/description
ascii_banner = pyfiglet.figlet_format("locus.")
print(ascii_banner)

#main_code
print("**********************")
x = input("Would you like to scan an ip today?: ")
while x != "no" or "No":
    ip = input("Enter target ip: ")
    response = DbIpCity.get(ip, api_key="free")
    print("~~~~~~~~~~~~~~~~~~~~~~")
    print("Your target's ip address is : {0}".format(response.ip_address))
    print("----------------------")
    print("Your target's region is : {0}".format(response.region))
    print("----------------------")
    print("Your target's country is : {0}".format(response.country))
    print("----------------------")
    print("Your target's city is : {0}".format(response.city))
    print("----------------------")
    print("Your target's longitude is : {0}".format(response.longitude))
    print("----------------------")
    print("Your target's latitude is : {0}".format(response.latitude))
    print("~~~~~~~~~~~~~~~~~~~~~~")
    print("**********************")
y = input("Are you sure? (y for yes, n for no): ")
if y == "y" or "Y":
    quit()
elif y == "n" or "N":
    ip = input("Enter target ip: ")
    response = DbIpCity.get(ip, api_key="free")
    print("~~~~~~~~~~~~~~~~~~~~~~")
    print("Your target's ip address is : {0}".format(response.ip_address))
    print("----------------------")
    print("Your target's region is : {0}".format(response.region))
    print("----------------------")
    print("Your target's country is : {0}".format(response.country))
    print("----------------------")
    print("Your target's city is : {0}".format(response.city))
    print("----------------------")
    print("Your target's longitude is : {0}".format(response.longitude))
    print("----------------------")
    print("Your target's latitude is : {0}".format(response.latitude))
    print("~~~~~~~~~~~~~~~~~~~~~~")
    print("**********************")
