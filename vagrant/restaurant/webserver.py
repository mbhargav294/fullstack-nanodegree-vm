from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Restaurant, MenuItem


# Creating Session to connect to our database
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def listRestaurants(self, restaurants):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    output = ""
    output += "<html><body>"
    output += "<h1><a href='/restaurants/new'>Register new Restaurant<a></h1>"
    output += "<h1>List of restaurants</h1>"
    for restaurant in restaurants:
        output += ("%s<br />" % restaurant.name)
        output += ("<a href='restaurants/%s/edit'>Edit</a><br />" % restaurant.id)
        output += ("<a href='restaurants/%s/delete'>Delete</a><br /><br />" % restaurant.id)
    output += "</body></html>"
    self.wfile.write(output)
    print output
    return


def registerRestaurant(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    output = ""
    output += "<html><body>"
    output += "<h1>Register a new Restaurant</h1>"
    output += '''<form method="POST" enctype="multipart/form-data" action="/restaurants/new">'''
    output += "Enter the Restaurant Name:"
    output += '''<input type="text" name="restaurant"><input type="submit" value="Submit">'''
    output += "</form>"
    output += "</body></html>"
    self.wfile.write(output)
    print output
    return


def editRestaurant(self, restaurant):
    if restaurant:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ""
        output += "<html><body>"
        output += "<h1>Edit Restaurant</h1>"
        output += ("<h1>%s</h1>" % restaurant.name)
        output += ('''<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/edit">''' % restaurant.id)
        output += ('''<input type="text" name="restaurant" placeholder="%s"><input type="submit" value="Submit">''' % restaurant.name)
        output += "</form>"
        output += "</body></html>"
        self.wfile.write(output)
        print output
    else:
        self.send_error(404, "File Not Found %s", self.path)
    return


def deleteRestaurant(self, restaurant):
    if restaurant:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ""
        output += "<html><body>"
        output += ("<h1>Are you sure you want to delete: %s</h1>" % restaurant.name)
        output += ('''<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/delete">''' % restaurant.id)
        output += '''<input type="submit" value="Delete">'''
        output += "</form>"
        output += "</body></html>"
        self.wfile.write(output)
        print output
    else:
        self.send_error(404, "File Not Found %s", self.path)
    return


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                if restaurants:
                    listRestaurants(self, restaurants)

            if self.path.endswith("/restaurants/new"):
                registerRestaurant(self)

            if self.path.endswith("/edit"):
                retaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id =
                                    retaurantIDPath).one()
                editRestaurant(self, myRestaurantQuery)

            if self.path.endswith("/delete"):
                retaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id =
                                    retaurantIDPath).one()
                deleteRestaurant(self, myRestaurantQuery)

        except IOError:
            self.send_error(404, "File Not Found %s", self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantname = fields.get('restaurant')

                restaurant = Restaurant(name = "%s"%restaurantname[0])
                session.add(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantname = fields.get('restaurant')

                retaurantIDPath = self.path.split("/")[2]
                myRestaurant = session.query(Restaurant).filter_by(id =
                               retaurantIDPath).one()

                if myRestaurant:
                    myRestaurant.name = restaurantname[0]
                    session.add(myRestaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantname = fields.get('restaurant')

                retaurantIDPath = self.path.split("/")[2]
                myRestaurant = session.query(Restaurant).filter_by(id =
                               retaurantIDPath).one()

                if myRestaurant:
                    session.delete(myRestaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Webserver is running on the port %s..." % port
        server.serve_forever()

    except KeyboardInterrupt: # triggers when user holds Ctrl + C on Keyboard
        print "Got Interrupt ^C: Server Stoped..."
        server.socket.close()


if __name__ == '__main__':
    main()
