from http import server

hostname = '0.0.0.0'
port = 8080

class MainRequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("Request Received: ", self.path)
        path = '/home.html' if self.path == '/' else self.path
        try:
            with open("interface" + path, 'rb') as f:
                self.send_response(200)
                if path.split('.')[-1] in ['html', 'css']:
                    self.send_header('Content-type', "text/" + path.split('.')[-1])
                elif path.split('.')[-1] in ['png', 'jpeg']:
                    self.send_header('Content-type', "image/" + path.split('.')[-1])
                elif path.split('.')[-1] in ['jpg']:
                    self.send_header('Content-type', "image/jpeg")
                self.end_headers()
                self.wfile.write(f.read())
            return


        except IOError:
            self.send_error(404, 'File Not Found: {}'.format(self.path))



mainServer = server.HTTPServer((hostname, port), MainRequestHandler)

print("\n\tStarting server at:  ", hostname, ":", port, "\n", sep="")


try:
    mainServer.serve_forever()
except KeyboardInterrupt:
    pass

mainServer.server_close()


