"""Cisco Business Dashboard PyPi library"""
import logging
import uuid
import time
from dataclasses import dataclass
import jwt

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
    hostname: str = ""
    type: str = ""
    ipaddress: str = ""

    # states: str = ""

    @staticmethod
    def from_json(item):
        """load json results into Node Class"""
        print("item:")
        print(item)

        # if "states" in item:
        #    states = item["states"]
        # if "sn" in item:
        #    serial = item["sn"]

        return CiscoBDNodeClass(
            # serial,
            # states,
            # id=item["id"],
            #    systemstate=item,
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
    print("raw data:")
    print(data)
    for item in data["data"]:
        try:
            results.append(source.from_json(item["system-state"]))
        except KeyError:
            logging.getLogger(__name__).warning("Got wrong data: %s", item)

    return results
