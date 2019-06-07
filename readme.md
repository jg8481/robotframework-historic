# Robotframework - Historical

Aim of the project is to store execution results in local database and create html report based on historical data

Sample Report: [link](https://robotframework-historic.netlify.com/)

## How it works

 - Capture execution results using robotframework listener
     - Executed On
     - Total tests
     - Passed tests
     - Failed test
     - Duration

 - Store captured results into sqlite3 database (inbuilt in python)

 - Generate html report based on available data in database

## How to use

 - Copy `StoreResultsListener.py` to project

 - Execute test's using above listener
   > robot --listener StoreResultsListener.py test.robot
 
 - After completion of execution `historical_results_do_not_delete.db` will be created in root folder
   > Don't delete this file, for every execution test results are store here

 - Fetch results from `historical_results_do_not_delete.db` and generate html report based on results

### Current status

 - This idea is still in draft (ideas and contribution are much appreciated)

> Inspired from [robotframework/dbbot](https://github.com/robotframework/DbBot)
