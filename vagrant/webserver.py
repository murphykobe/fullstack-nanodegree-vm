from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Add New Resturant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name="newResturantName" type="text" placeholder = "New Resturant" ><input type="submit" value="Create"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                resturantsPath = self.path.split("/")[2]
                myResturant = session.query(Restaurant).filter_by(id=resturantsPath).one()
                if myResturant !=[]:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"+myResturant.name+"</h1>"
                    output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><input name="updateResturantName" type="text" placeholder = "New Name" ><input type="submit" value="Rename"> </form>''' % str(myResturant.id)
                    output += "</body></html>"
                    self.wfile.write(output)
                    return

            if self.path.endswith("/delete"):
                resturantsPath = self.path.split("/")[2]
                myResturant = session.query(Restaurant).filter_by(id=resturantsPath).one()
                if myResturant !=[]:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure to delete %s ?</h1>" % myResturant.name
                    output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'><input type="submit" value="Delete"> </form>''' % str(myResturant.id)
                    output += "</body></html>"
                    self.wfile.write(output)
                    return

            if self.path.endswith("/restaurants"):
                resturants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output +="<a href=/restaurants/new>New Resturant</a>"
                output +="<br>"
                for r in resturants:
                    output += r.name
                    output +="<br>"
                    output +="<a href=/resturants/%s/edit>Edit</a>" %str(r.id)
                    output +="<br>"
                    output +="<a href=/resturants/%s/delete>Delete</a>" %str(r.id)
                    output +="<br>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newResturantName')
                    newResturant = Restaurant(name=messagecontent[0])
                    session.add(newResturant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location','/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('updateResturantName')
                    resturantsPath = self.path.split('/')[2]
                    myResturant = session.query(Restaurant).filter_by(id=resturantsPath).one()
                    if myResturant != []:
                        myResturant.name = messagecontent[0]
                        session.add(myResturant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location','/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                resturantsPath = self.path.split('/')[2]
                myResturant = session.query(Restaurant).filter_by(id=resturantsPath).one()
                if myResturant != []:
                    session.delete(myResturant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location','/restaurants')
                    self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()