from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
# from flask_mail import Mail # for sending emails
import os
from werkzeug.utils import secure_filename # update, this is a new import libarary for uploading files
import math #for pagination purposes


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


local_server = True
app = Flask(__name__)
app.secret_key = 'SECRET KEY'
app.config['UPLOAD_FOLDER'] = params['upload_location']

'''
sending mails
'''
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail_user'],
#     MAIL_PASSWORD=params['gmail_password']
# )
# mail=Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:   
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_num = db.Column(db.String(120), nullable=False)
    mes = db.Column(db.String(120), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all() 
    # [0: 5]
    last = math.ceil(len(posts)/5) #5 as in number of posts per page    
    page=request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page=int(page)
    posts=posts[int(page-1)*5:int(page)*5+5] #params['no_of_posts'] hona chahiye tha but i didn't used it.
    '''
    Pagination logic:
    1. First page
    prev=#
    next=page+1
    2. Middle page
    prev=page-1
    next=page+1
    3. Last page
    prev=page-1
    next=#
    '''
    #First
    if (page==1):
        prev="#"
        next = "/?page=" + str(int(page) + 1)
   #last
    elif(page==last):
        prev= "/?page=" + str(int(page) - 1)
        next = "#"
    #Middle
    else:
        prev= "/?page=" + str(int(page) - 1)
        next = "/?page=" + str(int(page) + 1)
    
   
   
    return render_template("index.html", params=params, posts=posts, prev=prev, next=next)
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params ['admin_name']):
        posts = Posts.query.all()
        return render_template ('dashboard.html', params=params, posts=posts) 
    
    if request.method=='POST':
        # REDIRECT TO ADMIN
        username=request.form.get('uname')
        password=request.form.get('pass')
        if (username== params['admin_name'] and password==params['admin_password']):
            #set the session variable 
            session['user']= username
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)
    else:
        return render_template("login.html", params=params)

@app.route("/post/<string:post_slug>", methods=['GET']) # string:post_slug is a variable, also important keep in note
def post_route(post_slug):
        post = Posts.query.filter_by(slug=post_slug).first()
        return render_template('post.html', params=params, post=post)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params ['admin_name']):
        if request.method=='POST':
            box_title=request.form.get('title')
            slug=request.form.get('slug')
            content=request.form.get('content')
            if sno=='0':
                post=Posts(title=box_title, slug=slug, content=content)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
     if ('user' in session and session['user'] == params ['admin_name']):
         post=Posts.query.filter_by(sno=sno).first()
         db.session.delete(post)
         db.session.commit()
         return redirect("/dashboard")



@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session ['user']==params['admin_name']):
        if (request.method=='POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "upload successfully"

@app.route("/logout")
def logout():
    session.pop('user') #killing usersession
    return redirect ('/dashboard')

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/contact", methods=['GET', 'POST']) 
def contact ():
    if (request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone_num=request.form.get('phone_num')
        mes=request.form.get('mes')
        entry= Contacts(name=name, phone_num=phone_num, email=email, mes=mes) #isme hamne sno nahi dala hai, so we are assuming ki vo apne aap lelega, and for that, ham ek initial entry database me de denge

        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New message from ' + name, sender=email, recipients=[params['gmail_user']], body= mes + "/n" + phone_num)
        
    # '''
    # Issue arised: no module found named "mysql db"
    # solution:
    # pip install mysqlclient
    # '''
    return render_template('contact.html')

app.run(debug=True, host="0.0.0.0") #host="0.0.0.0" will make the page accessable by going to http://[ip]:5000/ on any computer in the network