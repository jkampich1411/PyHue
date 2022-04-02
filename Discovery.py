from zeroconf import ServiceBrowser, Zeroconf
from requests import get

from time import sleep
import socket


class mdns_listener:
    def __init__(self, add):
        self.__add = add

    def remove_service(self, zeroconf, type, name):
        "empty"

    def update_service(self, zeroconf, type, name):
        "empty"

    def add_service(self, zeroconf, type, name):
        serviceInfo = zeroconf.get_service_info(type, name)
        ip = "err"
        if serviceInfo:
            ip = socket.inet_ntoa(serviceInfo.addresses[0])

        self.__add(name=name, ip=ip)


def BrowseEndpoint(addF):
    res = get("https://discovery.meethue.com/")
    for bridge in res.json():
        addF(name=bridge["name"], ip=bridge["internalipaddress"])


def BrowseMdns(target, addF):
    zeroConf = Zeroconf()
    listener = mdns_listener(add=addF)
    browser = ServiceBrowser(zeroConf, target, listener)
    sleep(3)
    zeroConf.close()
