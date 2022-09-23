from .Bridge import Bridge

from .libs import Converter as __conv
__colourc = __conv()



class Lights(object):
    def __init__(self, bridge: Bridge, lightId: int):
        self.__brid = bridge
        self.__id = lightId
    
    def __ExceptionError(self, res):
        if "error" in res[0]:
            raise Exception(
                f"Error {res[0]['error']['type']}: {res[0]['error']['description']} at {res[0]['error']['address']}")


    def set_custom(self, customData: dict) -> dict:
        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body=customData)
        self.__ExceptionError(res)

        return self.light["state"]


    @property
    def light(self) -> dict:
        dev = self.__brid.api_request(
            "GET", url="/lights/" + str(self.__id))

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
                "colourmode": dev["state"]["colormode"],
                "reachable": dev["state"]["reachable"],
            }
        })
    

    @property
    def power(self):
        return self.light["state"]["on"]

    @power.setter
    def power(self, onOff: bool) -> str:
        res = self.__brid.api_request(
            "PUT", url="/lights/" + str(self.__id) + "/state", body={"on": onOff})
        self.__ExceptionError(res)

        return self.light["state"]["on"]

    def toggle_power(self) -> str:
        res = self.__brid.api_request(
            "PUT", url="/lights/" + str(self.__id) + "/state", body={"on": not self.light["state"]["on"]})
        self.__ExceptionError(res)

        return self.light["state"]["on"]


    @property
    def brightness(self) -> int:
        return int(self.light["state"]["bri"])
    
    @brightness.setter
    def brightness(self, brightness: int) -> int:
        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body={"bri": brightness})
        self.__ExceptionError(res)

        return int(self.light["state"]["bri"])


    @property
    def saturation(self) -> int:
        return int(self.light["state"]["sat"])

    @saturation.setter
    def saturation(self, saturation: int) -> int:
        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body={"sat": saturation})
        self.__ExceptionError(res)

        return int(self.light["state"]["sat"])


    @property
    def breathing(self) -> bool:
        return not not self.light["state"]["alert"]

    @breathing.setter
    def breathing(self, breathing: str) -> str:
        if breathing == "long":
            brth = "lselect"
        elif breathing == "once":
            brth = "select"
        else:
            brth = "none"

        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body={"alert": brth})
        self.__ExceptionError(res)

        if self.light["state"]["alert"] == "lselect":
            return "long"
        elif self.light["state"]["alert"] == "select":
            return "once"
        else:
            return "none"


    @property
    def colourloop(self) -> bool:
        if self.light["state"]["effect"] == "colorloop":
            return True

        return False
    
    @colourloop.setter
    def colourloop(self, effect: bool) -> str:
        if effect == True:
            val = "colorloop"
        else:
            val = "none"

        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body={"effect": val})
        self.__ExceptionError(res)

        if self.light["state"]["effect"] == "colorloop":
            return True
        else:
            return False

    def toggle_colourloop(self) -> str:
        val = self.light["state"]["effect"]
        if val == "none":
            val = "colorloop"
        else:
            val = "none"

        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body={"effect": val})
        self.__ExceptionError(res)

        return self.light["state"]["effect"]


    @property
    def colour(self) -> tuple:
        xy = self.light["state"]["xy"]
        x, y = xy[0], xy[1]

        bri = self.light["state"]["bri"]

        return __colourc.xy_to_rgb(x, y, bri)
    
    @colour.setter
    def colour(self, rgbTuple: tuple[int, int, int]) -> list:
        xy = __colourc.rgb_to_xy(rgbTuple[0], rgbTuple[1], rgbTuple[2])
        x, y = xy[0], xy[1]

        res = self.__brid.api_request(
            "PUT", url=f"/lights/{self.__id}/state", body={"xy": [x, y]})
        self.__ExceptionError(res)

        return self.light["state"]["xy"]