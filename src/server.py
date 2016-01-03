# Example value of "self" in "do_GET(self):"
# requestline: GET /?data=sdf HTTP/1.1
# wfile: <socket._fileobject object at 0x101e49650>
# request: <socket._socketobject object at 0x1037917c0>
# raw_requestline: GET /?data=sdf HTTP/1.1
# 
# server: <SocketServer.TCPServer instance at 0x10493e518>
# headers: Host: localhost:8000
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
# Cookie: G_ENABLED_IDPS=google; _ga=GA1.1.1738252731.1446445775; wp-settings-1=mfold%3Do%26hidetb%3D1%26libraryContent%3Dbrowse%26align%3Dnone%26imgsize%3Dlarge%26editor%3Dtinymce%26advImgDetails%3Dshow%26wplink%3D1%26urlbutton%3Dcustom; wp-settings-time-1=1446446165
# User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9
# Accept-Language: en-us
# Accept-Encoding: gzip, deflate
# Connection: keep-alive
# 
# connection: <socket._socketobject object at 0x1037917c0>
# command: GET
# rfile: <socket._fileobject object at 0x101e496d0>
# path: /?data=value
# request_version: HTTP/1.1
# client_address: ('127.0.0.1', 64895)
# close_connection: 1
import SimpleHTTPServer
import socket
import SocketServer
from urlparse import urlparse, parse_qs
from wifistat import WiFiStat
import json

class WiFiStatRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        wifi = WiFiStat()
        #wifi.print_verbose('\n'.join("%s: %s" % item for item in vars(self).items())) not really necessary...
        params = parse_qs(urlparse(self.path).query)
        results = []
        for key, values in params.iteritems():
            for value in values:
                result = wifi.run_command(self, key, value)
                if not result is None:
                    results.append(result)
        if results:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(str(results)))
            self.end_headers()
            self.wfile.write(json.dumps(results))
        else:
            if self.path == '/':
                self.path = 'src/web/main.html'
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
    
class WiFiStatTCPServer(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

