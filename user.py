class User:
    def __init__(self,idUser,userName,userSurnaName,userMail,userPhone,Ppassword=None):
        self.id=idUser
        self.name = userName
        self.surName = userSurnaName
        self.mail=userMail
        self.phone=userPhone
        self.pasword=Ppassword