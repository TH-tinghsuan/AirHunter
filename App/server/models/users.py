from server import db, login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from server.models.flight import get_airport_detail
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key = True)
    account    = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64),unique=True, index=True)
    password = db.Column(db.String(128))

    db_user_fav = db.relationship('UserFavorite', backref='uesrs')

    def __init__(self, account, username, password):
        self.account = account
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_user_name(account):
    db.session.commit()
    user = User.query.filter_by(account=account).first()
    return user.username

class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True,  nullable=False)
    go_arrive_airport_code = db.Column(db.String(3),primary_key = True, nullable=False)
    go_arrive_time = db.Column(db.DateTime(), primary_key = True, nullable=False)
    go_depart_airport_code = db.Column(db.String(3), primary_key = True, nullable=False)
    go_depart_time = db.Column(db.DateTime(), primary_key = True, nullable=False)
    back_arrive_airport_code = db.Column(db.String(3))
    back_arrive_time = db.Column(db.DateTime())
    back_depart_airport_code = db.Column(db.String(3))
    back_depart_time = db.Column(db.DateTime())
    price = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean)

    def __init__(self, user_id, go_arrive_airport_code, 
                 go_arrive_time, go_depart_airport_code, 
                 go_depart_time, back_arrive_airport_code, 
                 back_arrive_time, back_depart_airport_code, 
                 back_depart_time, price, active=True):
        self.user_id = user_id
        self.go_arrive_airport_code = go_arrive_airport_code
        self.go_arrive_time = go_arrive_time
        self.go_depart_airport_code = go_depart_airport_code
        self.go_depart_time = go_depart_time
        self.back_arrive_airport_code = back_arrive_airport_code
        self.back_arrive_time = back_arrive_time
        self.back_depart_airport_code = back_depart_airport_code
        self.back_depart_time = back_depart_time
        self.price = price
        self.active = active


def create_user_fav(data):
    """
        insert a record into user_favorites table, if it already exist, set active to True
        parameter shoule be dictionary with key='user_id', 'arrive_airport_code', 
                 'arrive_time', 'depart_airport_code', 'depart_time', 'price'
    """
    db.session.commit()
    query = UserFavorite.query.filter_by(user_id = data['user_id'],go_arrive_airport_code=data['go_arrive_airport_code'],
                                         go_arrive_time = data['go_arrive_time'], go_depart_airport_code=data['go_depart_airport_code'],
                                         go_depart_time = data['go_depart_time'],back_arrive_airport_code=data['back_arrive_airport_code'],
                                         back_arrive_time = data['back_arrive_time'], back_depart_airport_code=data['back_depart_airport_code'],
                                         back_depart_time = data['back_depart_time']).first()
    if not query:
        user_fav_model = UserFavorite(**data) 
        db.session.add(user_fav_model)
        db.session.commit()
    else:
        query.active = True
        db.session.commit() 

        
def del_user_fav(data):
    """
        set a record in user_favorites table as inactive.
        parameter shoule be dictionary with key='user_id', 'arrive_airport_code', 
                 'arrive_time', 'depart_airport_code', 'depart_time'
    """
    db.session.commit()
    query = UserFavorite.query.filter_by(user_id = data['user_id'],go_arrive_airport_code=data['go_arrive_airport_code'],
                                         go_arrive_time = data['go_arrive_time'], go_depart_airport_code=data['go_depart_airport_code'],
                                         go_depart_time = data['go_depart_time'],back_arrive_airport_code=data['back_arrive_airport_code'],
                                         back_arrive_time = data['back_arrive_time'], back_depart_airport_code=data['back_depart_airport_code'],
                                         back_depart_time = data['back_depart_time'])
    query.update({"active": False})
    db.session.commit()



def get_user_fav(userID):
    """
        retrieve a user's favorite list by user ID.
    """
    db.session.commit()
    query = UserFavorite.query.filter_by(user_id = userID, active=True).all()
    
    fav_list = []
    for item in query:
        fav = {}
        fav["go_arrive_airport"] = get_airport_detail(item.go_arrive_airport_code)['airport_name']
        fav["go_arrive_airport_code"] = item.go_arrive_airport_code
        fav["go_arrive_time"] = item.go_arrive_time.strftime("%Y-%m-%d %H:%M")
        fav["go_depart_airport"] = get_airport_detail(item.go_depart_airport_code)['airport_name']
        fav["go_depart_airport_code"] = item.go_depart_airport_code
        fav["go_depart_time"] = item.go_depart_time.strftime("%Y-%m-%d %H:%M")
        if item.back_arrive_airport_code:
            fav["back_arrive_airport"] = get_airport_detail(item.back_arrive_airport_code)['airport_name']
            fav["back_arrive_airport_code"] = item.back_arrive_airport_code
            fav["back_arrive_time"] = item.back_arrive_time.strftime("%Y-%m-%d %H:%M")
            fav["back_depart_airport"] = get_airport_detail(item.back_depart_airport_code)['airport_name']
            fav["back_depart_airport_code"] = item.back_depart_airport_code
            fav["back_depart_time"] = item.back_depart_time.strftime("%Y-%m-%d %H:%M")
            fav["schedule"] = "return"
        else:
            fav["schedule"] = "oneWay"
        fav_list.append(fav)
    return fav_list