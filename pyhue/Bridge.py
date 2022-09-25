import requests as reqs
import os
from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
import socket

def __ExceptionError(res):
    if "error" in res[0]:
        raise Exception(
            f"Error {res[0]['error']['type']}: {res[0]['error']['description']} at {res[0]['error']['address']}")

class Bridge(object):
    def __init__(self, ip=None):
        self.requests = reqs.Session()

        self.__bridge = None
        self.__discovered_bridges = []

        self.__discoveryTried = 0

        self.__workingDir = os.getcwd()
        self.__ip_path = f"{self.__workingDir}/.cached_ip_important"
        self.__username_path = f"{self.__workingDir}/.cached_username_important"

        self.__startupLogic(ip)

    class __mdns_listener:
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

    def __BrowseEndpoint(self, addF):
        res = self.requests.get("https://discovery.meethue.com/")
        for bridge in res.json():
            addF(name=bridge["name"], ip=bridge["internalipaddress"])

    def __BrowseMdns(self, target, addF):
        zeroConf = Zeroconf()
        listener = self.__mdns_listener(add=addF)
        ServiceBrowser(zeroConf, target, listener)
        sleep(3)
        zeroConf.close()

    def __startupLogic(self, ip):
        if os.path.exists(self.__ip_path):
            with open(self.__ip_path, 'r') as f:
                dat = f.read()
                if dat != "":
                    self.__bridge_discovered(dat)
                else:
                    self.__discover()
        elif ip:
            self.__bridge_discovered(ip)
        else:
            self.__discover()

    def __discover(self, ip=None):
        if ip is not None:
            self.__bridge_discovered(ip)

        self.__BrowseMdns("_hue._tcp.local.", lambda name,
                          ip: self.__discovered_bridges.append({"name": name, "ip": ip}))

        if len(self.__discovered_bridges) == 0:
            self.__BrowseEndpoint(lambda name,
                                  ip: self.__discovered_bridges.append({"name": name, "ip": ip}))
        if len(self.__discovered_bridges) == 0:
            raise Exception("Could not find bridge.")

        if len(self.__discovered_bridges) >= 2:
            raise Exception(
                "Found more than one bridge, please specify the IP address of the bridge you want to use with the parameter 'ip'. Discovered bridges: " + str(self.__discovered_bridges))
        else:
            self.__bridge_discovered(self.__discovered_bridges[0]["ip"])

    def __bridge_discovered(self, ip):
        self.__bridgeIp = ip
        res = None
        try:
            res = self.__unauthenticated_api_request("GET", url="/0/config")
        except:
            if self.__discoveryTried > 3:
                raise Exception("Could not find bridge.")

            self.__discover()
            self.__discoveryTried += 1
        else:
            with open(self.__ip_path, 'w') as f:
                self.__bridgeIp = ip
                f.write(ip)

            if os.path.exists(self.__username_path):
                with open(self.__username_path, 'r') as f:
                    dat = f.read()
                    if dat != "":
                        self.__bridge = {
                            "ip": ip,
                            "name": res["name"],
                            "mac": res["mac"],
                            "username": dat
                        }
                    else:
                        self.__authenticate(ip, resJson=res)
            else:
                self.__authenticate(ip, resJson=res)

    def __authenticate(self, ip, resJson):
        authReqJsonOne = self.__unauthenticated_api_request(
            "POST", url="", body={"devicetype": "PyHue"})

        if authReqJsonOne[0]["error"]["type"] == 101:
            sel = input(
                "Please press the Blue Button on the Hue-Bridge and then enter on your keyboard!")
            authReqJson = self.__unauthenticated_api_request(
                "POST", url="", body={"devicetype": "PyHue"})

            if authReqJson[0]["success"]["username"] is not None:
                with open(self.__username_path, 'w') as f:
                    f.write(authReqJson[0]["success"]["username"])
                self.__bridge = {
                    "ip": ip,
                    "name": resJson["name"],
                    "swversion": resJson["swversion"],
                    "mac": resJson["mac"],
                    "username": authReqJson[0]["success"]["username"]
                }
            else:
                raise Exception("Could not authenticate.")

        elif authReqJsonOne[0]["success"]["username"] is not None:
            with open('./.cached_username_important', 'w') as f:
                f.write(authReqJsonOne[0]["success"]["username"])
            self.__bridge = {
                "ip": ip,
                "name": resJson["name"],
                "swversion": resJson["swversion"],
                "mac": resJson["mac"],
                "username": authReqJsonOne[0]["success"]["username"]
            }
        else:
            raise Exception("Could not authenticate.")

    def __unauthenticated_api_request(self, method, url, body=None) -> dict:
        if body is None:
            body = {}

        res = self.requests.request(
            method, "http://" + self.__bridgeIp + "/api" + url, json=body)

        if res.status_code == 200:
            return res.json()
        else:
            raise Exception("Error: " + str(res.status_code) + " " + res.text)

    def __authenticated_api_request(self, method, url, body=None) -> dict:
        if body is None:
            body = {}

        res = self.requests.request(
            method, "http://{ipA}/api/{uN}{url}".format(ipA=self.__bridge["ip"], uN=self.__bridge["username"], url=url), json=body)

        if res.status_code == 200:
            return res.json()
        else:
            raise Exception("Error: " + str(res.status_code) + " " + res.text)

    def api_request(self, method, url, body={}) -> dict:
        bud = self.__authenticated_api_request(
            method=method, url=url, body=body)
        return bud

    # Getters:
    def get_all_lights(self):
        devices = []
        devs = self.api_request("GET", url="/lights")

        for dev in devs:
            devices.append({
                "id": int(dev),
                "type": devs[dev]["type"],
                "manufacturer": devs[dev]["manufacturername"],
                "productName": devs[dev]["productname"],
                "modelId": devs[dev]["modelid"],
                "name": devs[dev]["name"],
            })
        return(devices)

    def get_all_groups(self):
        groups = []
        grps = self.api_request("GET", url="/groups")

        for grp in grps:
            groups.append({
                "id": int(grp),
                "name": grps[grp]["name"],
                "lights": grps[grp]["lights"],
                "type": grps[grp]["type"],
                "state": grps[grp]["action"],
            })
        return(groups)


    def rename_light(self, deviceId: int, newName: str) -> bool:
        res = self.api_request(
            "PUT", url="/lights/" + str(deviceId), body={"name": newName})
        __ExceptionError(res)

        return True

    def delete_light(self, deviceId: int) -> bool:
        res = self.api_request(
            "DELETE", url="/lights/" + str(deviceId))
        __ExceptionError(res)

        return True