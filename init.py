from http import server
from hashlib import sha3_512
import database
import random
import time
import urllib
#import logging
#logging.getLogger("requests").setLevel(logging.CRITICAL)


def getMillis():
    return int(time.time() * 1000)


hostname = '0.0.0.0'
port = 8080

class MainRequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.count("/get"):
            table = self.path.replace("/get", "")
            if database.tableExists(table) and database.isPublic(table):
                self.send_response(200)
                self.send_header('Content-type', "application/json")
                self.end_headers()
                self.wfile.write(bytes(database.json.dumps(database.getAllRows(table)), 'utf-8'))
            else:
                self.send_error(403, "Requested table is not public")
            return

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
        self.getFields()
        if self.path == "/login":
            self.login()
        elif self.path == "/register":
            self.register()
        elif self.path == "/verifySession":
            self.verifySession()
        elif self.path == "/personalData":
            self.getPersonalData()
        elif self.path == "/addNewProduct":
            self.addNewProduct()
        return

    def getFields(self):
        length = int(self.headers['content-length'])
        field_data = urllib.parse.unquote_plus(self.rfile.read(length).decode("UTF-8"))
        self.fields = {name : (True if value == "on" else (int(value) if value.isdigit() else (float(value) if value.count(".") == 1 and value.replace(".", "").isdigit() else value))) for name, value in (item.split("=") for item in field_data.split("&"))}

    def register(self):
        fields = self.fields
        if not database.tableExists("login") or not database.rowExists("login", lambda row: row["email"] == fields["email"]): 
            loginData = database.addRow("login", {"name": fields["fname"], "email": fields["email"], "password": sha3_512(bytes(fields["password"], 'utf-8')).hexdigest(), "producer": fields.get("producer")})
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
        fields = self.fields
        if database.tableExists("login") and database.rowExists("login", lambda row: row["email"] == fields["email"] and row["password"] == sha3_512(bytes(fields["password"], 'utf-8')).hexdigest()): 
            self.send_response(302)
            self.createSession(database.getRows("login", lambda row: row["email"] == fields["email"] and row["password"] == sha3_512(bytes(fields["password"], 'utf-8')).hexdigest())[0]["id"], fields.get("remember"))
            self.send_header('Location', '/home')
            self.end_headers()
        else:
            self.send_response(400)
            self.send_header('Content-type', "text/plain")
            self.end_headers()
            self.wfile.write(bytes("Email or password invalid", 'utf-8'))
        return
    
    def createSession(self, userId, remember=False):
        milis = getMillis() + 86400000 * (30 if remember else 1) ### Convert micros to millis UNIX-Standard and add 1 or 30 day
        sessionId = hex(random.getrandbits(128))[2:]
        database.addRow("sessions", {"userId": userId, "sessionId": sessionId, "expire": milis})
        self.send_header('set-cookie', "sessionId=" + sessionId + ("; Expires=" + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(milis/1000)) if remember else ""))

    def isSessionValid(self):
        fields = self.fields
        return database.tableExists("sessions") and database.rowExists("sessions", lambda row: row["sessionId"] == fields["sessionId"]) and getMillis() < database.getRows("sessions", lambda row: row["sessionId"] == fields["sessionId"])[0]["expire"]

    def verifySession(self):
        fields = self.fields
        res = "true" if self.isSessionValid() else "false"
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        self.wfile.write(bytes('{"isValid": ' + res + '}', 'utf-8'))
        return

    def getPersonalData(self):
        fields = self.fields
        if self.isSessionValid():
            userId = database.getRows("sessions", lambda row: row["sessionId"] == fields["sessionId"])[0]["userId"]
            personalData = database.getRowById("login", userId)
            personalData["password"] = None
            self.send_response(200)
            self.send_header('Content-type', "application/json")
            self.end_headers()
            self.wfile.write(bytes(database.json.dumps(personalData), 'utf-8'))
        else:
            self.send_error(401, 'Login is needed')
        return

    def isProducer(self, userId):
        if database.tableExists("login") and database.getRowById("login", userId).get("producer"):
            return True
        return False

    def addNewProduct(self):
        if self.isSessionValid():
            fields = self.fields
            userId = database.getRows("sessions", lambda row: row["sessionId"] == fields["sessionId"])[0]["userId"]
            if self.isProducer(userId):
                if not database.tableExists("products"):
                    database.createTable("products", True)
                product = database.addRow("products", {"name": fields.get("name"), "type": fields.get("type"), "price": fields.get("price"), "stock": fields.get("stock"), "img": fields.get("img"), "visible": fields.get("visible"), "producerId": userId})
                self.send_response(200)
                self.send_header('Content-type', "application/json")
                self.end_headers()
                self.wfile.write(bytes(database.json.dumps(product)))
            else:
                self.send_error(403, 'Only producers can add new products')
        else:
             self.send_error(401, 'Login is needed')


mainServer = server.ThreadingHTTPServer((hostname, port), MainRequestHandler)

print("\n\tStarting server at:  ", hostname, ":", port, "\n", sep="")

try:
    mainServer.serve_forever()
except KeyboardInterrupt:
    pass

mainServer.server_close()


