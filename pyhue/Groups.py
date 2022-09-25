from .Bridge import Bridge
from .Lights import Lights

class Groups(object):
    def __init__(self, bridge: Bridge, groupId: int):

        self.__brid = bridge
        self.__id = groupId

        self.__LightHandlers = [
            Lights(bridge, lightId) for lightId in self.group["lights"]
        ]

    def __ExceptionError(self, res):
        if "error" in res[0]:
            raise Exception(
                f"Error {res[0]['error']['type']}: {res[0]['error']['description']} at {res[0]['error']['address']}")


    @property
    def group(self) -> dict:
        dev = self.__brid.api_request(
            "GET", url="/groups/" + str(self.__id))

        return({
            "name": dev["name"],
            "type": dev["type"],
            "class": dev["class"],
            "lights": dev["lights"],
            "state": {
                "all_on": dev["state"]["all_on"],
                "any_on": dev["state"]["any_on"],
            },
            "action": dev["action"]
        })


    @property
    def lights(self) -> list:
        return self.__LightHandlers
    