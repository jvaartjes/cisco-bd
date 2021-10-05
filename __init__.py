#!/usr/bin/env python3
import logging
import jwt
import uuid
import time

from dataclasses import dataclass
from aiohttp import ClientSession, ClientResponseError


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
        id = item
        return CiscoBDOrganisationClass(
            id=id["id"],
            organisation=item["name"],
            description=item["description"],
            defaultgroup=item["default-group"],
            networkcount=item["network-count"],
            devicecount=item["device-count"],
            monitorprofiles=item["monitor-profiles"],
            changewindowtype=item["change-window-type"],
            changewindow=item["change-window"],
        )


DEFAULT_SOURCE = CiscoBDOrganisationClass

# Create acces token
def getToken(
    keyid,
    secret,
    clientid=None,
    appname="cbdscript.example.com",
    appver="1.0",
    lifetime=3600,
):
    if clientid == None:
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


## Currently only returns json information on the default organisation
async def get_default_organisation(
    session: ClientSession,
    *,
    dashboard,
    port,
    keyid,
    secret,
    clientid,
    appname,
    source=DEFAULT_SOURCE
):
    token = getToken(keyid, secret, clientid, appname)

    resp = await session.get(
        "https://%s:%s/api/v2/orgs" % (dashboard, port),
        headers={"Authorization": "Bearer %s" % token},
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
