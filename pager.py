#!/usr/bin/env python
#--coding:utf-8--

import requests
from requests.auth import HTTPBasicAuth
import json
import urllib
import urllib.parse
from urllib.parse import urlparse
import binascii 
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path


curdir = path.dirname(path.realpath(__file__))
sep = '/'

# MIME-TYPE
mimedic = [
                        ('.html', 'text/html'),
                        ('.htm', 'text/html'),
                        ('.js', 'application/javascript'),
                        ('.css', 'text/css'),
                        ('.json', 'application/json'),
                        ('.png', 'image/png'),
                        ('.jpg', 'image/jpeg'),
                        ('.gif', 'image/gif'),
                        ('.txt', 'text/plain'),
                        ('.avi', 'video/x-msvideo'),
                    ]

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET request reply
    def do_GET(self):
        #print(self.headers)
        #print(self.command)
        #print(self.requestline)
        parsed_url = urlparse(self.requestline)
        targetpara=(parsed_url.query.split(' ')[0])
        finalpara=targetpara.split('&')
        if (len(finalpara)>1): #if detected parameter, then do sending process
            callsign=finalpara[0].split('=')[-1] # Get target call sign 
            massage=finalpara[1].split('=')[-1]# Get target message (chinese char in url encoded format"%D2%D1 etc")
            sender=finalpara[2].split('=')[-1]# Get sender call sign 
            passwd=finalpara[3].split('=')[-1]# Get sender password
            asciimassage=massage.strip('%').split('%') # remove "%" just leave ASCII hex 
            massagelen=len(asciimassage)# calculate lenth of chinese char lenth
            #print (asciimassage) # print it for debug
            sendmassage=[] # make a blank massage list
            if (massagelen>1):
                for i in range(massagelen):
                    Bchari=bytes.fromhex(asciimassage[i]) # trasnfer ASCII hex to 1 byte HEX code
                    Ichari=int.from_bytes(Bchari, byteorder='big', signed=False)-128 # transfer GB2312 code to Pager Chinese code, "-128" means sub 0x80 in data byte.
                    sendmassage.append(chr(Ichari))  # transfer final code to finalmassage list
                    finalmassage=''.join(sendmassage) # transfer list format to string format
                    
            #print (callsign+',')# print it for debug
            callsignlist= callsign.split(",") # transfer target callsign to list format.
            
            #print (callsignlist) # Debug perpose
            #print(finalmassage)# Debug perpose
            #print (sender)# Debug perpose
            #print (passwd)# Debug perpose
            
            print(send(finalmassage, callsignlist, sender, passwd, 'http://hampager.de/api/calls','b-all')) # call send function to POST sending API and print send reply for resault debug

        # if no parameter, reply index page.
        sendReply = False
        querypath = urlparse(self.path)
        filepath, query = querypath.path, querypath.query
        if filepath.endswith('/'):
            filepath += 'index.html'
        filename, fileext = path.splitext(filepath)
        for e in mimedic:
            if e[0] == fileext:
                mimetype = e[1]
                sendReply = True

        if sendReply == True:
            try:
                with open(path.realpath(curdir + sep + filepath),'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type',mimetype)
                    self.end_headers()
                    self.wfile.write(content)
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)

def run():
    port = 8001  #  change service port here.
    print('starting server, port', port)
    # Server settings
    server_address = ('', port) # change server IP address here
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

# under this line , it is oringnal Dapnet send function. Thanks DL7FL and all dapnet group
def send(text, callsign, login, passwd, url,txgroup): # mit json modul machen
	""" Sendet JASON-String zur Funkruf senden."""

	json_string =json.dumps({"text": text, "callSignNames": callsign, "transmitterGroupNames": [txgroup], "emergency": False})
	#import pprint; pprint.pprint(json_string) # rem for debug perpose
	response = requests.post(url, data=json_string, auth=HTTPBasicAuth(login, passwd)) # Exception handling einbauen
	return response

if __name__ == '__main__':
    run()
