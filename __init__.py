#!/usr/bin/env python3
import aiohttp
import asyncio
import requests
import json
import argparse

import environment
import cbdauth

## Currently only returns json information on the default organisation
def get_organisations():
    token = cbdauth.getToken(keyid=environment.keyid,
                            secret=environment.secret,
                            clientid=environment.clientid,
                            appname=environment.appname)

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
                    print("Default org:",organisation["name"])
                    results = organisation
        else:
            # Some other error occurred.
            print('HTTPError:',response.status_code,response.headers)

             # Most errors return additional information as a json payload
            if 'application/json' in response.headers['Content-Type']:
                print('Error payload:')
                print(json.dumps(response.json(),indent=2))
    return results

org = get_organisations()
print(org)

