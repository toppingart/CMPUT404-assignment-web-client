#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
        port = 80

        getIpAddress = socket.gethostbyname(parseUrl.hostname)
        return (getIpAddress, port) # returns the IP address and the port


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
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
            #print(part)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        hostPart = self.get_host_port(url)
        self.connect(hostPart[0], hostPart[1]) # ip address, port

        parseUrl = urllib.parse.urlparse(url)
        requestData = f"GET {parseUrl.path} HTTP/1.1\nHost: {parseUrl.hostname}\n\n"

        self.sendall(requestData)

        # listen for response from the server
        response = self.socket.recv(1024)
        self.socket.shutdown(socket.SHUT_WR)
        full = ''
        while (len(response) > 0):
            full += response.decode()
            response = self.socket.recv(1024)


       # a = self.recvall(self.socket)
        print(full)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = "title=test&body=bodytest&userId=1"


        hostPart = self.get_host_port(url)
        self.connect(hostPart[0], hostPart[1]) # ip address, port


        parseUrl = urllib.parse.urlparse(url)
        contentType = "application/x-www-form-urlencoded"
        requestData = f"POST {parseUrl.path} HTTP/1.1\nHost: {parseUrl.hostname}\nContent-Type: {contentType}\r\n\r\n{body}\r\n"

        self.sendall(requestData)

        # listen for response from the server
        response = self.socket.recv(1024)
        self.socket.shutdown(socket.SHUT_WR)
        full = ''
        while (len(response) > 0):
            full += response.decode()
            response = self.socket.recv(1024)
        print(full)
        '''
        POST /test HTTP/1.1
Host: foo.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 27

field1=value1&field2=value2
        '''
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
