#!/usr/bin/env python3
import requests
import json
import argparse
import logging

import environment
import cbdauth

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

#Create Token
token = cbdauth.getToken(keyid=environment.keyid,
                            secret=environment.secret,
                            clientid=environment.clientid,
                            appname=environment.appname)

## Currently only returns json information on the default organisation
def get_default_organisation(source=DEFAULT_SOURCE):
    try:
        # Build and send the API request.  The getOrganizations API path is
        # /api/v2/orgs
        response=requests.get('https://%s:%s/api/v2/orgs' %
                         (environment.dashboard, environment.port),
                          headers={'Authorization':"Bearer %s" % token},
                          verify=environment.verify_cbd_cert)

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

org = get_default_organisation()
print(org)

