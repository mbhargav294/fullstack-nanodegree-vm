# Catalog Application

### Introduction
This application is developed on Python using Flask Framework. The backend of this project is based on the PostgreSQL and SQLAlchemy is used to perform CRUD operations to the database. The features included in this application are as follows:

1. __Google Signin__: A Google sign is implemented in the project. Users can directly login with their google accounts to this application.

2. __RESTful Endpoints__: A RESTful endpoint is also implemented in the project. Where developers can directly retrieve data from the application by making simple REST calls to the application. Further information is provided @ `http://localhost:8080/developers`

3. __Search Engine__: A basic search engine is also implemented which will take queries in form of a string and provide any matching Category names or Item names. This is implemented with basic queries: `like`. This will be updated with a vector space model built on each item's name and description too. So, the search will be more intuitive.

***

### Instructions to run the project locally
Since this project is built on vagrant VM, make sure a most recent version of Vagrant and VirtualBox are installed on your Development Machine.

To run vagrant, enter the following two commands at prompt inside the vagrant folder:
1. `vagrant up`
2. `vagrant ssh`
3. `cd /vagrant`
4. `cd /catalog`

#### Database setup
Now after the development machine is setup make sure that the __catalog__ database is present in your PostgreSQL. If not, run these commands:
1. `psql`
2. `create database catalog;`
3. `\q`
4. Verify if the database is created using: `psql catalog`

Now after all these steps are done, first run the `database_setup.py` file using the command `python database_setup.py`

#### Running the web server
After setting up the database, run the `web_server.py` file using `python web_server.py` to start the webserver at `http://localhost:8080/`
