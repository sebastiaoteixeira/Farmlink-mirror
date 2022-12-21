import json
import os

"""
Create database directory 
if it not exists
"""
try:
    os.mkdir("database")
except FileExistsError:
    pass

"""
Get table file path by
table name
"""
def tablePath(table):
    return "database/" + table + ".json"

"""
Verify if a table exists
"""
def tableExists(table):
    try:
        open(tablePath(table), 'r')
        return True
    except FileNotFoundError:
        return False
    
"""
Create a new table
"""
def createTable(table):
    with open(tablePath(table), 'x') as f:
        f.write('{"lastId": 0, "tableRows": []}')
    
    return True
    
"""
Read table json file
and loads json
"""
def readTable(table):
    with open(tablePath(table), 'r') as f:
        data = json.loads(f.read())

    return data

"""
Convert data to json 
and save table json file
"""
def writeTable(table, data):
    with open(tablePath(table), 'w') as f:
        f.write(json.dumps(data))

"""
Add a row to table
"""
def addRow(tableName, row):
    if not tableExists(tableName):
        createTable(tableName)

    table = readTable(tableName)

    lastId = table["lastId"]

    data = table["tableRows"]
    row["id"] = lastId
    data.append(row)
    
    table["lastId"] += 1

    writeTable(tableName, table)

"""
Get tables list
"""
def getTables():
    tables = os.listdir("database")
    for t in tables:
        t = t[:-5]
    return t

"""
Get rows from a table
that satisfies a condition
ex: getRows("login", lambda row: row["id"] == 7)
"""
def getRows(tableName, condition):
    assert tableExists(tableName), "Table not exists"
    
    data = readTable(tableName)["tableRows"]
    result = []
    for row in data:
        if condition(row):
            result.append(row)
    
    return result

"""
Returns True if exists
at least a row with that
satisfies a condition
"""
def rowExists(tableName, condition):
    if not len(getRows(tableName, condition)):
        return False
    return True

"""
Get a row from a table by Id
"""
def getRowById(tableName, Id):
    return getRows(tableName, lambda row: row["id"] == Id)[0]

"""
Get all rows from a table
"""
def getAllRows(tableName):
    return getRows(tableName, lambda row: True)

"""
Delete a row
"""
def removeRow(tableName, row):
    if not tableExists(tableName):
        createTable(tableName)

    table = readTable(tableName)

    lastId = table["lastId"]

    data = table["tableRows"]
    row["id"] = lastId
    data.append(row)
    
    table["lastId"] += 1

    writeTable(tableName, table)


