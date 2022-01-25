"""Cisco Business Dashboard PyPi library"""
import logging
import uuid
import time
from dataclasses import dataclass
import jwt
import json
import types

from aiohttp import ClientSession, ClientResponseError


@dataclass
class CiscoBDSettingsClass:
    """Cisco Business Dashboard Settings Class"""

    dashboard = ""
    port = ""
    keyid = ""
    secret = ""
    appname = "cbdscript.example.com"
    appver = "1.0"
    clientid = str(uuid.uuid4())
    token = ""
    lifetime = 3600

    def __init__(self, dashboard, port, secret, keyid):
        self.dashboard = dashboard
        self.port = port
        self.secret = secret
        self.keyid = keyid

    def gen_token(self) -> str:
        """Generate authentication token"""
        print("Generating Token JWT !")
        claimset = {
            "iss": self.appname,
            "cid": self.clientid,
            "appver": self.appver,
            "aud": "business-dashboard.cisco.com",
            "iat": int(time.time()),
            "exp": int(time.time() + self.lifetime),
        }

        self.token = jwt.encode(
            claimset, self.secret, algorithm="HS256", headers={"kid": self.keyid}
        )

        return self.token

    def __setattr__(self, name: str, value):
        """Generate new token when attributes changes"""
        self.__dict__[name] = value
        if "token" not in name:
            if "" not in (self.dashboard, self.port, self.keyid, self.secret):
                print("Generate new Token")
                self.gen_token()


