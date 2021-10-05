#!/usr/bin/env python3
import requests
import logging
import jwt
import json
import uuid
import time

from dataclasses import dataclass

@dataclass
class CiscoBDOrganisationClass:
    """Cisco Business Dashboard Organisation Class"""

    id: str
    name: str
    description: str
    defaultgroup: str
    networkcount: int
    devicecount: int
    monitorprofiles: str
    changewindowtype: str
    changewindow: str

    @staticmethod
    def from_json(item):
        return CiscoBDOrganisationClass(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            defaultgroup=item["default-group"],
            networkcount=item["network-count"],
            devicecount=item["device-count"],
            monitorprofiles=item["monitor-profiles"],
            changewindowtype=item["change-window-type"],
            changewindow=item["change-window"],
        )

DEFAULT_SOURCE = CiscoBDOrganisationClass
def getToken(keyid,secret,clientid=None,appname="cbdscript.example.com",appver="1.0",lifetime=3600):
  if clientid == None:
    clientid = str(uuid.uuid4())
  claimset = {
    "iss":appname,
    "cid":clientid,
    "appver":appver,
    "aud":"business-dashboard.cisco.com",
    "iat":int(time.time()),
    "exp":int(time.time()+lifetime)
  }

  return jwt.encode(claimset,secret,algorithm='HS256',headers={'kid':keyid})

#Create Token

## Currently only returns json information on the default organisation
def get_default_organisation(dashboard,port,keyid,secret,clientid,appname,verify_cbd_cert,source=DEFAULT_SOURCE):
    token = getToken(keyid,secret,clientid,appname)
    try:
        # Build and send the API request.  The getOrganizations API path is
        # /api/v2/orgs
        response=requests.get('https://%s:%s/api/v2/orgs' %
                         (dashboard, port),
                          headers={'Authorization':"Bearer %s" % token},
                          verify=verify_cbd_cert)

    except requests.exceptions.RequestException as e:
        # Generally this will be a connection error or timeout.  HTTP errors are
        # handled in the else section below
        print("Failed with exception:",e)
        sys.exit(1)

    else:
        if response.status_code == 200:
            organisations = response.json()

            for organisation in organisations['data']:
                if 'default' in organisation:
                    results = []
                    try:
                        results.append(source.from_json(organisation))
                    except KeyError:
                        logging.getLogger(__name__).warning("Got wrong data: %s", item)
        else:
            # Some other error occurred.
            print('HTTPError:',response.status_code,response.headers)

             # Most errors return additional information as a json payload
            if 'application/json' in response.headers['Content-Type']:
                print('Error payload:')
                print(json.dumps(response.json(),indent=2))
    return results

