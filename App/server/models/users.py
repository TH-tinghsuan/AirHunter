from server import db, login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import update
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
    user = User.query.filter_by(account=account).first()
    return user.username

class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True,  nullable=False)
    arrive_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    arrive_time = db.Column(db.DateTime(), nullable=False)
    depart_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    depart_time = db.Column(db.DateTime(), primary_key=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean)

    def __init__(self, user_id, arrive_airport_code, 
                 arrive_time, depart_airport_code, 
                 depart_time, price, active=True):
        self.user_id = user_id
        self.arrive_airport_code = arrive_airport_code
        self.arrive_time = arrive_time
        self.depart_airport_code = depart_airport_code
        self.depart_time = depart_time
        self.price = price
        self.active = active


def create_user_fav(data):
    """
        insert a record into user_favorites table, if it already exist, set active to True
        parameter shoule be dictionary with key='user_id', 'arrive_airport_code', 
                 'arrive_time', 'depart_airport_code', 'depart_time', 'price'
    """
    query = UserFavorite.query.filter_by(user_id = data['user_id'],arrive_airport_code=data['arrive_airport_code'],
                                         arrive_time = data['arrive_time'], depart_airport_code=data['depart_airport_code'],
                                         depart_time = data['depart_time']).first()
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
    query = UserFavorite.query.filter_by(user_id = data['user_id'],arrive_airport_code=data['arrive_airport_code'],
                                         arrive_time = data['arrive_time'], depart_airport_code=data['depart_airport_code'],
                                         depart_time = data['depart_time'] )
    query.update({"active": False})
    db.session.commit()

def get_user_fav(userID):
    """
        retrieve a user's favorite list by user ID.
    """
    query = UserFavorite.query.filter_by(user_id = userID, active=True).all()
    fav_list = []
    for item in query:
        fav = {}
        fav["arrive_airport"] = get_airport_detail(item.arrive_airport_code)['airport_name']
        fav["arrive_airport_code"] = item.arrive_airport_code
        fav["arrive_time"] = item.arrive_time.strftime("%Y-%m-%d %H:%M")
        fav["depart_airport"] = get_airport_detail(item.depart_airport_code)['airport_name']
        fav["depart_airport_code"] = item.depart_airport_code
        fav["depart_time"] = item.depart_time.strftime("%Y-%m-%d %H:%M")
        fav_list.append(fav)
    return fav_list