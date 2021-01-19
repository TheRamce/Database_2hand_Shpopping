from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session ,current_app
from flask_mysqldb import MySQL 
import MySQLdb.cursors 
import re 
import settings,views
from database import Database
from product import Product
from user import User
from photo import Photo
import base64

import hashlib, binascii, os
def homepage():
    products_=[]
    mysql=current_app.config["db"]
    if request.method == 'GET' :
       
        types_=mysql.get_types()
        if not ('id' in session):
            return redirect(url_for('login'))
        else:   
            products_=mysql.get_P_R_P_n(session['id'])
        return render_template("home.html", products=products_,types=types_)
    
    elif request.method == 'POST' :
        if request.form['type'] != 'all':
            types_=mysql.get_types()
            if not ('id' in session):
                return redirect(url_for('login'))
            else: 
                typ_=request.form['type'] 
                products_=mysql. get_P_R_P_n_t(session['id'],typ_)
            return render_template("home.html", products=products_,types=types_)
        else: 
            types_=mysql.get_types()
            if not ('id' in session):
                return redirect(url_for('login'))
            else:   
                products_=mysql.get_P_R_P_n(session['id'])
            return render_template("home.html", products=products_,types=types_)






def login(): 
    msg = '' 
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form: 
        email = request.form['email'] 
        
        password = request.form['password'] 
        mysql=current_app.config["db"]
        account = mysql.get_user_with_mail(email) 
        if account: 
            if verify_password(account['userPassword'],password):
                session['loggedin'] = True
                current_app.config["log"]=True
                session['id'] = account['idUser'] 
                session['email'] = account['userMail']
                session['name'] =  account['userName']
                session['Sname']= account['userSurnaName']
                msg = 'Logged in successfully !'
                return redirect(url_for('homepage'))
            else:
                msg = 'Incorrect username / password !'
                return render_template('login.html', msg = msg)
           
        else: 
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

def register(): 
    msg = '' 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form : 
        username = request.form['username'] 
        surname = request.form['surname'] 
        
        password = request.form['password'] 

        email = request.form['email'] 
        test = email.split("@")
        if len(test)==2:
            if not ("itu.edu.tr" in test[1]):
                msg = 'Sign ın wit ITU mail !!!'
                return render_template('register.html', msg = msg)
        else:
            msg = 'Sign ın wit ITU mail !!!'
            return render_template('register.html', msg = msg)
        phone = request.form['phone'] 

        mysql=current_app.config["db"] 
        account= mysql.get_user_with_mail(email)
        if account: 
            msg = 'Account already exists !!!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'Invalid email address !!!'
        elif not re.match(r'[A-Za-z0-9]+', username): 
            msg = 'Username must contain only characters and numbers !!!'
        elif not username or not password or not email: 
            msg = 'Please fill out the form !!!'
        else:
            password_=hash_password (password)
            mysql.set_user_info(username, surname, email,password_,phone)
            msg = 'You have successfully registered '
            return redirect(url_for('login'))
            
    elif request.method == 'POST': 
        msg = 'Please fill out the form !!!'
    return render_template('register.html', msg = msg)


def logout(): 
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('username', None) 
    session.pop('surname', None) 
    session.pop('phone', None) 
    current_app.config["log"]=False
    return redirect(url_for('login'))

def products():
    
    products_=[]
    mysql=current_app.config["db"] 
    if request.method == "GET":
        if session['loggedin']:
            products_=mysql.get_Products(session['id'])
            st="data:image/png;base64,"
            for p in products_:
            
                phto=mysql.getOnePhoto(p.id)
                if phto!=None :
                    imgg=base64.b64encode(phto['photo']).decode("utf-8")
                    a=st+str(imgg)
                    p.photo=a
                else:
                    p.photo=''
        else:
            products_=None
            

        return render_template('products.html',products=products_)
    else:
      
       
        form_product_keys = request.form.getlist("product_key")
        for form_product_key in form_product_keys:
            mysql.delete_product(int(form_product_key))
        return redirect(url_for("products"))

def product(product_key):
    mysql=current_app.config["db"]
    product_=mysql.get_Product(product_key)
    phto=mysql.getPhoto(product_key)
    st="data:image/png;base64,"
    link=[]
    types_=mysql.get_types()
    for i in range (len(phto)):
        imgg=base64.b64encode(phto[i]['photo']).decode("utf-8")
        a=st+str(imgg)
        p=Photo(phto[i]['idPhoto'],a)
        link.append(p)
    if request.method == "GET":
        return render_template("product.html",product=product_,ps=link,types=types_)
    else:
        name=request.form['name']
        price=request.form['price']
        desc=request.form['description']
        typ=request.form['type']
        mysql.update_product(name,price,desc,product_key,typ)
        
        if  request.files['a_photo'] :
            
            ph=request.files['a_photo'].read()
            
            mysql.insert_Blob(ph,product_key)
            
        return redirect(url_for("products"))
    
def reqProduct(product_key):
    mysql=current_app.config["db"]
    product_,user_,link=mysql.get_Product_w_user(product_key)
    
    req_=mysql.get_Status_requests(product_key,session['id'])
  
    if request.method == "GET":
        return render_template("reProduct.html",product=product_,user=user_,photos=link,req=req_)
    else:
        mysql.make_request(session['id'],product_key)
        return redirect(url_for("homepage"))
    
