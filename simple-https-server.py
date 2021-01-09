#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Alex Dergachev
# SPDX-FileCopyrightText: 2016 Jonathon Reinhart

# Source: https://gist.github.com/JonathonReinhart/f26365364918b44d82bbd6b90269fbd6

import BaseHTTPServer
import SimpleHTTPServer
import ssl
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--certfile')
ap.add_argument('--keyfile')
ap.add_argument('--port', type=int, default=443)
ap.add_argument('--hostname', default='localhost')
args = ap.parse_args()

url = 'https://' + args.hostname
if args.port != 443:
    url += ':' + str(args.port)
url += '/'

httpd = BaseHTTPServer.HTTPServer((args.hostname, args.port), SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile=args.certfile, keyfile=args.keyfile, server_side=True)

print('Serving at {}'.format(url))
httpd.serve_forever()
