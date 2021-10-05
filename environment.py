#!/usr/bin/env python3
# Hostname and port
dashboard = "cbd.jochem.me"
port = "443"

# This value is not used by Home Assistant Integration
verify_cbd_cert = True

# Generate an access key from the Administration > Users page of the Cisco
# Business Dashboard GUI. Replace below sample values.
keyid = "615ac54546dbad0607af8416"
secret = "b3PoEaZ1rCK39L8IfZmXGWu9vE1paNwo"

# The appname should be unique to the application.  Recommended format is in
# domain name format
appname = "cbd.jochem.me"

# Provide a string identifier for this application instance.  A UUID is
# recommended.  Set clientid to None to generate a UUID dynamically
clientid = None
