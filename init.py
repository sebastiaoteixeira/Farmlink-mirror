from http import server
from hashlib import sha3_512
import database

hostname = '0.0.0.0'
port = 8080

class MainRequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("Request Received: ", self.path)
        path = '/home.html' if self.path == '/' else self.path
        if path.count('.') == 0:
            path += '.html'
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

    def do_POST(self):
        if self.path == "/login":
            self.login()
        elif self.path == "/register":
            self.register()

    def register(self):
        length = int(self.headers['content-length'])
        field_data = self.rfile.read(length).decode("UTF-8")
        fields = {name : value for name, value in (item.split("=") for item in field_data.split("&"))}

        database.addRow("login", {"name": fields["fname"], "email": fields["email"], "password": sha3_512(bytes(fields["password"], 'utf-8')).hexdigest()})


    def login(self):
        pass


mainServer = server.HTTPServer((hostname, port), MainRequestHandler)

print("\n\tStarting server at:  ", hostname, ":", port, "\n", sep="")


try:
    mainServer.serve_forever()
except KeyboardInterrupt:
    pass

mainServer.server_close()