@dataclass
class CiscoBDNodeClass:
    """Cisco Business Dashboard Node Class"""

    # id: str = ""
    # global serial
    # systemstate: str = ""
    alert: int
    info: int
    warn: int
    normal: int

    hostname: str = ""
    type: str = ""
    ipaddress: str = ""
    overallstate: str = ""
    state: str = ""

    @staticmethod
    def __json_extract(obj, key):
        """Recursively fetch values from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        values = extract(obj, arr, key)
        return values[0]

    @staticmethod
    def from_json(item):
        """load json results into Node Class"""

        return CiscoBDNodeClass(
            overallstate=CiscoBDNodeClass.__json_extract(item, "overall"),
            info=CiscoBDNodeClass.__json_extract(item, "info"),
            warn=CiscoBDNodeClass.__json_extract(item, "warn"),
            normal=CiscoBDNodeClass.__json_extract(item, "normal"),
            alert=CiscoBDNodeClass.__json_extract(item, "alert"),
            hostname=item["hostname"],
            type=item["type"],
            ipaddress=item["ip"],
        )


@dataclass
class CiscoBDOrganisationClass:
    """Cisco Business Dashboard Organisation Class"""

    id: str
    organisation: str
    description: str
    defaultgroup: str
    networkcount: int
    devicecount: int
    monitorprofiles: str
    changewindowtype: str
    changewindow: str

    @staticmethod
    def from_json(item):
        """load json results into Organisation Class"""
        # id = item
        return CiscoBDOrganisationClass(
            id=item["id"],
            organisation=item["name"],
            description=item["description"],
            defaultgroup=item["default-group"],
            networkcount=item["network-count"],
            devicecount=item["device-count"],
            monitorprofiles=item["monitor-profiles"],
            changewindowtype=item["change-window-type"],
            changewindow=item["change-window"],
        )


OrganisationSource = CiscoBDOrganisationClass
NodeSource = CiscoBDNodeClass


# Create acces token
def get_token(
    keyid,
    secret,
    clientid=None,
    appname="cbdscript.example.com",
    appver="1.0",
    lifetime=3600,
):
    """Generate token for authentication"""
    if clientid is None:
        clientid = str(uuid.uuid4())
    claimset = {
        "iss": appname,
        "cid": clientid,
        "appver": appver,
        "aud": "business-dashboard.cisco.com",
        "iat": int(time.time()),
        "exp": int(time.time() + lifetime),
    }

    return jwt.encode(claimset, secret, algorithm="HS256", headers={"kid": keyid})


async def get_node_interfaces(
    session: ClientSession, settings: CiscoBDSettingsClass, source=OrganisationSource
):
    """Get all the information from with different API requests"""
    settings.gen_token()

    # TODO replace UID with function input
    resp = await session.get(
        "https://%s:%s/api/v2/nodes/04aa667e-4d4b-4843-b784-b87521619ede"
        % (settings.dashboard, settings.port),
        headers={"Authorization": "Bearer %s" % settings.token},
    )
    data = await resp.json(content_type=None)

    if "error" in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data["error"]["code"],
            message=data["error"]["message"],
            headers=resp.headers,
        )

    print("Print each key-value pair from JSON response:")
    for key, value in data.items():
        print(key, ":", value)
    interfaces = data["interfaces"]
    print("Interfaces:")
    print(interfaces)

    results = []

    for item in interfaces:
        print("Interface:" + item["name"])

        interface_details = {"name": None}
        interface_details["name"] = item["name"]
        interface_details["enabled"] = item["enabled"]
        if "poe" in item:
            print("PoE enabled: " + str(item["poe"]["enable"]))
            interface_details["poe"] = item["poe"]
            interface_details["poe-enable"] = item["poe"]["enable"]

        results.append(interface_details)

    return results


async def get_organisation(
    session: ClientSession,
    settings: CiscoBDSettingsClass,
    orgname: str,
    source=OrganisationSource,
):
    """Get the organisation specified in orgname from API"""

    resp = await session.get(
        "https://%s:%s/api/v2/orgs" % (settings.dashboard, settings.port),
        headers={"Authorization": "Bearer %s" % settings.token},
    )
    data = await resp.json(content_type=None)

    if "error" in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data["error"]["code"],
            message=data["error"]["message"],
            headers=resp.headers,
        )

    results = []

    for item in data["data"]:
        if item["name"] == orgname:
            try:
                results.append(source.from_json(item))
            except KeyError:
                logging.getLogger(__name__).warning("Got wrong data: %s", item)

    return results


async def get_default_organisation(
    session: ClientSession, settings: CiscoBDSettingsClass, source=OrganisationSource
):
    """Get the default organisation from API"""
    settings.gen_token()
    resp = await session.get(
        "https://%s:%s/api/v2/orgs" % (settings.dashboard, settings.port),
        headers={"Authorization": "Bearer %s" % settings.token},
    )
    data = await resp.json(content_type=None)

    if "error" in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data["error"]["code"],
            message=data["error"]["message"],
            headers=resp.headers,
        )

    results = []

    for item in data["data"]:
        if "default" in item:
            try:
                results.append(source.from_json(item))
            except KeyError:
                logging.getLogger(__name__).warning("Got wrong data: %s", item)

    return results


async def get_organisation_id(
    session: ClientSession, settings: CiscoBDSettingsClass, orgname: str
):
    """input organisation name return the organisation id"""

    resp = await session.get(
        "https://%s:%s/api/v2/orgs" % (settings.dashboard, settings.port),
        headers={"Authorization": "Bearer %s" % settings.token},
    )
    data = await resp.json(content_type=None)

    for item in data["data"]:
        if item["name"] == orgname:
            return item["id"]

    return None


async def get_nodes_organisation(
    session: ClientSession,
    settings: CiscoBDSettingsClass,
    orgname,
    source=NodeSource,
):
    """Get the nodes attached to orgid from API"""
    orgid = await get_organisation_id(session, settings, orgname)
    print("get_nodes_organisation: ", orgid)

    resp = await session.get(
        "https://%s:%s/api/v2/nodes?fields=/system-state/hostname,/system-state/type,/system-state/ip,/system-state/sn&type=Device"
        % (settings.dashboard, settings.port),
        headers={"Authorization": "Bearer %s" % settings.token, "x-ctx-org-id": orgid},
    )
    data = await resp.json()

    if "error" in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data["error"]["code"],
            message=data["error"]["message"],
            headers=resp.headers,
        )

    results = []

    for item in data["data"]:
        try:
            results.append(source.from_json(item["system-state"]))
        except KeyError:
            logging.getLogger(__name__).warning("Got wrong data: %s", item)

    return results
