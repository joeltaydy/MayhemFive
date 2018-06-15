#-----------------------------------------------------------------------------#
#---------------------------- Data Access Layer ------------------------------#
#------------------------- For Login Functionality ---------------------------#
#-----------------------------------------------------------------------------#

import os
import sys
import MySQLdb

def getConnection():
    host = "localhost"
    database = "fyp"

    # check if operating system is windows
    if os.name == "nt":
        user = "root"
        password = ""
    else:
        user = "root"
        password = "root"

    # open a database connection
    return MySQLdb.connect (host = host, user = user, passwd = password, db = database)

def closeConnection(connection):
    # disconnect from server
    connection.close()

def getDataFrom(table,connection):
    # prepare a cursor object using cursor() method
    cursor = connection.cursor()

    # Prepare SQL query to INSERT a record into the database
    sqlstmt = "SELECT * FROM " + table

    try:
        # Execute the SQL command
        cursor.execute(sqlstmt)

        # Fetch all the rows in a list of lists
        results = cursor.fetchall()
        return results

    except:
        return "Error: unable to fetch data"
