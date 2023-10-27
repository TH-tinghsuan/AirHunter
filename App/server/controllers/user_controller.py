import json

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from server import app, db
from server.models.users import User, create_user_fav, del_user_fav, get_user_fav

@app.route("/user/login", methods=["GET"])
def get_login():
    return render_template("login.html")

@app.route("/user/login", methods=["POST"])
def login():
    account = request.values["account"]
    password = request.values["password"]
    next_page = request.values["next"]
    user = User.query.filter_by(account=account).first()

    if user is None:
        flash("此帳號不存在", category="account")
        return render_template("login.html")
    elif user is not None and user.check_password(password) == False:
        flash("密碼不正確", category="password")
        return render_template("login.html")
    elif user.check_password(password) and user is not None:
        if not next_page:
            next_page = url_for("index")
        login_user(user)
        flash("您已成功登入！", category="success")
        return redirect(next_page)

@app.route("/user/signup", methods=["GET"])
def get_register():
    return render_template("register.html")

@app.route("/user/signup", methods=["POST"])
def register():
    account = request.values["account"]
    username = request.values["userName"]
    password = request.values["password"]
    user = User(account=account, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    flash("您已成功註冊為會員！", category="register")
    return redirect(url_for('login'))

@app.route('/user/logout')
@login_required
def logout():
    logout_user()
    flash("您已經成功登出")
    return redirect(url_for('index'))

@app.route("/user/favorites/add", methods=["POST"])
def add_favorites():
    flights_info = request.get_json()
    
    main_info = {}
    main_info['user_id'] = current_user.get_id()
    main_info['depart_airport_code'] = flights_info['departAirport']
    main_info['arrive_airport_code' ] = flights_info['arriveAirport']
    main_info['depart_date'] = flights_info['departDate']
    main_info['return_date'] = flights_info['returnDates'] if flights_info["schedule"] == "return" else "1970-01-01"
    main_info['min_price'] = flights_info['minPrice']
    main_info['schedule'] = flights_info["schedule"]
    
    create_user_fav(main_info)
    
    return jsonify({"message": "Favorite flight added successfully"})

@app.route("/user/favorites/remove", methods=["POST"])
def del_favorites():
    flights_info  = request.get_json()
    flights_info["user_id"] = current_user.get_id()
    if flights_info["return_date"] == None:
        flights_info["return_date"] = "1970-01-01"
    
    del_user_fav(flights_info)

    return jsonify({"message": "Favorite flight removed successfully"})


@app.route("/user/favorites/get", methods=["GET"])
def get_favorites():
    userID = current_user.get_id()
    data = get_user_fav(userID)
    return json.dumps(data, ensure_ascii=False)

@app.route("/user/favorites", methods=["GET"])
def favorites_list():
    if not current_user.is_authenticated:
        return render_template("login.html", next="/user/favorites")
    return render_template("favorite.html")