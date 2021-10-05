#!/usr/bin/env python3
import environment
import ciscobusinessdashboard


result = ciscobusinessdashboard.get_default_organisation(verify_cbd_cert=environment.verify_cbd_cert, dashboard=environment.dashboard, port=environment.port, keyid=environment.keyid ,secret=environment.secret,clientid=environment.clientid,appname=environment.appname )
print (result)
print("hello")