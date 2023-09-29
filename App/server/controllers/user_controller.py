from server import app, db
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from server.models.users import User, create_user_fav, del_user_fav, get_user_fav
import json

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

@app.route("/user/favorites/add", methods=["POST"])
def add_favorites():
    flights_info = request.get_json()
    main_info = {}
    main_info['user_id'] = current_user.get_id()
    main_info['arrive_airport_code'] = flights_info['arrive'].split(" ")[2]
    main_info['arrive_time'] = flights_info['arrive'].split(" ")[3] + " " + flights_info['arrive'].split(" ")[4]
    main_info['depart_airport_code'] = flights_info['depart'].split(" ")[2]
    main_info['depart_time'] = flights_info['depart'].split(" ")[3] + " " + flights_info['depart'].split(" ")[4]
    main_info['price'] = 2345
    create_user_fav(main_info)
    return "OK"

@app.route("/user/favorites/remove", methods=["POST"])
def del_favorites():
    flights_info  = request.get_json()
    main_info = {}
    main_info["user_id"] = current_user.get_id()
    main_info['arrive_airport_code'] = flights_info['arrive'].split(" ")[1]
    main_info['arrive_time'] = flights_info['arrive'].split(" ")[2] + " " + flights_info['arrive'].split(" ")[3]
    main_info['depart_airport_code'] = flights_info['depart'].split(" ")[1]
    main_info['depart_time'] = flights_info['depart'].split(" ")[2] + " " + flights_info['depart'].split(" ")[3]
    del_user_fav(main_info)
    return "OK"

@app.route("/user/member", methods=["GET"])
def member():
    return render_template("member.html")

@app.route("/user/favorites/get", methods=["GET"])
def get_favorites():
    userID = current_user.get_id()
    data = get_user_fav(userID)
    return json.dumps(data, ensure_ascii=False)

@app.route("/user/favorites", methods=["GET"])
def favorites_list():
    return render_template("favorite.html")