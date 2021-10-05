#!/usr/bin/env python3
import asyncio
import aiohttp

import ciscobusinessdashboard
import environment


async def main():
    """Simple function to test the output."""
    async with aiohttp.ClientSession() as client:
        result = await ciscobusinessdashboard.get_default_organisation(
            client,
            dashboard=environment.dashboard,
            port=environment.port,
            keyid=environment.keyid,
            secret=environment.secret,
            clientid=environment.clientid,
            appname=environment.appname,
        )

        print(result)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
