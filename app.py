from flask import Flask, render_template, request, redirect, url_for, session 
from flask_mysqldb import MySQL 
import MySQLdb.cursors 
import re 
import settings,views
from database import Database
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        response.headers.add('Access-Control-Allow-Headers',
                            'Content-Type,Authorization')
        return response
    app.config['CORS_HEADERS'] = 'Content-Type'
    cors = CORS(app, resources={r"/": {"origins": ""}})
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.homepage,methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login,methods=["GET", "POST"])
    app.add_url_rule("/register", view_func=views.register,methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout,methods=["GET", "POST"])
    app.add_url_rule("/products", view_func=views.products,methods=["GET", "POST"])
    app.add_url_rule("/requestedProducts", view_func=views.requestedProducts) 
    app.add_url_rule("/listRequests", view_func=views.listRequests)

    app.add_url_rule("/deleteUser", view_func=views.user_delete_User)

    app.add_url_rule("/UserSettings", view_func=views.get_update_User,methods=["GET", "POST"])

    app.add_url_rule("/listComments/<int:product_key>/<int:senderId>", view_func=views.edit_comment,methods=["GET", "POST"])

    app.add_url_rule("/<int:product_key>/<int:senderId>", view_func=views.delete_comment,methods=["GET", "POST"])

    app.add_url_rule("/listComments", view_func=views.listComments) 

    app.add_url_rule("/requestedProducts/<int:product_key>", view_func=views.requestedProduct,methods=["GET", "POST"] )


    app.add_url_rule("/listRequst/<int:userId>/<int:prodId>", view_func=views.listRequst,methods=["GET", "POST"])

    app.add_url_rule("/acceptRequest/<int:userId>/<int:prodId>", view_func=views.acceptRequest,methods=["GET", "POST"])
    app.add_url_rule("/rejectRequest/<int:userId>/<int:prodId>", view_func=views.rejectRequest,methods=["GET", "POST"])
    app.add_url_rule("/sellProduct/<int:userId>/<int:prodId>", view_func=views.sellProduct,methods=["GET", "POST"]) 
    app.add_url_rule("/comment/<int:userId>/<int:prodId>", view_func=views.commentProduct,methods=["GET", "POST"])
    app.add_url_rule("/products/<int:product_key>", view_func=views.product,methods=["GET", "POST"]) 
   
    app.add_url_rule("/<int:product_key>", view_func=views.reqProduct, methods=["GET", "POST"])
    app.add_url_rule( "/new-product", view_func=views.product_add_product, methods=["GET", "POST"])
    mysql = Database(app)
    app.config["db"] = mysql
    app.config["log"]=False
    return app

if __name__ == '__main__':
    app= create_app()
    app.run(debug=False)

    