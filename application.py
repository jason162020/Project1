import os

from flask import Flask, session,render_template,request,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# for api
import requests

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
   # raise RuntimeError("DATABASE_URL is not set")

 #if not os.getenv("postgres://iorynocojkwjgc:d6104889e6eeee320700f04b6012980b77506087bded1c13ed5e9d155c97a245@ec2-107-22-162-8.compute-1.amazonaws.com:5432/d22b8flhk40kgi"):
 #	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://iorynocojkwjgc:d6104889e6eeee320700f04b6012980b77506087bded1c13ed5e9d155c97a245@ec2-107-22-162-8.compute-1.amazonaws.com:5432/d22b8flhk40kgi")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=['GET','POST'])
def index():
	if request.method=='POST':
		user =request.form.get('username')
		pswrd=request.form.get('passwrd')

		
		if user!="" and pswrd!="":
			try:
				usr=db.execute("SELECT * FROM users WHERE username=:user AND pswrd=:pswrd",{'user':user,'pswrd':pswrd}).fetchone()
				
				if usr.username== user:
					return render_template('search.html',user=usr)
				else: 
					return 'Invalid username or passwrd'
			except Exception as e:
				return 'Invalid input'
		else:
			return 'Invalid username or password'
	else:
		return render_template('index.html')

    
@app.route("/register",methods=['GET','POST'])
def register():
	if request.method=='GET':
		return render_template('register.html')
	else:
		username=request.form.get('username')
		pswrd=request.form.get('passwrd')
		
		

		try:
			db.execute("INSERT INTO users (username,pswrd) VALUES(:username,:pswrd)",{'username':username,'pswrd':pswrd})
			db.commit()
			return "Account has been"
		except Exception as e:
			return "Invalid username or password"
		
@app.route("/search",methods=['GET','POST'])
def search():
	name=request.form.get('srch')
	keyword=request.form.get('keyword')
	if name=='isbn':
		lists=db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",{'isbn':'%'+keyword+'%'}).fetchall()
	elif name=='title':
		lists=db.execute("SELECT * FROM books WHERE title LIKE :title",{'title':'%'+keyword+'%'}).fetchall()
	elif name=='author':
		lists=db.execute("SELECT * FROM books WHERE author LIKE :author",{'author':'%'+keyword+'%'}).fetchall()

	if request.method=='GET':
		return render_template('search.html')
	else:
		return render_template('search.html',lists=lists)

@app.route('/book_details/<int:book_id>')
def book_details(book_id):
	details=db.execute("SELECT * FROM books WHERE id=:book_id",{'book_id':book_id}).fetchone()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BKMKb4vaIpvUbGUseF2Yg", "isbns":details.isbn })
	data=res.json()
	avg_ratings=data["books"][0]['average_rating']
	num_ratings=data["books"][0]['work_ratings_count']
	#return jsonify(data["books"][0]['average_rating'])
	return render_template('book_details.html',avg_ratings=avg_ratings,num_ratings=num_ratings,details=details)






