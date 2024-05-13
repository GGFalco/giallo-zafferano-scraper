import http.client
import json
import ssl

from secrets import API_URL

class SQLWrapper:

    conn: http.client.HTTPSConnection   = None
    host: str                           = API_URL
    data: dict                          = {}
    headers                             = {"Content-type": "application/json", "Accept": "text/plain"}


    def createConnection(self):
        self.conn   = http.client.HTTPSConnection(self.host, context=ssl._create_unverified_context())
        self.createData()

    def createData(self):
        self.data   = {
            "type"      : "",
            "values"    : {},
        }
    
    def setQueryType(self, type):
        self.data["type"] = type
        return self.data["type"]

    def addValue(self, columnName, columnValue):
        self.data["values"][columnName] = columnValue
        return self.data["values"]

    def resetValue(self):
        self.data["values"] = {}
        return self.data["values"]

    def sendRequest(self, request, url = "/ricette.php/insert/ricette_rating"):
        try:
            self.conn.request(request, url, json.dumps(self.data), self.headers)
            self.resetValue()
            response = self.conn.getresponse()
            print(response.read().decode('utf-8'))
        except http.client.HTTPException as e:
            print("Errore di connessione:", e)


    def closeConnection(self):
        self.conn.close()