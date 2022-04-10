import requests as reqs
from requests import get
import urllib3 as urll3
import os
import pickle
from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
import socket


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


def BrowseEndpoint(addF):
    res = get("https://discovery.meethue.com/")
    for bridge in res.json():
        addF(name=bridge["name"], ip=bridge["internalipaddress"])


def BrowseMdns(target, addF):
    zeroConf = Zeroconf()
    listener = __mdns_listener(add=addF)
    browser = ServiceBrowser(zeroConf, target, listener)
    sleep(3)
    zeroConf.close()


class Hue:
    def __init__(self, ip=None):
        self.requests = reqs
        self.urllib3 = urll3

        self.__bridge = None
        self.__discovered_bridges = []

        self.__discoveryTried = 0

        self.__workingDir = os.getcwd()
        self.__ip_path = f"{self.__workingDir}/.cached_ip_important"
        self.__username_path = f"{self.__workingDir}/.cached_username_important"

        self.__startupLogic(ip)

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

        BrowseMdns("_hue._tcp.local.", lambda name,
                   ip: self.__discovered_bridges.append({"name": name, "ip": ip}))

        if len(self.__discovered_bridges) == 0:
            BrowseEndpoint(lambda name,
                           ip: self.__discovered_bridges.append({"name": name, "ip": ip}))

        if len(self.__discovered_bridges) >= 2:
            raise Exception(
                "Found more than one bridge, please specify the IP address of the bridge you want to use with the parameter 'ip'.")
        else:
            self.__bridge_discovered(self.__discovered_bridges[0]["ip"])

    def __bridge_discovered(self, ip):
        self.__bridgeIp = ip
        res = self.__unauthenticated_api_request("GET", url="/0/config")
        if res:
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

        else:
            if self.__discoveryTried > 3:
                raise Exception("Could not find bridge.")

            self.__discover()
            self.__discoveryTried += 1

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

    def __ExceptionError(self, res):
        if "error" in res[0]:
            raise Exception(
                f"Error {res[0]['error']['type']}: {res[0]['error']['description']} at {res[0]['error']['address']}")

    def get_all_lights(self):
        devices = []
        devs = self.__authenticated_api_request("GET", url="/lights")

        self.__ExceptionError(devs)

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

    def rename_light(self, deviceId: int, newName: str) -> bool:
        res = self.__authenticated_api_request(
            "PUT", url="/lights/" + str(deviceId), body={"name": newName})
        self.__ExceptionError(res)

        return True

    def delete_light(self, deviceId: int) -> bool:
        res = self.__authenticated_api_request(
            "DELETE", url="/lights/" + str(deviceId))
        self.__ExceptionError(res)

        return True

    def get_light(self, deviceId: int) -> dict:
        dev = self.__authenticated_api_request(
            "GET", url="/lights/" + str(deviceId))
        self.__ExceptionError(dev)

        return({
            "type": dev["type"],
            "manufacturer": dev["manufacturername"],
            "productName": dev["productname"],
            "modelId": dev["modelid"],
            "name": dev["name"],
            "state": {
                "on": dev["state"]["on"],
                "bri": dev["state"]["bri"],
                "hue": dev["state"]["hue"],
                "sat": dev["state"]["sat"],
                "xy": dev["state"]["xy"],
                "ct": dev["state"]["ct"],
                "alert": dev["state"]["alert"],
                "effect": dev["state"]["effect"],
                "colormode": dev["state"]["colormode"],
                "reachable": dev["state"]["reachable"],
            }
        })

    def onOff_light_toggle(self, deviceId: int) -> str:
        res = self.__authenticated_api_request(
            "PUT", url="/lights/" + str(deviceId) + "/state", body={"on": not self.get_light(deviceId)["state"]["on"]})
        self.__ExceptionError(res)

        return self.get_light(deviceId)["state"]["on"]

    def onOff_light_set(self, deviceId: int, onOff: bool) -> str:
        res = self.__authenticated_api_request(
            "PUT", url="/lights/" + str(deviceId) + "/state", body={"on": onOff})
        self.__ExceptionError(res)

        return self.get_light(deviceId)["state"]["on"]

    def get_onOff(self, deviceId: int):
        return self.get_light(deviceId=deviceId)["state"]["on"]

    def set_light_custom(self, deviceId: int, customData: dict) -> dict:
        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body=customData)
        self.__ExceptionError(res)

        return self.get_light(deviceId)["state"]

    def set_light_brightness(self, deviceId: int, brightness: int) -> int:
        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body={"bri": brightness})
        self.__ExceptionError(res)

        return int(self.get_light(deviceId)["state"]["bri"])

    def get_light_brightness(self, deviceId: int) -> int:
        return int(self.get_light(deviceId)["state"]["bri"])

    def set_light_saturation(self, deviceId: int, saturation: int):
        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body={"sat": saturation})
        self.__ExceptionError(res)

        return int(self.get_light(deviceId)["state"]["sat"])

    def get_light_saturation(self, deviceId: int) -> int:
        return int(self.get_light(deviceId)["state"]["sat"])

    def set_light_breathing(self, deviceId: int, breathing: str) -> str:
        if breathing == "long":
            brth = "lselect"
        elif breakpoint == "once":
            brth = "select"
        else:
            brth = "none"

        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body={"alert": brth})
        self.__ExceptionError(res)

        if self.get_light(deviceId)["state"]["alert"] == "lselect":
            return "long"
        elif self.get_light(deviceId)["state"]["alert"] == "select":
            return "once"
        else:
            return "none"

    def colorloop_light_toggle(self, deviceId: int) -> str:
        val = self.get_light(deviceId)["state"]["effect"]
        if val == "none":
            val = "colorloop"
        else:
            val = "none"

        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body={"effect": val})
        self.__ExceptionError(res)

        return self.get_light(deviceId)["state"]["effect"]

    def colorloop_light_set(self, deviceId: int, effect: bool) -> str:
        if effect == True:
            val = "colorloop"
        else:
            val = "none"

        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body={"effect": val})
        self.__ExceptionError(res)

        if self.get_light(deviceId)["state"]["effect"] == "colorloop":
            return True
        else:
            return False

    def get_light_effect(self, deviceId: int) -> dict:
        return({
            'effect': self.get_light(deviceId)["state"]["effect"],
            'breathing': self.get_light(deviceId)["state"]["alert"]
        })

    def rgb2xyb(self, rgbTuple: tuple[int, int, int]):
        r = rgbTuple[0]
        g = rgbTuple[1]
        b = rgbTuple[2]

        r = ((r+0.055)/1.055)**2.4 if r > 0.04045 else r/12.92
        g = ((g+0.055)/1.055)**2.4 if g > 0.04045 else g/12.92
        b = ((b+0.055)/1.055)**2.4 if b > 0.04045 else b/12.92

        X = r * 0.4124 + g * 0.3576 + b * 0.1805
        Y = r * 0.2126 + g * 0.7152 + b * 0.0722
        Z = r * 0.0193 + g * 0.1192 + b * 0.9505

        return X / (X + Y + Z), Y / (X + Y + Z), int(Y*254)

    def set_light_color(self, deviceId, rgbTuple: tuple[int, int, int]) -> list:
        x, y, b = self.rgb2xyb(rgbTuple)

        res = self.__authenticated_api_request(
            "PUT", url=f"/lights/{deviceId}/state", body={"xy": [x, y]})
        self.__ExceptionError(res)

        return self.get_light(deviceId)["state"]["xy"]
