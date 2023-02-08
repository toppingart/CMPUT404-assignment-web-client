#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, Elena Xu, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
 

class HTTPClient(object):
    def get_host_port(self,url):

        parseUrl = urllib.parse.urlparse(url)
        
        # if a port is not specified
        if not parseUrl.port:
            port = 80
        else:
            port = parseUrl.port

        getIpAddress = socket.gethostbyname(parseUrl.hostname)
        return (getIpAddress, port) # returns the IP address and the port


    def connect(self, host, port):
        # create socket and connect it to host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
       

    def get_code(self, data):
        headersBody = data.split('\r\n\r\n')

        # get the status code from the first line (e.g. HTTP/1.1 200 OK)
        return int(headersBody[0][9:12])


    def get_headers(self,data):
        # separate the headers from the body (length of list will be 2)
        headersBody = data.split('\r\n\r\n')
        return headersBody[0]

    def get_body(self, data):

        # separate the headers from the body (length of list will be 2)
        headersBody = data.split('\r\n\r\n')
        return headersBody[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        # generic error response (500)
        code = 500
        body = ""

        hostPort = self.get_host_port(url)
        self.connect(hostPort[0], hostPort[1]) # ip address, port

        parseUrl = urllib.parse.urlparse(url)
        path = parseUrl.path
        hostName = parseUrl.hostname
        queryDict = dict(urllib.parse.parse_qsl(parseUrl.query))

        # in case a path is not specified
        if not path:
            path = '/'

        # add the query string to the end of path if there is one: 
      
        # args being a dictionary
        if args:
            body += '?'
            for key,value in args.items():
                body += f'{key}={value}' # key = value
                if key != list(args.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    body += '&'
        
        # in case no arg is provided but the query is found in the url itself
        elif not args and len(queryDict) > 0:
            body += '?'
            for key,value in queryDict.items():
                body += f'{key}={value}'
                if key != list(queryDict.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    body += '&'

        path += body
        # add host and connection 
        requestData = f"GET {path} HTTP/1.1\r\nHost: {hostName}\r\nConnection: close\r\n\r\n"

        self.sendall(requestData)
       
        # listen for response from the server
        response = self.recvall(self.socket)
 
        body = self.get_body(response)
        code = self.get_code(response)

        self.close() # close the socket
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # args being a dictionary
        if args:
           for key,value in args.items():
                body += f'{key}={value}' # key = value
                if key != list(args.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    body += '&' # add & in between 

        hostPort = self.get_host_port(url)
        self.connect(hostPort[0], hostPort[1]) # ip address, port

        parseUrl = urllib.parse.urlparse(url)
        contentType = "application/x-www-form-urlencoded"
        contentLength = len(body)

        # add host, content-type, connection, and body
        requestData = f"POST {parseUrl.path} HTTP/1.1\nHost: {parseUrl.hostname}\nContent-Type: {contentType}\nConnection: close\nContent-length:{contentLength}\r\n\r\n{body}\r\n"

        self.sendall(requestData)

        # listen for response from the server
        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)
        
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
