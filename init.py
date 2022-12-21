from http import server
from hashlib import sha3_512
import database
import random
import time

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

        if not database.rowExists("login", lambda row: row["email"] == fields["email"]): 
            loginData = database.addRow("login", {"name": fields["fname"], "email": fields["email"], "password": sha3_512(bytes(fields["password"], 'utf-8')).hexdigest()})
            self.send_response(302)
            self.createSession(loginData["id"])
            self.send_header('Location', '/home')
            self.end_headers()
        else:
            self.send_response(400)
            self.send_header('Content-type', "text/plain")
            self.end_headers()
            self.wfile.write(bytes("This Email is already registed", 'utf-8'))
        return  

    def login(self):
        length = int(self.headers['content-length'])
        field_data = self.rfile.read(length).decode("UTF-8")
        fields = {name : value for name, value in (item.split("=") for item in field_data.split("&"))}
        if database.rowExists("login", lambda row: row["email"] == fields["email"] and row["password"] == sha3_512(bytes(fields["password"], 'utf-8')).hexdigest()): 
            self.send_response(302)
            self.createSession(database.getRows("login", lambda row: row["email"] == fields["email"] and row["password"] == sha3_512(bytes(fields["password"], 'utf-8')).hexdigest())[0]["id"])
            self.send_header('Location', '/home')
            self.end_headers()
        else:
            self.send_response(400)
            self.send_header('Content-type', "text/plain")
            self.end_headers()
            self.wfile.write(bytes("Email or password invalid", 'utf-8'))
    
    def createSession(self, userId, remember=False):
        milis = int(time.time() / 1000) + 86400000 * (30 if remember else 1) ### Convert micros to millis UNIX-Standard and add 1 day
        sessionId = hex(random.getrandbits(128))[2:]
        database.addRow("sessions", {"userId": userId, "sessionId": sessionId, "expire": milis})
        self.send_header('set-cookie', "sessionId=" + sessionId)



mainServer = server.HTTPServer((hostname, port), MainRequestHandler)

print("\n\tStarting server at:  ", hostname, ":", port, "\n", sep="")

try:
    mainServer.serve_forever()
except KeyboardInterrupt:
    pass

mainServer.server_close()


