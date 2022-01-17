import flask
import re   # for checking emails
import datetime
from datetime import date
import sqlite3
from sqlite3 import Error


import smtplib, ssl #for sending emails
import airbnb
import pandas as pd



#creating connection to the database
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        return sqlite3.connect(db_file)
        
    except Error as e:
        print(e)

database = r"/Users/tomasfencl/Desktop/JEM207_project_Rezabek_Fencl/maindb.db"


#-------------------------------------------------------------------------------------------

# functions for testing input, in the next step they would be replaced by js

#getting id from airbnb.com/.... link
def getID(link):
    try:
        ID = link.split("?")[0].split("/")[-1]

        return(ID)
    except:
            return "0"

#checks if email is in correct format
def checkmail(email):   
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):   
        return 1   
    else:   
        return 0 




#testing input date
def isdatedate(inputDate):
        try:
                year, month, dayQ = inputDate.split('-')
                isValidDate = True
                datetime.datetime(int(year), int(month), int(dayQ))
        except ValueError:
                isValidDate = False
        if(isValidDate):
                return 1
        else:
                return 0

def checkaftertoday(self):
        today = str(date.today())

        if (self > today):
                return 1
        else:
                return 0
def checkinbeforeout(checkin, checkout):
    if (checkin < checkout):
        return 1
    else:
        return 0


#-------------------------------------------------------------------------------------------

# functions and definitions backend

#function to send emails
def sendemailto(receiver_email,message):
    port = 465  # For SSL
    password = "Penthouse123" #input("Type your password and press enter: ")
    context = ssl.create_default_context()
    sender_email = "aparmannadrevne@gmail.com"
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


#function to find out difference between two dates
def days_between (d1, d2):
	d1 = datetime.datetime.strptime(d1,"%Y-%m-%d")
	d2 = datetime.datetime.strptime(d2,"%Y-%m-%d")
	return abs ((d2 - d1).days)

#this function gets the availability and price for specified dates.
def getpriceandavailability(accom_id, chi, cho):
    api = airbnb.Api()
    my_cal = api.get_calendar(accom_id)
    # l = [{}for month in my_cal["calendar_months"] for day in month["days"]] - list comprehension (můžu za to dát ronou pomocí konstru
    # dáte to pomocí try e aby to bylo odolné proti změnám...
    to_DF = []
    for month in my_cal["calendar_months"]:
        for day in month["days"]:
            to_DF.append({"date": (day["date"]),
                          "available": (day["available"]),
                          "available_for_checkin": (day["available_for_checkin"]),
                          'min_nights': (day["min_nights"]),
                          'max_nights': (day["max_nights"]),
                          "local_adjusted_price": (day["price"]["local_adjusted_price"]),
                          "local_currency": (day["price"]["local_currency"]),
                          "local_price": (day["price"]["local_price"]),
                          "native_adjusted_price": (day["price"]["native_adjusted_price"]),
                          "native_currency": (day["price"]["native_currency"]),
                          "native_price": (day["price"]["native_price"]),
                          "type": (day["price"]["type"]),
                          "local_price_formatted": (day["price"]["local_price_formatted"]),

                          })

    df = pd.DataFrame(to_DF).drop_duplicates()
    after_start_date = df["date"] >= chi
    before_end_date = df["date"] < cho
    between_two_dates = after_start_date & before_end_date
    filtered_dates = df.loc[between_two_dates]

    Available = "yes"
    if not (int(filtered_dates[0:1]["min_nights"]) < days_between(chi, cho)):
        Available = "too short stay"
    if not (int(filtered_dates[0:1]["max_nights"]) > days_between(chi, cho)):
        Available = "too long stay"
    if not ((filtered_dates[0:1]["available_for_checkin"]).bool == True):
        Available = "date not possible for checkin"

    available_each_day = True
    for x in filtered_dates["available"]:
        if x == False:
            available_each_day = False
    if not (available_each_day == True):
        Available = "some days are not available"

    total_price = 0
    for x in filtered_dates["local_adjusted_price"]:
        total_price = total_price + x
    return (total_price, Available)






#-------------------------------------------------------------------------------------------
#  The code



app = flask.Flask(__name__)

@app.route("/")
def home():
	return flask.render_template("index.html")



