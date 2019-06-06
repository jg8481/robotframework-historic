import datetime
import sqlite3
from sqlite3 import Error
from robot.libraries.BuiltIn import BuiltIn

class StoreResultsListener:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
        self.PRE_RUNNER = 0
        self.start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        self.date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def start_suite(self, name, attrs):
        self.test_count = len(attrs['tests'])

    def end_test(self, name, attrs):
        if self.test_count != 0:
            self.total_tests += 1
        
        if attrs['status'] == 'PASS':
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def close(self):
        self.end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        self.total_time=(datetime.datetime.strptime(self.end_time,'%H:%M:%S') - datetime.datetime.strptime(self.start_time,'%H:%M:%S'))

        # Connect to db, if db doesn't exist create new one
        self.con = sql_connection()
        sql_table(self.con)

        entities = (str(self.date_now), str(self.total_tests), str(self.passed_tests), str(self.failed_tests))
        sql_insert(self.con, entities)
        sql_fetch(self.con)

'''

# * # * # * # * Re-usable methods out of class * # * # * # * #

''' 

def get_current_date_time(format,trim):
    t = datetime.datetime.now()
    if t.microsecond % 1000 >= 500:  # check if there will be rounding up
        t = t + datetime.timedelta(milliseconds=1)  # manually round up
    if trim:
        return t.strftime(format)[:-3]
    else:
        return t.strftime(format)

def sql_connection():
    try: 
        con = sqlite3.connect('rf_historical_results_db.db')
        return con 
    except Error: 
        print("Unable to connect for DB, please retry after some time")
        #print(Error)

def sql_table(con): 
    cursorObj = con.cursor()
    try:
        cursorObj.execute("CREATE TABLE results(execution_date text, total_tests text, passed_tests text, failed_tests text)") 
        con.commit()
    except Error:
        print("Table exist, moving further")
        #print(Error)

def sql_insert(con, entities):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT INTO results(execution_date, total_tests, passed_tests, failed_tests) VALUES(?, ?, ?, ?)', entities)
    con.commit()

def sql_fetch(con): 
    cursorObj = con.cursor() 
    cursorObj.execute('SELECT * FROM results') 
    rows = cursorObj.fetchall() 
    for row in rows: 
        #print("Execution Date: " + str(row[0]) + "\n\tTotal Tests: " + str(row[1]) + "\n\tPassed Tests: " + str(row[2]) + 
        #"\n\tFailed Tests: " + str(row[3]))
        print(row)