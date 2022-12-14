from http import server

hostname = 'localhost'
port = 10101

class MainRequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("Request Received: ", self.path)
        path = '/home.html' if self.path == '/' else self.path
        print(path)
        try:
            if path.split(".")[-1] in ["png", "jpg", "webp", "ico"]:
                f = open("interface" + path, 'rb')
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f.read())
                return
            elif path.split(".")[-1] in ["html"]:
                f = open("interface" + path)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(f.read(), "utf-8"))
            elif path.split(".")[-1] in ["css"]:
                f = open("interface" + path)
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(bytes(f.read(), "utf-8"))


        except IOError:
            self.send_error(404, f'File Not Found: {self.path:s}')



mainServer = server.HTTPServer((hostname, port), MainRequestHandler)

print("\n\tStarting server at:  ", hostname, ":", port, "\n", sep="")


try:
    mainServer.serve_forever()
except KeyboardInterrupt:
    pass

mainServer.server_close()