@app.route("/form",methods=["POST","GET"]) #at /form user can inputs his details
def login():
        if flask.request.method == "POST":
                user = flask.request.form 
                error_message = ""
                if checkmail(user["email"]) == 0:
                        error_message = error_message + "invalid email address"
                if isdatedate(user["chi"]) == 0:
                        error_message = error_message + ", invalid ch/i date"
                if isdatedate(user["cho"]) == 0:
                        error_message = error_message + ", invalid ch/O date"
                        
                if checkaftertoday(user["chi"]) == 0:
                        error_message = error_message + ", the checkin date has to be after today"
                        
                if checkinbeforeout(user["chi"],user["cho"]) == 0:
                        error_message = error_message + ", ch/i is after ch/o"




                if error_message != "":
                        return flask.render_template("login.html",promena = error_message)

                
#redirectnout na odchodovou stránku a vstupy zapsat do DB
                name = user["name"]
                email = user["email"]
                chi =user["chi"]
                cho = user["cho"]
                #vložit do for loopu - na víc listingů si najít jinja template - není nutné (nebo pomocí JS)
                listingid_1 = getID(user["listing_1"])
                listingid_2 = getID(user["listing_2"])
                listingid_3 = getID(user["listing_3"])
                listingid_4 = getID(user["listing_4"])
                listingid_5 = getID(user["listing_5"])
                none = 0

                sql1 = f"INSERT INTO indatatable VALUES('{name}', '{email}','{chi}', '{cho}','{listingid_1}')"
                sql2 = f"INSERT INTO indatatable VALUES('{name}', '{email}','{chi}', '{cho}','{listingid_2}')"
                sql3 = f"INSERT INTO indatatable VALUES('{name}', '{email}','{chi}', '{cho}','{listingid_3}')"
                sql4 = f"INSERT INTO indatatable VALUES('{name}', '{email}','{chi}', '{cho}','{listingid_4}')"
                sql5 = f"INSERT INTO indatatable VALUES('{name}', '{email}','{chi}', '{cho}','{listingid_5}')"

                #dát rovnou do c.execute
                
                text = f"{name},{email},{chi},{cho},{listingid_1},{listingid_2},{listingid_3},{listingid_4},{listingid_5}" 

                conn = create_connection(database)

                c = conn.cursor()



                c.execute(sql1)
                c.execute(sql2)
                c.execute(sql3)
                c.execute(sql4)
                c.execute(sql5)               
                conn.commit()
                conn.close()
                return flask.redirect(flask.url_for("user", usr=text))
        else:
                return flask.render_template("login.html")
@app.route("/update_availability") #when loading /update_availability the program will update the database with outputs
def update_availability():

        conn = create_connection(database)
        c = conn.cursor()

        c.execute("SELECT rowid, * FROM indatatable")
        ids = c.fetchall()
        conn.commit()
        conn.close()
        print(ids[0])

        conn = create_connection(database)
        c = conn.cursor()
        today = date.today()
        currday = today.strftime("%Y-%m-%d")

        for item in ids:
            idecko = item[0]
            pric, av = getpriceandavailability(item[5], item[3], item[4])
            sql = f'''INSERT INTO outdatatable VALUES('{idecko}','{currday}', {pric}, '{av}')'''
            c.execute(sql)

        conn.commit()
        conn.close()
        return("<p>updated</p>")

@app.route("/sendmails") #when user or chronos load this, the program will send to the users informations about todays prices of its listing
def sendmails():
        today = datetime.datetime.today()
        currday = today.strftime("%Y-%m-%d")
        conn = create_connection(database)
        c = conn.cursor()

        c.execute("SELECT mail FROM indatatable")
        emails = c.fetchall()
        conn.commit()
        conn.close()
        emails = list(set(emails))
        emails

        for email in emails:
            conn = create_connection(database)
            c = conn.cursor()
            SQLquery = f"SELECT indatatable.name, indatatable.mail, indatatable.chi, indatatable.cho, indatatable.id, outdatatable.date, outdatatable.price, outdatatable.available FROM outdatatable INNER JOIN indatatable ON outdatatable.ext_id=indatatable.rowid WHERE mail = '{email[0]}'AND outdatatable.date = '{currday}'"

            c.execute(SQLquery)
            display = c.fetchall()
            x = (display)
            mailbody = """
            Subject: Accommodation WatchDog
        
            """
            for i in x:
                mailbody = mailbody + " the listing is " + str(i[4]) + " and the price of it is " + str(
                    i[6]) + " and the availability status is: " + str(i[7]) + "\n"
            sendemailto(email, mailbody)
            conn.commit()
            conn.close()
        return "sent"



@app.route("/<usr>") # this is just for fun when I load anything different than above specified
def user(usr):
        return f"<h1>{usr}</h1>"



app.run(debug = 1)
