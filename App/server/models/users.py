from server import db, login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from server.models.flight import get_airport_detail
from datetime import datetime, timedelta

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True)
    depart_airport_code = db.Column(db.String(3),primary_key = True)
    arrive_airport_code = db.Column(db.String(3), primary_key = True)
    depart_date = db.Column(db.DateTime(), primary_key=True)
    return_date = db.Column(db.DateTime(), primary_key=True)
    schedule = db.Column(db.String(20), primary_key=True)
    min_price = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    def __init__(self, user_id, depart_airport_code, arrive_airport_code,
                 depart_date, return_date, schedule, min_price, active=True):
        self.user_id = user_id
        self.depart_airport_code = depart_airport_code
        self.arrive_airport_code = arrive_airport_code
        self.depart_date = depart_date
        self.return_date = return_date
        self.schedule = schedule
        self.min_price = min_price
        self.active = active


def create_user_fav(data):
    """
        insert a record into user_favorites table, if it already exist, set active to True
        parameter shoule be dictionary with key='user_id', 'arrive_airport_code', 
                 'depart_airport_code', 'depart_date', 'return_date', 'schedule', 'min_price'
    """
    db.session.commit()
    query = UserFavorite.query.filter_by(user_id = data['user_id'],depart_airport_code=data['depart_airport_code'],
                                         arrive_airport_code = data['arrive_airport_code'], depart_date=data['depart_date'],
                                         return_date = data['return_date'], schedule=data['schedule']).first()
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
    query = UserFavorite.query.filter_by(user_id = data['user_id'],depart_airport_code=data['depart_airport_code'],
                                         arrive_airport_code = data['arrive_airport_code'], depart_date=data['depart_date'],
                                         return_date = data['return_date'], schedule=data['schedule'])
    
    query.update({"active": False})
    db.session.commit()

def get_utc_8_date():
    utc_date = datetime.utcnow()
    utc_8_date = utc_date + timedelta(hours=8)
    formatted_date = utc_8_date.strftime('%Y-%m-%d')
    return formatted_date

def get_user_fav(userID):
    """
        retrieve a user's favorite list by user ID.
    """
    db.session.commit()
    today = get_utc_8_date()
    query = UserFavorite.query.filter(UserFavorite.user_id == userID, UserFavorite.depart_date >= today, UserFavorite.active==True).all()
    fav_list = []
    for item in query:
        fav = {}
        fav["depart_city"] = get_airport_detail(item.depart_airport_code)['city_name']
        fav["arrive_city"] = get_airport_detail(item.arrive_airport_code)['city_name']
        fav["depart_airport_code"] = item.depart_airport_code
        fav["arrive_airport_code"] = item.arrive_airport_code
        fav["depart_date_formatted"] = item.depart_date.strftime("%Y年%m月%d日")
        fav["depart_date"] = item.depart_date.strftime("%Y-%m-%d")
        fav["schedule"] = item.schedule
        fav["return_date_formatted"] = item.return_date.strftime("%Y年%m月%d日") if item.schedule == "return" else None
        fav["return_date"] = item.return_date.strftime("%Y-%m-%d") if item.schedule == "return" else None
        fav["min_price"] = item.min_price
        fav_list.append(fav)
    return fav_list