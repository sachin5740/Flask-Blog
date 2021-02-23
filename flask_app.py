from flask import Flask,render_template,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from datetime import datetime
from werkzeug import secure_filename
import json
import os
import wikipedia
a=open("config.json","r")
info=json.load(a)["info"]
app=Flask(__name__)
if info["localhost"]:
    app.config['SQLALCHEMY_DATABASE_URI']=info["localhost_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI']=info["production_uri"]

app.secret_key = 'MEENA_Ji_IS_SUPERKEY'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sachin.meena3198@gmail.com'
app.config['MAIL_PASSWORD'] = 'sachin@9754995740'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail=Mail(app)

db=SQLAlchemy(app)

class feedback(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=False)
    mobile=db.Column(db.Integer(),nullable=False)
    email=db.Column(db.String(80),nullable=False)
    massage=db.Column(db.String(255),nullable=False)

class Posts(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(20),nullable=False)
    route=db.Column(db.String(20),nullable=False)
    detail=db.Column(db.String(220),nullable=False)
    date_time=db.Column(db.String(20),nullable=False)
    content=db.Column(db.String(120),nullable=False)
    img_data=db.Column(db.String(120),nullable=False)



#start a code of route and other functionality
@app.route('/admin',methods=['GET','POST'])
def admin():
    post=Posts.query.order_by(Posts.sno.asc()).all()
    if ('user' in session and session['user']==info['username']):
        return render_template("Dashboard.html",logger= "Logged in succesfully",info=info,post=post)
    
    if request.method=='POST':
        print("sachin")
        user=request.form.get('Admin_username')
        u_pass=request.form.get('Admin_password')
        print(user,u_pass)
    
        if user==info['username'] and u_pass==info['User_password']:
            session['user']=user
            return render_template("Dashboard.html",logger= "Logged in succesfully",info=info,post=post)
        else:
            return render_template("login.html",logger="Logged in fail",info=info)
    else:
        return render_template('login.html',info=info)
@app.route("/logout",methods=["POST","GET"])
def logout():
    session.pop('user',None)
    return redirect(url_for('admin'))

@app.route("/")
def index():
    post=Posts.query.filter_by().all()
    #[0:info["NO_OF_POST"]]
    last=len(post)//int(info["NO_OF_POST"])
    print("lenth of post is {} and and last post is {}".format(len(post),last))
    page=request.args.get("page")
    print("page--",page)
    if (not str(page).isnumeric()):
        page=0
    print(type(page))
    page=int(page)
    post=post[int(page*info["NO_OF_POST"]):int(page*info["NO_OF_POST"])+int(info["NO_OF_POST"])]
    #first
    if (page==1):
        prev="/"
        next="/?page="+str((page+1))
    #last
    elif(page==last):
        prev="/?page="+str((page-1))
        next="#"
    else:
        prev="/?page="+str((page-1))
        next="/?page="+str((page+1))
    
    
    return render_template("index.html",links="bg.jpg",info=info,post=post,prev=prev,next=next)


@app.route("/post/<data>",methods=["GET"])
#@app.route("/post")
def post_route(data):
    post=Posts.query.filter_by(route=data).first()
    #which identify a url slug (route) and provide dynamic url -> post=post.query.filter_by(post_slug)
    data=wikipedia.page("{}".format(post.title))
    return render_template("post.html",info=info,post=post,data=data)
@app.route("/post")
def post():
    post=Posts.query.filter_by().all()
    from datetime import datetime
    return render_template("preview_post.html",info=info,time=datetime.now(),post=post)

@app.route("/about")
def about():
    return render_template("about.html",info=info)
@app.route("/contact", methods=['GET','POST'])
def contact():
    
    ms=''
    if(request.method=='POST'):
        try:
            name=request.form.get('name')
            email=request.form.get('email')
            mobile=request.form.get('number')
            massage=request.form.get('message')
            if name!='' and email!='' and mobile!='' and massage!='':
                entry=feedback(name=name,mobile=mobile,email=email,massage=massage)
                db.session.add(entry)
                db.session.commit()
                ms="Your Massage are suceesfully sent to admin ..Response will soon.."

                try:
                    #mail sender
                    '''
                    mail.send_message(["NEW MASSAGE FROM"+name],
                    sender=[info["GMAIL_USER"]],
                    recipients="[sachin.meena9754995740@gmail.com]",
                    body=[massage+"\n sender phone no"+mobile])
                    print("Mail are Succesfully sent")'''
                    msg=Message("NEW MAIL FROM YOU CODING BLOG",
                    sender=info["GMAIL_USER"],
                    recipients=[info["GMAIL_USER"]])
                    msg.body="hello sir I am "+name+"\n and i want to say that "+massage+"\n massage from "+email+"\n mobile no "+mobile
                    mail.send(msg)
                    print("mail are succefully send")


                except Exception as e :
                    print(e)
            else:
                ms="Please fill all entrys ... And try again"
        except Exception as error :

            print(error)
            ms="OopS.. Something went worng your massage can't be sended in this Time please try sometime later"
    return render_template("contact.html",a=ms,info=info)

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']==info['username']:
        date=datetime.now().date()
        data=Posts.query.filter_by(sno=sno).first()
        if request.method=='POST':
            title=request.form.get('Title')
            detail=request.form.get('detail')
            image=request.form.get('image_name')
            content=request.form.get('content')
            if title!='' and detail!='' and image!='' and content!='' and sno=='0':
                post_data=Posts(title=title,detail=detail,img_data=image,content=content,route=title,date_time=date)
                db.session.add(post_data)
                db.session.commit()
                return redirect("/edit/"+sno)
            else:
                data.title=title
                data.detail=detail
                data.img_data=image
                data.content=content
                data.date_time=date
                data.route=title
                db.session.commit()
                redirect("/edit/"+sno)
    return render_template('edit.html',info=info,sno=sno,cdate=date,f_data=data)

@app.route("/uploader",methods=['GET','POST'])
def uplader():
    if ('user' in session and session['user']==info['username']):
        if (request.method=='POST'):
            file=request.files["file"]
            file.save(os.path.join(info['Upload_location']+secure_filename(file.filename)))
            return "File suceefully Uplaoded"
    return render_template('uploader.html')

@app.route("/delete/<string:sno>",methods=["GET","POST"])
def delete(sno):
    if 'user' in session and session['user']==info['username']:
        file=Posts.query.filter_by(sno=sno).first()
        db.session.delete(file)
        db.session.commit()
    return redirect('/admin')



app.run(debug=True)
