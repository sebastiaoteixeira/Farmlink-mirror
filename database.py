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

def tablePath(table):
    """
    Get table file path by
    table name
    """
    return "database/" + table + ".json"

def tableExists(table):
    """
    Verify if a table exists
    """
    try:
        open(tablePath(table), 'r')
        return True
    except FileNotFoundError:
        return False
    
def createTable(table, public=False):
    """
    Create a new table
    """
    with open(tablePath(table), 'x') as f:
        f.write('{"lastId": 1, "public": ' + ('true' if public else 'false') + ', "tableRows": []}')
    
    return True
    
def readTable(table):
    """
    Read table json file
    and loads json
    """
    with open(tablePath(table), 'r') as f:
        data = json.loads(f.read())

    return data

def writeTable(table, data):
    """
    Convert data to json 
    and save table json file
    """
    with open(tablePath(table), 'w') as f:
        f.write(json.dumps(data))

def addRow(tableName, row):
    """
    Add a row to table
    """
    if not tableExists(tableName):
        createTable(tableName)

    table = readTable(tableName)

    lastId = table["lastId"]

    data = table["tableRows"]
    row["id"] = lastId
    data.append(row)
    
    table["lastId"] += 1

    writeTable(tableName, table)

    return row

def getTables():
    """
    Get tables list
    """
    tables = os.listdir("database")
    for t in tables:
        t = t[:-5]
    return t

def isPublic(tableName):
    assert tableExists(tableName), "Table not exists"
    
    data = readTable(tableName)["public"]
    return data

def getRows(tableName, condition):
    """
    Get rows from a table
    that satisfies a condition
    ex: getRows("login", lambda row: row["id"] == 7)
    """
    assert tableExists(tableName), "Table not exists"
    
    data = readTable(tableName)["tableRows"]
    result = []
    for row in data:
        if condition(row):
            result.append(row)
    
    return result

def rowExists(tableName, condition):
    """
    Returns True if exists
    at least a row with that
    satisfies a condition
    """
    if not len(getRows(tableName, condition)):
        return False
    return True

def getRowById(tableName, Id):
    """
    Get a row from a table by Id
    """
    return getRows(tableName, lambda row: row["id"] == Id)[0]

def getAllRows(tableName):
    """
    Get all rows from a table
    """
    return getRows(tableName, lambda row: True)

def removeRow(tableName, rowId):
    """
    Delete a row
    """
    if not tableExists(tableName):
        createTable(tableName)

    table = readTable(tableName)
    deletedRow = getRowById(tableName, rowId)
    table["tableRows"] = list(filter(lambda row: row["id"] != rowId, table["tableRows"]))
    
    writeTable(tableName, table)
    
    return deletedRow

def editRowElement(tableName, rowId, param, newValue):
    """
    Edit row element
    """
    if tableExists(tableName):
        table = readTable(tableName)
         
        changedRow = {}
        for row in table["tableRows"]:
            if row["id"] == rowId:
                row[param] = newValue
                changedRow = row

        writeTable(tableName, table)
        return changedRow