def product_add_product():
    mysql=current_app.config["db"]
    types_=mysql.get_types()
    if request.method == "GET":
        values = {"name": "", "price": "","description":""}
        
        return render_template(
            "productEdit.html", values=values,types=types_)
    else:
        valid = validate_movie_form(request.form)
        if not valid:
            return render_template(
                "productEdit.html",values=request.form,types=types_)
        name = request.form.data["name"]
        price = request.form.data["price"]
        desc = request.form.data["description"]
        p_type=request.form["p_type"]
        ph=request.files['a_photo'].read()

        product = Product(Pid=session['id'],Pname=name,Pprice=price,Pdescription=desc,PisSold=0,Ptype=p_type)
        
        _key = mysql.add_product(product)
        
        mysql.insert_Blob(ph,_key)
        return redirect(url_for("products"))

def requestedProducts():
    mysql=current_app.config["db"]
    products_=mysql.get_My_requests(session['id'])
    
    stat_=mysql.get_Nstatus(session['id'])
    return render_template('requests.html',products=products_,stat=stat_)

def requestedProduct(product_key):
    mysql=current_app.config["db"]
    if request.method == "GET":
        
        product_, user_ =mysql.get_get_user_and_prod(product_key)
        stat_=mysql.get_Status_requests(product_key,session['id'])
       
        comment_=None
        if stat_==1 or stat_==3:
            if stat_==3:
                comment_=mysql.get_my_comment(product_key,session['id'])

        else:
            user_=None

        return render_template("Myrequest.html",product=product_,stat=stat_,user=user_,comment=comment_)
    elif request.method == "POST":
        mysql.delete_request(session['id'],product_key)
        return redirect(url_for("requestedProducts"))

def listRequests():
    mysql=current_app.config["db"]
    dic_=mysql.get_request_to_my_products(session['id'])
    
    return render_template('listrequests.html',dic=dic_)

def listRequst(userId,prodId):
    mysql=current_app.config["db"]
    user_=mysql.get_user_with_id(userId)
    product_,link=mysql.get_Product_w_photo(prodId)
    (product_).Pstat=mysql.get_Status_requests(prodId,userId)
    
    return render_template("ac_rec.html",product=product_,user=user_,ps=link)

def acceptRequest(userId,prodId):
    mysql=current_app.config["db"]
    mysql.accept_reject_Request(userId,prodId,1)
    return redirect(url_for("listRequests"))

def rejectRequest(userId,prodId):
    mysql=current_app.config["db"]
    mysql.accept_reject_Request(userId,prodId,0)
    return redirect(url_for("listRequests"))

def sellProduct(userId,prodId):
    mysql=current_app.config["db"]
    mysql.sell_product(userId,prodId)
    return redirect(url_for("listRequests"))

def commentProduct(userId,prodId):
    mysql=current_app.config["db"]
    
    if request.method =="GET":
        comment_=mysql.get_my_comment(prodId,session['id'])
        
        
        return render_template("star.html",str=comment_,Id=prodId)

    else:
        l=[]
        for i in request.form.values():
            l.append(i)
            
            
        mysql.insert_comment(userId,prodId,l[1],l[0])
        
        return redirect(url_for("requestedProducts"))

def  edit_comment(product_key,senderId):
        mysql=current_app.config["db"]
        if request.method == "GET":
            comment_=mysql.get_my_comment(product_key,senderId)
         
            return render_template("editcomment.html",comment=comment_)
    
        else:
            print("burdayızbe")
            
            comment=request.form['comment']
            star=request.form['star']
            mysql.update_comment(comment,star,senderId,product_key)
            return redirect(url_for("requestedProduct",product_key=product_key))

def delete_comment(product_key,senderId):
    mysql=current_app.config["db"]
    
    mysql.delete_One_comment(senderId,product_key)
    return redirect(url_for("requestedProduct",product_key=product_key))


def listComments():
    mysql=current_app.config["db"]
    dict_=mysql.list_my_comments(session['id'])
    
    return render_template("comments.html",dict=dict_)


def validate_movie_form(form):
    form.data = {}
    form.errors = {}

    form_name = form.get("name", "").strip()
    if len(form_name) == 0:
        form.errors["name"] = "Name can not be blank."
    else:
        form.data["name"] = form_name

    form_desc = form.get("description", "").strip()
    if len(form_desc) == 0:
        form.errors["description"] = "Description can not be blank."
    else:
        form.data["description"] = form_desc

    form_price = form.get("price")
    
    if not form_price:
        form.data["price"] = None
        form.errors["price"] = "Price must not be empty."
    elif not form_price.isdigit():
        form.errors["price"] = "Price must consist of digits only."
    else:
        price = int(form_price)
        if (price <= 0) :
            form.errors["price"] = "Price not in valid range."
        else:
            form.data["price"] = price
    
    return len(form.errors) == 0
    



def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def get_update_User():
    mysql=current_app.config["db"]
    if request.method =="GET":
        
        user_=mysql.get_user_with_id(session['id'])
        
        return render_template("user.html",user=user_)
    elif request.method =="POST":
        name=request.form['name']
        sname=request.form['sname']
        mail=request.form['mail']
        phone=request.form['phone']
        password=request.form['password']
        if ('XXXX' in password) :
            mysql.update_user(name,sname,mail,phone,session['id'])
        else:
            password=hash_password(password)
            mysql.update_user_w_p(name,sname,mail,phone,session['id'],password)
        return   redirect(url_for("get_update_User"))

def user_delete_User():
    mysql=current_app.config["db"]
    mysql.delete_use(session['id'])
    return redirect(url_for("logout"))

def delete_my_req():
    mysql=current_app.config["db"]
    mysql.delete_use(session['id'])
    return redirect(url_for("logout"))




    
   




   