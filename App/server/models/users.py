from server import db, login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    # columns
    id       = db.Column(db.Integer, primary_key = True)
    account    = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64),unique=True, index=True)
    password = db.Column(db.String(128))
    def __init__(self, account, username, password):
        """初始化"""
        self.account = account
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        """檢查使用者密碼"""
        return bcrypt.check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_user_name(account):
    user = User.query.filter_by(account=account).first()
    return user.username