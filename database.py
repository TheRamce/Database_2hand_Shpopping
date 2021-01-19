from flask_mysqldb import MySQL 
import settings
from product import Product
from user import User
from photo import Photo
import datetime
import base64

class Database:
    def __init__(self, app):
        app.secret_key = 'your secret key'
        app.config['MYSQL_HOST'] = settings.SQL_HOST
        app.config['MYSQL_USER'] = '' 
        #app.config['MYSQL_USER'] ='root'
        app.config['MYSQL_PASSWORD'] = settings.PASSWORD
        app.config['MYSQL_DB'] = '' 
        #app.config['MYSQL_DB'] ='shema'
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        mysql = MySQL(app)
        self.dbfile = mysql

    def get_user_info(self,email,password):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT * FROM usertable WHERE userMail = % s AND userPassword = % s', (email, password, ))
        return  cursor.fetchone() 

    def get_user_with_mail(self,email):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT * FROM usertable  WHERE userMail = % s', (email, )) 
        return  cursor.fetchone() 

    def get_user_with_id(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT * FROM usertable  WHERE idUser = % s', (key, )) 
        dic=cursor.fetchone()
        user=User(idUser=dic['idUser'],userName=dic['userName'],userSurnaName=dic['userSurnaName'],userMail=dic['userMail'],userPhone=dic['userPhone'])
        return user

    def set_user_info(self,username, surname, email,password,phone):
        cursor = self.dbfile.connection.cursor()
        cursor.execute('INSERT INTO usertable VALUES (NULL,% s,%s, % s, % s,%s)', (username, surname, email,password,phone, )) 
        self.dbfile.connection.commit() 
        
    def get_Products(self,user_id):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT userId,idProduct, productName, price FROM producttable  WHERE userId = % s', (user_id, )) 
        products=[]
        p_list=cursor.fetchall()
        i=0
        for uId,pId , pName ,Pprice in p_list:
            
            products.append(Product(PidUser=p_list[i][uId],Pid=p_list[i][pId],Pname=p_list[i][pName],Pprice=p_list[i][Pprice],Pdescription=None,PisSold=0))
            i=i+1
        return products

    def get_Product(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT userId,productName, price,description,isSold FROM producttable  WHERE idProduct = % s', (key, ))
        dic=cursor.fetchone() 
        
        
        product=Product(PidUser=dic['userId'],Pid=key,Pname=dic['productName'],Pprice=dic['price'],Pdescription=dic[ 'description'],PisSold=dic['isSold'])
        return product


    def get_Product_w_photo(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('''SELECT * FROM producttable 
        
        Inner join phototable ON producttable.idProduct =phototable.productId
        where idProduct = % s''', (key, ))
        dic=cursor.fetchall() 

        product=Product(Pid=key,Pname=dic[0]['productName'],Pprice=dic[0]['price'],Pdescription=dic[0][ 'description'],PisSold=dic[0]['isSold'],PidUser=dic[0]['userId'])

        st="data:image/png;base64,"
        link=[]
        for i in range (len(dic)):
            imgg=base64.b64encode(dic[i]['photo']).decode("utf-8")
            a=st+str(imgg)
            p=Photo(dic[i]['idPhoto'],a)
            link.append(p)
        return product,link

    def get_Product_w_user(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('''SELECT * FROM producttable 
        INNER JOIN usertable ON producttable.userId= usertable.idUser 
        Inner join phototable ON producttable.idProduct =phototable.productId
        where idProduct = % s''', (key, ))
        dic=cursor.fetchall() 
        
        
        user=User(idUser=dic[0]['idUser'],userName=dic[0]['userName'],userSurnaName=dic[0]['userSurnaName'],userMail=dic[0]['userMail'],userPhone=dic[0]['userPhone'])
        product=Product(Pid=key,Pname=dic[0]['productName'],Pprice=dic[0]['price'],Pdescription=dic[0][ 'description'],PisSold=dic[0]['isSold'],PidUser=dic[0]['idUser'])
        
        st="data:image/png;base64,"
        link=[]
        for i in range (len(dic)):
            imgg=base64.b64encode(dic[i]['photo']).decode("utf-8")
            a=st+str(imgg)
            p=Photo(dic[i]['idPhoto'],a)
            link.append(p)
        return product,user,link

    def get_P_R_P_n(self,user_id):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('''SELECT   userId,idProduct,description, productName, price,photo  FROM producttable
                        inner join phototable ON idProduct=phototable.productId
                        where PhotoOrder =1 and userId <> %s and issold=0
                        group by userId,idProduct  
                        ''', (user_id,)) 
        products=[]
        p_list=cursor.fetchall()
       
        i=0
        st="data:image/png;base64,"
        for i in range (len(p_list)):
            if p_list[i]['photo'] :
                imgg=base64.b64encode(p_list[i]['photo']).decode("utf-8")
                a=st+str(imgg)
            else:
                a=''    
            products.append(Product(PidUser=p_list[i]['userId'],Pid=p_list[i]['idProduct'],Pname=p_list[i]['productName'],Pprice=p_list[i]['price'],Pdescription=p_list[i]['description'],PisSold=0,Pphoto=a))    
        return products

    def get_P_R_P_n_t(self,user_id,typ):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute(''' SELECT   userId,idProduct,description, productName, price,photo  FROM producttable
                        inner join phototable ON idProduct=phototable.productId
                        where PhotoOrder =1 and userId <> %s and issold=0  and typeId =%s
                        group by userId, idProduct ''', (user_id,typ, )) 
        products=[]
        p_list=cursor.fetchall()
        i=0
        st="data:image/png;base64,"
        for i in range (len(p_list)):
            if p_list[i]['photo'] :
                imgg=base64.b64encode(p_list[i]['photo']).decode("utf-8")
                a=st+str(imgg)
            else:
                a=''    
            products.append(Product(PidUser=p_list[i]['userId'],Pid=p_list[i]['idProduct'],Pname=p_list[i]['productName'],Pprice=p_list[i]['price'],Pdescription=p_list[i]['description'],PisSold=0,Pphoto=a))    
        return products

    def delete_product(self,key):
        cursor = self.dbfile.connection.cursor()
        cursor.execute('DELETE FROM producttable WHERE idProduct = % s', (key, ))
        self.dbfile.connection.commit()
 
    def add_product(self,product):
        cursor = self.dbfile.connection.cursor()
        pTime= datetime.datetime.now()
        cursor.execute('INSERT INTO producttable VALUES (NULL,% s,%s, % s, % s,% s, %s,%s)', (product.id,product.type ,product.name, product.price,product.description,product.isSold,pTime, )) 
        self.dbfile.connection.commit()
        return cursor.lastrowid

    def get_All_products(self,key):
        cursor = self.dbfile.connection.cursor()
        '''
            SELECT idUser, idProduct, productName,	description,isSold FROM producttable INNER JOIN usertable ON producttable.userId= usertable.idUser where idProduct
        '''
        cursor.execute('SELECT userId,idProduct,description, productName, price FROM producttable where userId <> %s',(key, )) 
        products=[]
        
        p_list=cursor.fetchall()
        
        i=0
        for uId,pId , description,pName ,Pprice in p_list:  
            
            products.append(Product(PidUser=p_list[i][uId],Pid=p_list[i][pId],Pname=p_list[i][pName],Pprice=p_list[i][Pprice],Pdescription=p_list[i][description],PisSold=0))
            i=i+1
        return products

    def make_request(self,userId,productId):
        cursor = self.dbfile.connection.cursor()
        pTime= datetime.datetime.now()
        cursor.execute('INSERT INTO requesttable VALUES (%s,% s,%s, % s)', (userId, productId, 2,pTime, ))
        self.dbfile.connection.commit() 

    def get_My_requests(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT * FROM requesttable INNER JOIN producttable ON productId= producttable.idProduct where senderId =%s', (key, ))
        #cursor.execute('SELECT * FROM requesttable where senderId= %s',(key,))
        p_list=cursor.fetchall()
        products=[]
        
       
        for i in range(len(p_list)):
            
            products.append(Product(PidUser=p_list[i]['userId'],Pid=p_list[i]['idProduct'],Pname=p_list[i]['productName'],Pprice=p_list[i]['price'],Pdescription=p_list[i]['description'],PisSold=p_list[i]['isSold'],Pstat=p_list[i]['statusProduct']))
            
      
        return products

    def get_Status_requests(self,key,id):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT statusProduct FROM requesttable where senderId=%s and productId=%s;', (id,key, ))
        dic=cursor.fetchone()
        if dic:
             return dic['statusProduct']
        else:
            return None
            
    def get_request_to_my_products(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('''SELECT senderId,idProduct,productName,price,description,userName,idUser,userSurnaName,isSold,userMail,userPhone FROM requesttable INNER JOIN producttable ON productId= producttable.idProduct
                        INNER JOIN usertable ON senderId=idUser
                        where productId in (select idProduct from producttable where userId=%s )''', (key, ))

        dic=cursor.fetchall()
        
        
        return dic
    
    def accept_reject_Request(self,userId,proId,key):
        cursor = self.dbfile.connection.cursor()
        cursor.execute('UPDATE requesttable SET statusProduct = %s WHERE senderId =%s  and productId= %s', (key,userId, proId,  ))
        self.dbfile.connection.commit()

    def get_types(self):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("SELECT * FROM producttype")
        return cursor.fetchall()

    def change_isSold(self,prodId,key):
        cursor = self.dbfile.connection.cursor()
        cursor.execute('UPDATE  producttable SET isSold = %s  where idProduct= %s', (key,prodId,  ))
        self.dbfile.connection.commit()

    def sell_product(self,userId,proId):
        cursor = self.dbfile.connection.cursor()
        cursor.execute('UPDATE requesttable SET statusProduct = %s WHERE senderId = %s  and productId = %s', (3,userId, proId,  ))
        cursor.execute('UPDATE requesttable SET statusProduct = %s WHERE senderId <> %s  and productId = %s', (0,userId, proId,  ))
        self.dbfile.connection.commit()
        self.change_isSold(proId,1)
  
    def insert_comment(self,userId,proId,comment,star):
        cursor = self.dbfile.connection.cursor()
        pTime= datetime.datetime.now()
        cursor.execute('INSERT INTO commenttable VALUES (%s,% s,%s, % s ,%s)', (userId, proId, comment,star,pTime, ))
        
        self.dbfile.connection.commit()

    def list_my_comments(self,userId):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("SELECT UserId , productId, commentProduct,star,Ptime,userName,userSurnaName FROM commenttable INNER JOIN usertable ON commenttable.UserId= usertable.idUser where productId in (select idProduct from producttable where userId = %s)",(userId,))
        return cursor.fetchall()

    def get_my_comment(self,proId,userId):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("SELECT commentProduct,star,Ptime FROM commenttable where UserId =%s and productId=%s",(userId,proId))
       
        lst=cursor.fetchone()
      
        return lst

    def insert_Blob(self,Bfile,prodId):
        cursor = self.dbfile.connection.cursor()
        cursor.execute('SELECT count(photo) FROM phototable where productId=%s',(prodId,))
        count=int(cursor.fetchone()['count(photo)'])
        count=count+1
        cursor.execute('INSERT INTO phototable VALUES (NULL,%s,%s, %s)', (prodId, Bfile,count, ))
        self.dbfile.connection.commit()

    def getPhoto(self,key):
        cursor = self.dbfile.connection.cursor() 
        
        cursor.execute('SELECT idPhoto,photo FROM phototable where productId= %s',(key,))
        return cursor.fetchall()
   
    def getOnePhoto(self,key):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT idPhoto,photo FROM phototable where productId= %s',(key,))
        return cursor.fetchone()

    def get_Nstatus(self,sender):
        cursor = self.dbfile.connection.cursor() 
        cursor.execute('SELECT statusProduct,count(*) as Nstat  FROM requesttable where senderId=%s group by statusProduct',(sender,))
        stat=[0,0,0,0]
        lst= cursor.fetchall()
        for i in range(len(lst)):
            index=int(lst[i]['statusProduct'])
            stat[index]=int(lst[i]['Nstat'])
        return stat

    def update_product(self,name,price,desc,key):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("UPDATE  producttable set productName=%s , price=%s , description=%s where idProduct =%s",(name,price,desc,key,))
        self.dbfile.connection.commit()

    def update_user(self,name,sname,mail,phone,idUser):


        cursor = self.dbfile.connection.cursor()
        cursor.execute("UPDATE usertable SET userName =%s , userSurnaName=%s , userMail=%s ,userPhone=%s where idUser= %s",(name,sname,mail,phone,idUser,))
        self.dbfile.connection.commit()

    def delete_use(self,userId):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("DELETE FROM usertable where idUser =%s",(userId,))
        self.dbfile.connection.commit()

    def delete_request(self,userId,prodId):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("DELETE FROM requesttable where senderId =%s and productId=%s;",(userId,prodId))
        self.dbfile.connection.commit()

    def get_get_user_and_prod(self,prodId): 

        cursor = self.dbfile.connection.cursor() 
        cursor.execute('''SELECT * FROM producttable 
        INNER JOIN usertable ON producttable.userId= usertable.idUser 
        where idProduct = % s''', (prodId, ))
        dic=cursor.fetchone() 
        
        
        user=User(idUser=dic['idUser'],userName=dic['userName'],userSurnaName=dic['userSurnaName'],userMail=dic['userMail'],userPhone=dic['userPhone'])
        product=Product(Pid=prodId,Pname=dic['productName'],Pprice=dic['price'],Pdescription=dic[ 'description'],PisSold=dic['isSold'],PidUser=dic['idUser'])
        
        
        return product,user

    def update_comment(self,comment,star,uId,pId):
        pTime= datetime.datetime.now()
        cursor = self.dbfile.connection.cursor()
        cursor.execute('''UPDATE commenttable SET commentProduct= %s , star=%s , Ptime=%s 
                        where UserId=%s and productId=%s''',(comment,star,pTime,uId,pId,))
        self.dbfile.connection.commit()

    def delete_One_comment(self,senderId,product_key):
        cursor = self.dbfile.connection.cursor()
        cursor.execute("DELETE FROM commenttable where UserId =%s and productId=%s;",(senderId,product_key,))
        self.dbfile.connection.commit()


    