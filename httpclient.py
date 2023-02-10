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

'''
External sources used:
(Used to give me an idea on how to approach parsing the query string)

1. ahuigo's implementation, licensed under 
Creative Commons-Attribution-ShareAlike 4.0 (CC-BY-SA 4.0), found on Stack Overflow (https://stackoverflow.com/)
Title of question: Best way to parse a URL query string
Year: 2012
Link to site where implementation was found: https://stackoverflow.com/questions/10113090/best-way-to-parse-a-url-query-string
Link to author (in this case, the person who asked the question): https://stackoverflow.com/users/972376/egoskeptical
Link to author (in this case, the person who answered the question and provided the implementation idea): https://stackoverflow.com/users/2140757/ahuigo
Link to license: https://creativecommons.org/licenses/by-sa/4.0/
'''

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body="", headers=""):
        self.code = code
        self.body = body
        self.headers = headers
    def __str__(self):
        return f'{self.headers}\r\n\r\n{self.body}\r\n'

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
        if len(headersBody) > 0:
            return int(headersBody[0][9:12])


    def get_headers(self,data):
        # separate the headers from the body (length of list will be 2)
        headersBody = data.split('\r\n\r\n')
        if len(headersBody) > 0:
            return headersBody[0]

    def get_body(self, data):

        # separate the headers from the body (length of list will be 2)
        headersBody = data.split('\r\n\r\n')
        if len(headersBody) > 1:
            return headersBody[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        try:
            buffer = bytearray()
            done = False
            while not done:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
            return buffer.decode('utf-8')
        except UnicodeDecodeError:
            # in case of a decode error 
            return buffer.decode('latin-1')

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
        if isinstance(args,dict):
            body += '?'
            for key,value in args.items():
                key = str(key)
                value = str(value)
                # handles any special characters in the query string
                body += f'{urllib.parse.quote(key)}={urllib.parse.quote(value)}' # key = value
                if key != list(args.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    body += '&'
        
        # in case no arg is provided but the query is found in the url itself (working with a string)
        elif not args and len(queryDict) > 0:
            body += '?'
            for key,value in queryDict.items():
                # taking care of special characters
                body += f'{urllib.parse.quote(key)}={urllib.parse.quote(value)}'
                if key != list(queryDict.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    body += '&'

        # in case args is a string
        elif isinstance(args, str):
            body += '?'
            queryArgs = args.split('&')
            for i in range(0, len(queryArgs)):
                if ' ' in queryArgs[i]:
                    queryArgs[i] = queryArgs[i].replace(' ', '+') # replace spaces

                body += queryArgs[i]
                if (i != len(queryArgs) - 1): # if we have not reached the end yet, add &
                    body += '&'

        path += body
       
        # add host and connection 
        requestData = f"GET {path} HTTP/1.1\r\nHost: {hostName}\r\nConnection: close\r\n\r\n"

        self.sendall(requestData)
       
        # listen for response from the server
        response = self.recvall(self.socket)
 
        body = self.get_body(response)
        code = self.get_code(response)
        headers = self.get_headers(response)

        self.close() # close the socket
        return HTTPResponse(code, body, headers)

    def POST(self, url, args=None):
        code = 500
        body = ""

        parseUrl = urllib.parse.urlparse(url)
        path = parseUrl.path
        hostName = parseUrl.hostname
        queryDict = dict(urllib.parse.parse_qsl(parseUrl.query))

        query = ""

        # in case there is a query string at the end of the url
        if len(queryDict) > 0:
            query += '?'
            for key,value in queryDict.items():
                # taking care of special characters
                query += f'{urllib.parse.quote(key)}={urllib.parse.quote(value)}'
                if key != list(queryDict.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    query += '&'

        # args being a dictionary
        if isinstance(args,dict):
           for key,value in args.items():
                key = str(key)
                value = str(value)
                body += f'{urllib.parse.quote(key)}={urllib.parse.quote(value)}' # key = value
                if key != list(args.keys())[-1]: # if we're still not at the last item (i.e. more after this)
                    body += '&' # add & in between 

        # in case args is a string
        elif isinstance(args, str):
            queryArgs = args.split('&')
            for i in range(0, len(queryArgs)):
                if ' ' in queryArgs[i]:
                    queryArgs[i] = queryArgs[i].replace(' ', '+') # replace spaces

                body += queryArgs[i]
                if (i != len(queryArgs) - 1): # if we have not reached the end yet, add &
                    body += '&'

        hostPort = self.get_host_port(url)
        self.connect(hostPort[0], hostPort[1]) # ip address, port

        contentType = "application/x-www-form-urlencoded"
        contentLength = len(body)

        # in case a path is not specified
        if not path:
            path = '/'

        path += query
        # add host, content-type, connection, and body
        requestData = f"POST {path} HTTP/1.1\nHost: {hostName}\nContent-Type: {contentType}\nConnection: close\nContent-length:{contentLength}\r\n\r\n{body}\r\n"

        self.sendall(requestData)

        # listen for response from the server
        response = self.recvall(self.socket)
    
        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
      
        self.close()
        return HTTPResponse(code, body, headers)

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
