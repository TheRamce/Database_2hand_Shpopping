class Product:
    def __init__(self,Pid,Pname,Pprice,Pdescription,PisSold=None,PidUser=None,Pstat=None,Ptype=None,Pphoto=None):
        self.id=Pid
        self.name = Pname
        self.description = Pdescription
        self.price=Pprice
        self.isSold=PisSold
        self.user=PidUser
        self.status=Pstat
        self.type=Ptype
        self.photo=Pphoto