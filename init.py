from http import server
from hashlib import sha3_512
import database
import random
import time
import urllib
import sys
import os
#import logging
#logging.getLogger("requests").setLevel(logging.CRITICAL)


def getMillis():
    return int(time.time() * 1000)

hostname = '0.0.0.0'
port = 8080
if len(sys.argv) > 1:
     if sys.argv[1] == '--production':
        hostname = ''
        port = int(os.environ.get('PORT', '8000'))

class MainRequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.getFields()
        path = self.path.split('?')[0]
        if self.path.count("/get/"):
            table = self.path.split("/")[2].split("?")[0]
            if database.tableExists(table):
                if database.isPublic(table):
                    self.send_response(200)
                    self.send_header('Content-type', "application/json")
                    self.end_headers()
                    if not self.path.count("?"):
                        self.wfile.write(bytes(database.json.dumps(database.getAllRows(table)), 'utf-8'))
                    else:
                        def conditions(row):
                            for key in self.fields.keys():
                                if row.get(key):
                                    if self.fields[key] != row[key]:
                                        return False

                            if self.fields.get("q"):
                                for key in row.keys():
                                    if row[key].lower().count(self.fields["q"].lower()):
                                        return True
                                return False
                            return True
                        self.wfile.write(bytes(database.json.dumps(database.getRows(table, conditions)), 'utf-8'))
                else:
                    self.send_error(403, "Requested table is not public")
            else:
                self.send_error(404, "Requested table not exists")
            return

        path = '/home.html' if path == '/' else path
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
        self.getFields(post=True)
        self.getCookies()
        if self.path == "/login":
            self.login()
        elif self.path == "/register":
            self.register()
        elif self.path == "/registerProducer":
            producerId = self.registerProducer()
            self.register(producerId)
        elif self.path == "/verifySession":
            self.verifySession()
        elif self.path == "/personalData":
            self.getPersonalData()
        elif self.path == "/addNewProduct":
            self.addNewProduct()
        elif self.path == "/editProducer":
            self.editProducer()
        elif self.path == "/editProduct":
            self.editProduct()
        elif self.path == "/removeProduct":
            self.removeProduct()
        elif self.path == "/createOrder":
            self.createOrder()
        elif self.path == "/payOrder": 
            self.payOrder()
        elif self.path == "/acceptOrder":
            self.acceptOrder()
        elif self.path == "/rejectOrder":
            self.rejectOrder()
        elif self.path == "/orderPrepared":
            self.markOrderAsPrepared()
        else:
            self.send_error(404, 'Action Not Available: {}'.format(self.path))
        return

    def getFields(self, post=False):
        if post:
            length = int(self.headers['content-length'])
            if length > 0:
                field_data = self.rfile.read(length).decode("UTF-8")
            else:
                field_data = "_=null"
        else:
            if self.path.count("?"):
                field_data = self.path.split("?")[1]
            else:
                field_data = "_=null"
        field_data = urllib.parse.unquote_plus(field_data)
        self.fields = {name : (True if value == "on" or value == "true" else (int(value) if value.isdigit() else (int(value) if len(value) > 1 and value[0] == "-" and value[1:].isdigit() else (float(value) if value.count(".") == 1 and value.replace(".", "").isdigit() else (float(value) if len(value) > 1 and value.count(".") == 1 and value[0] == "-" and value.replace(".", "")[1:].isdigit() else value))))) for name, value in (item.split("=") for item in field_data.split("&"))}

    def getCookies(self):
        cookie_data = self.headers['Cookie']
        if cookie_data is not None:
            self.cookies = {name : (True if value == "on" else (int(value) if value.isdigit() else (float(value) if value.count(".") == 1 and value.replace(".", "").isdigit() else value))) for name, value in (item.split("=") for item in cookie_data.split("; "))}
        else:
            self.cookies = {}

    def register(self, producerId = None):
        if not database.tableExists("login") or not database.rowExists("login", lambda row: row["email"] == self.fields["email"]): 
            loginData = database.addRow("login", {"name": self.fields["fname"], "email": self.fields["email"], "password": sha3_512(bytes(self.fields["password"], 'utf-8')).hexdigest(), "producer": self.fields.get("producer"), "producerId": producerId})
            self.send_response(302)
            self.createSession(loginData["id"])
            location = '/producer' if self.fields.get("producer") else '/home'
            self.send_header('Location', location)
            self.end_headers()
        else:
            self.send_error(400, "This Email is already registed")
        return loginData["id"]

    def registerProducer(self):
        if not database.tableExists("producer"):
            database.createTable("producer", True)
        producerData = database.addRow("producer", {"name": self.fields.get("fname"), "email": self.fields.get("email"), "phone": self.fields.get("contact-phone"), "website": self.fields.get("website"), "description": self.fields.get("description"), "photo": self.fields.get("photo")})
        return producerData["id"]

    

    def login(self):
        if database.tableExists("login") and database.rowExists("login", lambda row: row["email"] == self.fields["email"] and row["password"] == sha3_512(bytes(self.fields["password"], 'utf-8')).hexdigest()): 
            self.send_response(302)
            self.createSession(database.getRows("login", lambda row: row["email"] == self.fields["email"] and row["password"] == sha3_512(bytes(self.fields["password"], 'utf-8')).hexdigest())[0]["id"], self.fields.get("remember"))
            self.send_header('Location', '/home')
            self.end_headers()
        else:
            self.send_error(400, "Email or password invalid")
        return
    
    def createSession(self, userId, remember=False):
        milis = getMillis() + 86400000 * (30 if remember else 1) ### Convert micros to millis UNIX-Standard and add 1 or 30 day
        sessionId = hex(random.getrandbits(128))[2:]
        database.addRow("sessions", {"userId": userId, "sessionId": sessionId, "expire": milis})
        self.send_header('set-cookie', "sessionId=" + sessionId + ("; Expires=" + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(milis/1000)) if remember else ""))

    def onlyLogged(func):
        def inner(self):
            if self.isSessionValid():
                return func(self)
            else:
                self.send_error(401, 'Login is needed')
        return inner

    def onlyProducer(func):
        def inner(self):
            if self.isSessionValid():
                userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
                if self.isProducer(userId):
                    return func(self)
                else:
                    self.send_error(403, 'Only producers can access this function')
            else:
                self.send_error(401, 'Login is needed')
        return inner
                

    def isSessionValid(self):
        return database.tableExists("sessions") and database.rowExists("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"]) and getMillis() < database.getRows("sessions", lambda row: row["sessionId"] == self.cookies.get("sessionId"))[0]["expire"]

    def verifySession(self):
        res = "true" if self.isSessionValid() else "false"
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        self.wfile.write(bytes('{"isValid": ' + res + '}', 'utf-8'))
        return

    @onlyLogged
    def getPersonalData(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        personalData = database.getRowById("login", userId)
        personalData["password"] = None
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        self.wfile.write(bytes(database.json.dumps(personalData), 'utf-8'))

    def isProducer(self, userId):
        if database.tableExists("login") and database.getRowById("login", userId).get("producer"):
            return True
        return False

    @onlyProducer
    def addNewProduct(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        producerId = database.getRowById("login", userId)["producerId"]
        if not database.tableExists("products"):
            database.createTable("products", True)
        product = database.addRow("products", {"name": self.fields.get("name"), "type": self.fields.get("type"), "price": self.fields.get("price"), "stock": self.fields.get("stock"), "description": self.fields.get("description"), "img": self.fields.get("img"), "visible": self.fields.get("visible"), "producerId": producerId})
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        self.wfile.write(bytes(database.json.dumps(product), 'utf-8'))

    @onlyProducer
    def editProduct(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        producerId = database.getRowById("login", userId)["producerId"]
        if not database.tableExists("products"):
            database.createTable("products", True)
        if database.rowExists("products", lambda row: row["id"] == self.fields["productId"]):
            producerIdOfProduct = database.getRowById("products", self.fields["productId"])["producerId"]
            if producerId != producerIdOfProduct:
                self.send_error(403, "You have not permission to edit this product")
                return

            productId = self.fields["productId"]

            if self.fields.get("name"):
                database.editRowElement("products", productId, "name", self.fields["name"])
            elif self.fields.get("type"):
                database.editRowElement("products", productId, "type", self.fields["type"])
            elif self.fields.get("price"):
                database.editRowElement("products", productId, "price", self.fields["price"])
            elif self.fields.get("stock"):
                database.editRowElement("products", productId, "stock", self.fields["stock"])
            elif self.fields.get("description"):
                database.editRowElement("products", productId, "description", self.fields["description"])
            elif self.fields.get("img"):
                database.editRowElement("products", productId, "img", self.fields["img"])
            elif self.fields.get("visible"):
                database.editRowElement("products", productId, "visible", self.fields["visible"])
            
            self.send_response_only(201)
            self.end_headers()
            return

    @onlyProducer
    def removeProduct(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        producerId = database.getRowById("login", userId)["producerId"]
        if not database.tableExists("products"):
            self.send_error(404, "Products table not exists")
        if database.rowExists("products", lambda row: row["id"] == self.fields["productId"]):
            producerIdOfProduct = database.getRowById("products", self.fields["productId"])["producerId"]
            if producerId != producerIdOfProduct:
                self.send_error(403, "You have not permission to edit this product")
                return

            productId = self.fields["productId"]
            database.editRowElement("products", productId, "visible", False)
            self.send_response_only(201)
            self.end_headers()
            return
        

    @onlyProducer
    def editProducer(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        if not database.tableExists("producer"):
            database.createTable("producer", True)
        if database.rowExists("login", lambda row: row["id"] == userId):
            producerId = database.getRowById("login", userId)["producerId"]
            print("Producer Id:", producerId)

            if self.fields.get("fname"):
                database.editRowElement("producer", producerId, "name", self.fields["fname"])
            elif self.fields.get("email"):
                database.editRowElement("producer", producerId, "email", self.fields["email"])
            elif self.fields.get("contact-phone"):
                database.editRowElement("producer", producerId, "phone", self.fields["contact-phone"])
            elif self.fields.get("description"):
                database.editRowElement("producer", producerId, "description", self.fields["description"])
            elif self.fields.get("photo"):
                database.editRowElement("producer", producerId, "photo", self.fields["photo"])
            elif self.fields.get("website"):
                database.editRowElement("producer", producerId, "website", self.fields["website"])

            self.send_response(201)
            self.end_headers()
            return

    """
    Order Status:
        -3: invalidated
        -2: canceled
        -1: rejected
        
        0: delivered

        2: validated
        3: pendent
        4: accepted
        5: prepared
        6: picked up
        7: returned
    """

    @onlyLogged
    def createOrder(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        if not database.tableExists("products"):
            self.send_error(404, "Products table not exists")
        if database.rowExists("products", lambda row: row["id"] == self.fields["productId"]):
            productData = database.getRowById("products", self.fields["productId"])
            if productData["stock"] != 0:
                if productData["stock"] > 0:
                    database.editRowElement("products", productData["id"], "stock", productData["stock"] - 1)
                order = database.addRow("orders", {"userId": userId, "productId": self.fields["productId"], "qty": self.fields["qty"], "nif": self.fields["nif"], "street": self.fields["street"], "zip": self.fields["zip"], "number": self.fields["number"], "district": self.fields["district"], "location": self.fields["location"], "status": 2})
                self.send_response(200)
                self.send_header('Content-type', "application/json")
                self.end_headers()
                self.wfile.write(bytes(database.json.dumps(order), 'utf-8'))
            else:
                order = database.addRow("orders", {"userId": userId, "productId": self.fields["productId"], "qty": self.fields["qty"], "nif": self.fields["nif"], "street": self.fields["street"], "zip": self.fields["zip"], "number": self.fields["number"], "district": self.fields["district"], "location": self.fields["location"], "status": -3})
                self.send_error(400, "Request product isn't available")
            return order
        else:
            self.send_error(400, "Requested product doesn't exists")
        return

    @onlyLogged
    def payOrder(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        if not database.tableExists("orders"):
            self.send_error(404, "Orders table not exists")
        if database.rowExists("orders", lambda row: row["id"] == self.fields["orderId"]):
            order = database.getRowById("orders", self.fields["orderId"])
            if order["status"] == 2:
                database.editRowElement("orders", order["id"], "status", 3)
                self.send_response_only(201)
                self.end_headers()
            else:
                self.send_error(400, "Requested order's status is not validated")
        else:
            self.send_error(400, "Requested order doesn't exists")
        return
    
    @onlyProducer
    def acceptOrder(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        producerId = database.getRowById("login", userId)["producerId"]
        if not database.tableExists("orders"):
            self.send_error(404, "Orders table not exists")
        if database.rowExists("orders", lambda row: row["id"] == self.fields["orderId"]):
            order = database.getRowById("orders", self.fields["orderId"])
            product = database.getRowById("products", order["productId"])
            if product["producerId"] != producerId:
                self.send_error(403, "You have not access to this order")
                return
            if order["status"] == 3:
                database.editRowElement("orders", order["id"], "status", 4)
                self.send_response_only(201)
                self.end_headers()
            else:
                self.send_error(400, "Requested order's status is not validated")
        else:
            self.send_error(400, "Requested order doesn't exists")
        return

    @onlyProducer
    def rejectOrder(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        producerId = database.getRowById("login", userId)["producerId"]
        if not database.tableExists("orders"):
            self.send_error(404, "Orders table not exists")
        if database.rowExists("orders", lambda row: row["id"] == self.fields["orderId"]):
            order = database.getRowById("orders", self.fields["orderId"])
            product = database.getRowById("products", order["productId"])
            if product["producerId"] != producerId:
                self.send_error(403, "You have not access to this order")
                return
            if order["status"] == 3:
                database.editRowElement("orders", order["id"], "status", -1)
                self.send_response_only(201)
                self.end_headers()
            else:
                self.send_error(400, "Requested order's status is not validated")
        else:
            self.send_error(400, "Requested order doesn't exists")
        return

    @onlyProducer
    def markOrderAsPrepared(self):
        userId = database.getRows("sessions", lambda row: row["sessionId"] == self.cookies["sessionId"])[0]["userId"]
        producerId = database.getRowById("login", userId)["producerId"]
        if not database.tableExists("orders"):
            self.send_error(404, "Orders table not exists")
        if database.rowExists("orders", lambda row: row["id"] == self.fields["orderId"]):
            order = database.getRowById("orders", self.fields["orderId"])
            product = database.getRowById("products", order["productId"])
            if product["producerId"] != producerId:
                self.send_error(403, "You have not access to this order")
                return
            if order["status"] == 4:
                database.editRowElement("orders", order["id"], "status", 5)
                self.send_response_only(201)
                self.end_headers()
            else:
                self.send_error(400, "Requested order's status is not validated")
        else:
            self.send_error(400, "Requested order doesn't exists")
        return

        

        
mainServer = server.ThreadingHTTPServer((hostname, port), MainRequestHandler)

print("\n\tStarting server at:  ", hostname, ":", port, "\n", sep="")

try:
    mainServer.serve_forever()
except KeyboardInterrupt:
    pass

mainServer.server_close()


