# Tournament Results Database using PostgreSQL

## Tournament directory (Supports only single tournament):
Instructions to run the code locally:
* Enter `psql` on terminal to start PostgreSQL CLI. (Make sure you are in the `./tournament` directory)
* Enter the following query:
    * `CREATE DATABASE tournament;`
    * `\i tournament.sql` to create required tables
    * and then `\q` to exit CLI.
* Once all the tables are up and running, test some basic queries on these tables in order to make sure that everything is working.
* Now run the test python file using the command `python tournament_test.py`
* You can see all the results for all 10 test cases.


## Tournament_extra directory (Supports multiple tournament):
Instructions to run the code locally:
* Enter `psql` on terminal to start PostgreSQL CLI. (Make sure you are in the `./tournament_extra` directory)
* Enter the following query:
    * `CREATE DATABASE tournament_extra;`
    * `\i tournament_extra.sql` to create required tables
    * and then `\q` to exit CLI.
* Once all the tables are up and running, test some basic queries on these tables in order to make sure that everything is working.
* Now run the test python file using the command `python tournament_extra_test.py`
    * _The_ `tournament_extra_test.py` _file is modified to support the code written in_ `tournament_extra.py` _file. All the table's structures are changed too._
* You can see all the results for all 10 test cases.
