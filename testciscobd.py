#!/usr/bin/env python3
import asyncio
import aiohttp

import environment
import ciscobusinessdashboard


async def main():
    """Run a few commands to test the PyPi library"""

    settings = ciscobusinessdashboard.CiscoBDSettingsClass(
        dashboard=environment.dashboard,
        port=environment.port,
        keyid=environment.keyid,
        secret=environment.secret,
    )
    print("main: settings dash")
    print(settings.dashboard)

    async with aiohttp.ClientSession() as client:
        result = await ciscobusinessdashboard.get_organisation_id(
            client, settings, orgname="Default"
        )

        print("All Information:")

        result = await ciscobusinessdashboard.get_node_interfaces(client, settings)
        print(result)

        #        print("orgid:")
        #        print(result)
        #        result = await ciscobusinessdashboard.get_default_organisation(client, settings)
        #        print("Default Org:")
        #        print(result)
        #        result = await ciscobusinessdashboard.get_organisation(
        #            client, settings, orgname="Jochem"
        #        )
        #        print("Jochem Org:")
        #        print(result)


#       result = await ciscobusinessdashboard.get_nodes_organisation(
#           client,
#           settings,
#           orgname="Default",
#       )
#       print("Nodes from Org Default:")
#       print(result)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
