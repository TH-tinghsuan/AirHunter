from server import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, login_required
from server.models.users import User, get_user_name
#from server.models.users import create_user, get_user_id


@app.route("/user/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account = request.values["account"]
        password = request.values["password"]
        user = User.query.filter_by(account=account).first()
        if user is None:
            flash("此帳號不存在", category="account")
            render_template("login.html")
        elif user is not None and user.check_password(password) == False:
            flash("密碼不正確", category="password")
            render_template("login.html")
        elif user.check_password(password) and user is not None:
            login_user(user)
            flash("您已成功登入！", category="success")
            return redirect(url_for('index'))
        
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("您已經成功登出")
    return redirect(url_for('index'))

@app.route("/user/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        account = request.values["account"]
        username = request.values["userName"]
        password = request.values["password"]
        user = User(account=account, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("您已成功註冊為會員！", category="register")
        return redirect(url_for('login'))
    return render_template("register.html")