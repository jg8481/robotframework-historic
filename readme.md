# Robotframework - Historical

Aim of the project is to store execution results in local database and create html report based on historical data

## How it works

 - Capture execution results using robotframework listener
     - Date of execution
     - Total tests
     - Passed tests
     - Failed test

 - Store captured results into sqlite3 database (inbuilt in python)

 - Generate html report based on available data in database

### Current status

 - This idea is still in draft (ideas and contribution is much appreciated)

> Inspired from [robotframework/dbbot](https://github.com/robotframework/DbBot)