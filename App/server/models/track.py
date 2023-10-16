from server import db
import pandas as pd
from datetime import datetime, timedelta
from server.models.flight import get_airport_detail, check_data, get_utc_8_date
from sqlalchemy import desc


class PriceHistory(db.Model):
    __tablename__= "price_history"
    depart_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    arrive_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    depart_date = db.Column(db.DateTime(), primary_key=True, nullable=False)
    min_price = db.Column(db.Integer)
    search_date = db.Column(db.DateTime(), primary_key=True, nullable=False)
   

    def __init__(self, arrive_airport_code, 
                 depart_airport_code, depart_date, min_price, search_date):
        self.arrive_airport_code = arrive_airport_code
        self.depart_airport_code = depart_airport_code
        self.depart_date = depart_date
        self.min_price = min_price
        self.search_date= search_date

class PriceChange(db.Model):
    __tablename__= "price_change"
    depart_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    arrive_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    depart_date = db.Column(db.DateTime(), primary_key=True, nullable=False)
    today_price = db.Column(db.Integer)
    yesterday_price = db.Column(db.Integer)
    change_type = db.Column(db.String(20))
    change_range = db.Column(db.Integer)
    search_date = db.Column(db.DateTime(), primary_key=True, nullable=False)
   

    def __init__(self, arrive_airport_code, 
                 depart_airport_code, depart_date, today_price, yesterday_price,
                 change_type, change_range, search_date):
        self.arrive_airport_code = arrive_airport_code
        self.depart_airport_code = depart_airport_code
        self.depart_date = depart_date
        self.today_price = today_price
        self.yesterday_price = yesterday_price
        self.change_type = change_type
        self.change_range = change_range
        self.search_date= search_date

#查特定出發地＋目的地在不同出發日的最低價格
def get_price_trend():
    db.session.commit()
    today_date = get_utc_8_date()
    query = PriceHistory.query.filter(
                    PriceHistory.depart_date >= today_date,
                    PriceHistory.search_date == today_date
                )
    result = query.all()
    data_list = []
    for item in result:
        data = {}
        data['出發地'] = item.depart_airport_code
        data['目的地'] = item.arrive_airport_code
        data['出發日'] = item.depart_date
        data['最低價格'] = item.min_price
        data_list.append(data)
    df = pd.DataFrame.from_dict(data_list)
    return df

#查歷史紀錄
def get_price_record():
    db.session.commit()
    result = PriceHistory.query.all()
    data_list = []
    for item in result:
        data = {}
        data['出發地'] = item.depart_airport_code
        data['目的地'] = item.arrive_airport_code
        data['搜尋時間'] = item.search_date.date()
        data['最低價格'] = item.min_price
        data['出發日'] = item.depart_date
        data_list.append(data)
    df = pd.DataFrame.from_dict(data_list)
    return df

airports = {'MZG':'澎湖', 'KHH':'高雄', 'KNH':'金門', 
            'RMQ':'台中', 'TSA':'台北', 'TNN':'台南',
            'MFK':'馬祖', 'LZN':'馬祖(南竿)', 'TTT':'台東',
            'HUN':'花蓮', 'CYI':'嘉義'}

def get_price_change_data():
    check_if_exist_data = check_data()
    if check_if_exist_data == True:
         search_date = get_utc_8_date()
    else:
        date_str = get_utc_8_date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        search_date_obj = date_obj - timedelta(days=1)
        search_date = search_date_obj.strftime('%Y-%m-%d')
    
    db.session.commit()
    query = PriceChange.query.filter(
                    PriceChange.change_type == "drop",
                    PriceChange.change_range > 1,
                    PriceChange.search_date == search_date
                )
    query = query.order_by(desc(PriceChange.change_range))
    query = query.limit(4)
    result = query.all()
    price_change_list = []
    for item in result:
        data = {}
        data["arrive_airport"] = airports[item.arrive_airport_code]
        data["arrive_airport_code"] = item.arrive_airport_code
        data["depart_airport"] = airports[item.depart_airport_code]
        data["depart_airport_code"] = item.depart_airport_code
        data["depart_date"] = item.depart_date.strftime('%Y-%m-%d')
        data["image"] = get_airport_detail(item.arrive_airport_code)["image"]
        data["today_price"] = item.today_price
        data["yesterday_price"] = item.yesterday_price
        data["change_range"] = item.change_range
        cal_rate = abs(round((item.today_price-item.yesterday_price)/item.today_price, 2))
        data["change_rate"] = int(cal_rate * 100)
        price_change_list.append(data)
    return price_change_list


def get_map_data():
    db.session.commit()
    search_date_obj = datetime.strptime(get_utc_8_date(), "%Y-%m-%d")
    next_week_obj = search_date_obj + timedelta(weeks=1)
    depart_date = next_week_obj.strftime('%Y-%m-%d')
    query = PriceHistory.query.filter(
                    PriceHistory.depart_airport_code == "TSA",
                    PriceHistory.depart_date == depart_date,
                    PriceHistory.search_date == get_utc_8_date()
                )
    query = query.order_by(PriceHistory.min_price)
    query = query.limit(3)
    result = query.all()
    destination_list = []
    for item in result:
        data = {}
        data["arrive_airport"] = airports[item.arrive_airport_code]
        data["arrive_airport_code"] = item.arrive_airport_code
        data["depart_airport"] = airports[item.depart_airport_code]
        data["depart_airport_code"] = item.depart_airport_code
        data["depart_date"] = item.depart_date.strftime('%Y-%m-%d')
        data["price"] = item.min_price
        data["image"] = get_airport_detail(item.arrive_airport_code)["image"]
        destination_list.append(data)
    
    return destination_list