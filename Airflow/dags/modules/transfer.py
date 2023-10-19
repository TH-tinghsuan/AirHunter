from bs4 import BeautifulSoup
import json, re
from datetime import datetime, timedelta
import time
import pymysql.cursors
import os
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.sqs import SqsHook
from dotenv import load_dotenv
from modules.cloud import download_from_s3
from airflow.models import Variable
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from string import Template
from pathlib import Path

load_dotenv()

connection = pymysql.connect(host=os.getenv("DB_HOST"),
                             user=os.getenv("DB_USERNAME"),
                             password=os.getenv("DB_PASSWORD"),
                             database=os.getenv("DB_DATABASE"),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
#create cusor
cursor = connection.cursor()

def gernerate_batch_version(region):
    sql = "SELECT * FROM batch_version WHERE region = %s"
    cursor.execute(sql, region)
    catch = cursor.fetchone()
    if catch:
        old_version = catch["version"]
        old_date = old_version[:8]
        today_date = datetime.today().date().strftime("%Y%m%d")
        if today_date == old_date:
            new_version = old_version[:9] + str(int(catch["version"][9:]) + 1)
            sql = "UPDATE batch_version SET version = %s WHERE version = %s"
            cursor.execute(sql, (new_version, old_version))
            connection.commit()
            return new_version
        else:
            new_version = today_date + "B1"
            sql = "UPDATE batch_version SET version = %s WHERE version = %s"
            cursor.execute(sql, (new_version, old_version))
            connection.commit()
            return new_version

    else:
        today_date = datetime.today().date()
        version_date = today_date.strftime("%Y%m%d")
        batch_version = version_date + "B1"
        sql = "INSERT INTO batch_version (version, region) VALUES (%s, %s)"
        cursor.execute(sql, (batch_version, region))
        connection.commit()
        return batch_version

def generate_sql(data_list):
    data = data_list[0]
    cols = ", ".join('`{}`'.format(k) for k in data.keys())
    val_cols = ', '.join('%({})s'.format(k) for k in data.keys())
    sql = """
    INSERT INTO flights_domestic_temp(%s) VALUES(%s)
    """ % (cols, val_cols)
    return sql

def get_utc_8_date():
    utc_date = datetime.utcnow()
    utc_8_date = utc_date + timedelta(hours=8)
    formatted_date = utc_8_date.strftime('%Y-%m-%d')
    return formatted_date

#0924 OK
def clean_data_richmond(filename):
    raw_data = download_from_s3(filename)
    date = filename.split("_")[0]
    total = []
    for d in raw_data["data"]:
        soup = BeautifulSoup(d, "html.parser")   
        flight_info = soup.find_all(class_="flight-wrap")      
        for item in flight_info:
            info = {}
            dpt_arr_airport = item.find_all(class_="fw-7 mr-2")
            info["depart_airport_code"] = dpt_arr_airport[0].text
            info["arrive_airport_code"] = dpt_arr_airport[1].text
            info["airlineName"] = item.find(class_="airline").text.strip()
            info["flightCode"] = item.find(class_="flight-intro").text.split("-")[-1]
            info["clsType"] = item.find(class_="flight-intro").find_next_sibling("span").text.split("(")[0]
            dpt_arr_time = item.find_all(class_="flight-time")
            info["depart_time"] = date + " " + dpt_arr_time[0].text.strip()
            info["arrive_time"] = date + " " + dpt_arr_time[1].text.strip()
            info["price"] = item.find(class_="airplane-price").text.strip().replace(",", "").replace("NT$", "")
            info["agentName"] = "richmond"
            info["search_date"] = Variable.get("search_date_key")
            total.append(info)
    sql = generate_sql(total)
    try:
        cursor.executemany(sql, total)
        connection.commit()
        print(f"Done. counts: {len(total)}, filename: {filename}")
    except Exception as e:
        print(f"Error: {e}, filename: {filename}")

#0924 OK
def clean_data_ezTravel(filename):
    raw_data = download_from_s3(filename)
    total = []
    for d in raw_data["data"]:
        for item in d["flightList"]:
            info ={}
            if item["crossDays"] == 0:
                for i in item['seats']:
                  if i["ageRestriction"] == "" and i ["FarePenalties"]["CityAllowed"] == "" and i["FarePenalties"]["NationAllowed"] == "":
                    flightInfo = json.loads(i["selectedFlightInfo"])
                    info["depart_airport_code"] = flightInfo["DepartureAirport"]["Code"]
                    info["arrive_airport_code"] = flightInfo["ArrivalAirport"]["Code"]
                    info["airlineName"] = flightInfo["Airline"]["Name"]
                    info["flightCode"] = flightInfo["FlightNo"][2::]
                    info["clsType"] = i["classType"]
                    info["depart_time"] = flightInfo["GoTime"].replace("年", "-").replace("月", "-").replace("日", "")
                    info["arrive_time"] = flightInfo["ToTime"].replace("年", "-").replace("月", "-").replace("日", "")
                    info['price'] = i['priceWithTax']
                    info["agentName"] = "ezTravel"
                    info["search_date"] = Variable.get("search_date_key")
                    total.append(info)
    
    sql = generate_sql(total)
    try:
        cursor.executemany(sql, total)
        connection.commit()
        print(f"Done. counts: {len(total)}, filename: {filename}")
    except Exception as e:
        print(f"Error: {e}, filename: {filename}")
    
#0924 OK
def clean_data_ezFly(filename):
    raw_data = download_from_s3(filename)
    total = []
    for d in raw_data["data"]:
        date = d["date"]
        date_obj = datetime.strptime(date, "%Y%m%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        soup = BeautifulSoup(d["info"], "html.parser")
        elements = soup.find_all(class_="ticket")

        for element in elements[1::]:
            info ={}
            info["depart_airport_code"] = d["depart"]
            info["arrive_airport_code"] = d["arrive"]
            info["airlineName"] = element.find("img").find_next_sibling(string=True)+"航空"
            info["flightCode"] = element.find(class_="airline").find(class_="flightcode").text.strip()
            dpt_arr_time = element.find(class_="time").text.strip()
            info["depart_time"] = formatted_date +" "+ dpt_arr_time.split("\n")[0].strip()
            info["arrive_time"] = formatted_date +" "+ dpt_arr_time.split("\n")[-1].strip()
            ticket_prices = element.find_all(class_="pick")
            total_price = []
            for item in ticket_prices:
                data = item.text.strip().split("\n")
                if data[0] == "------" or data[-1] == "停止售票":
                    total_price.append(None)
                    total_price.append(None)
                else:
                    total_price.append(data[0].replace(",", "").replace("元", ""))
                    total_price.append(data[-1].strip().replace("餘", "").replace("位", ""))
            
            if total_price[0] == None and total_price[2] != None:
                info["price"] = total_price[2]
            elif total_price[2] == None and total_price[0] != None:
                info["price"] = total_price[0]
            elif total_price[0] == None and total_price[2] == None:
                info["price"] = None
            else:
                info["price"] = min(total_price[0], total_price[2]) 
            info["agentName"] = "ezFly"
            info["search_date"] = Variable.get("search_date_key")           
            total.append(info)

    sql = generate_sql(total)
    try:
        cursor.executemany(sql, total)
        connection.commit()
        print(f"Done. counts: {len(total)}, filename: {filename}")
    except Exception as e:
        print(f"Error: {e}, filename: {filename}")

#0924 OK
def clean_data_lifetour(filename):
    raw_data = download_from_s3(filename)
    total = []
    for d in raw_data["data"]:
       if d["groupFareListCount"] != 0:
        total_flights = d["groupFareList"]
        for flights in total_flights:
            for item in flights["GroupItineraryList"]:
                info ={}
                info["depart_airport_code"] = item["Origin"]
                info["arrive_airport_code"] = item["Destination"]
                info["airlineName"] = item["AirlineName"]
                info["flightCode"] = item["Trips"][0]["SegmentList"][0]["FlightNumber"]
                info["clsType"] = item["Trips"][0]["SegmentList"][0]["CabinDesc"]
                info["depart_time"] = item["GoTime"][0:16].replace("T", " ")
                info["arrive_time"] = item["BackEndTime"][0:16].replace("T", " ")
                info["price"] = item["AdultPriceString"].replace(",", "")
                info["agentName"] = "lifetour"
                info["search_date"] = Variable.get("search_date_key")
                total.append(info)
    sql = generate_sql(total)
    try:
        cursor.executemany(sql, total)
        connection.commit()
        print(f"Done. counts: {len(total)}, filename: {filename}")
    except Exception as e:
        print(f"Error: {e}, filename: {filename}")

load_dotenv()
AWS_CONN_ID = os.getenv("AWS_CONN_ID")
queueUrl = os.getenv("QUEUE_URL")

def get_sqs_message_num(**kwargs):
    conn = SqsHook(aws_conn_id=AWS_CONN_ID, region_name="ap-southeast-2")
    sqs_hook_client = conn.get_conn()
    response = sqs_hook_client.get_queue_attributes(
                QueueUrl=queueUrl,
                AttributeNames=['ApproximateNumberOfMessages']
                )
    print(response)
    approximate_number_of_messages = int(response['Attributes']['ApproximateNumberOfMessages'])
    return approximate_number_of_messages

def insert_to_main_table():
    search_date = Variable.get("search_date_key")    
    print(search_date)
    messages = get_sqs_message_num()
    print(f"佇列中有 {messages} 則訊息。")
    if messages > 0:
        print(f"start to sleep {60*messages}")
        time.sleep(30*messages)
    else:
        print("sleep for 2 minutes, waiting transfer job complete.")
        time.sleep(120)

    sql_drop = """DELETE FROM flights_domestic_main WHERE search_date = %s"""
    sql_insert = """INSERT INTO flights_domestic_main SELECT * FROM flights_domestic_temp as t
                WHERE DATE(t.search_date) = %s"""
    sql_clear_temp = """TRUNCATE TABLE flights_domestic_temp"""
    try:
        cursor.execute(sql_drop, search_date)
        connection.commit()
        cursor.execute(sql_insert, search_date)
        connection.commit()
        cursor.execute(sql_clear_temp)
        connection.commit()
        print("Done.")
    except Exception as e:
        print("An error occurred:", e)
        connection.rollback()

def get_old_price_history_data(**kwargs):
    search_date = Variable.get("search_date_key")
    sql_search = """select * from price_history where search_date = %s"""
    cursor.execute(sql_search, search_date)
    data = cursor.fetchall()
    if not data:
        search_date_obj = datetime.strptime(search_date, "%Y-%m-%d")
        yesterday_obj = search_date_obj - timedelta(days=1)
        yesterday = yesterday_obj.strftime("%Y-%m-%d")
        sql_search_yesterday = """select * from price_history where search_date = %s"""
        cursor.execute(sql_search_yesterday, yesterday)
        data_yesterday = cursor.fetchall()
        old_df = pd.DataFrame.from_dict(data_yesterday)
        print("get yesterday data", yesterday)
       
    else:
        old_df = pd.DataFrame.from_dict(data)
        print("get today data", search_date)
    kwargs['ti'].xcom_push(key='old_dataframe', value=old_df)

def insert_to_price_history(**kwargs):
    search_date = Variable.get("search_date_key")
    sql = """INSERT INTO price_history (depart_airport_code, arrive_airport_code, depart_date, min_price, search_date)
          SELECT * FROM (SELECT depart_airport_code, arrive_airport_code, DATE(depart_time) AS depart_date, min(price) AS min_price,  DATE(search_date) AS search_date
          FROM flights_domestic_main where price is not null and search_date = %s
          GROUP BY depart_airport_code, arrive_airport_code, DATE(depart_date), DATE(search_date)) AS new
          ON DUPLICATE KEY UPDATE min_price=new.min_price;"""
    try: 
        cursor.execute(sql, search_date)
        connection.commit()
        print("Done")
    except Exception as e:
        print("An error occurred:", e)
        connection.rollback()

def compare_price_by_date():
    """Compare today and yesterday's prices, if any changes, store in tables, which will offer data to front-end(main_page)."""
    search_date = Variable.get("search_date_key") 
    search_date_obj = datetime.strptime(search_date, '%Y-%m-%d')
    yesterday_date_obj = search_date_obj - timedelta(days=1)
    yesterday_date = yesterday_date_obj.strftime('%Y-%m-%d')
    sql = """select depart_airport_code, arrive_airport_code, DATE(depart_date) AS depart_date, min_price, search_date
            from price_history where search_date = %s and depart_date > %s"""
    cursor.execute(sql, (search_date, search_date))
    today_data = cursor.fetchall()
    df_today = pd.DataFrame.from_dict(today_data)
    cursor.execute(sql, (yesterday_date, search_date))
    yesterday_data = cursor.fetchall()
    df_yesterday = pd.DataFrame.from_dict(yesterday_data)
    compare_df = pd.merge(df_yesterday, df_today, on=['depart_airport_code', 'arrive_airport_code', 'depart_date'], how='inner')
    selected_compare_df = compare_df[['depart_airport_code', 'arrive_airport_code', 'depart_date', 'min_price_x', 'min_price_y', 'search_date_y']]
    selected_compare_df = selected_compare_df.rename(columns={'min_price_x':'yesterday_price', 'min_price_y':'today_price', 'search_date_y':'search_date'})
        
    selected_compare_df["change_range"] =  selected_compare_df['today_price'] -  selected_compare_df['yesterday_price']
    def condition_type(row):
        if row["change_range"] < 0:
            return "drop"
        elif row["change_range"] > 0:
            return "raise"
    selected_compare_df["change_type"] =  selected_compare_df.apply(condition_type, axis=1)
    filterd_df =  selected_compare_df.query("change_range != 0")
    filterd_df['change_range'] = abs(filterd_df['change_range'])
    price_change_dict = filterd_df.to_dict(orient="records")
    price_change_list = []
    for i in price_change_dict:
        data = (i['depart_airport_code'], i['arrive_airport_code'], i['depart_date'], i['today_price'], i['yesterday_price'], i['change_type'], i['change_range'], i['search_date'])
        price_change_list.append(data)
    if price_change_list:
        sql_del = """DELETE FROM price_change WHERE search_date = %s"""
        cursor.execute(sql_del, search_date)
        connection.commit()
        sql = """INSERT INTO price_change (depart_airport_code, arrive_airport_code, 
                depart_date, today_price, yesterday_price, change_type, change_range, search_date) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.executemany(sql, price_change_list)
        connection.commit()
        print(f"done, total counts: {len(price_change_list)}")
    else:
        print(search_date, "no price change")


def compare_price_difference(**kwargs):
    sql_search = """select * from price_history where search_date = %s"""  
    search_date = Variable.get("search_date_key")  
    cursor.execute(sql_search, search_date)
    new_data = cursor.fetchall()
    new_df = pd.DataFrame.from_dict(new_data)
    ti = kwargs['ti']
    old_df = ti.xcom_pull(key='old_dataframe')
    # test
    print(f"old_df {old_df.columns}")
    print(f"new_df {new_df.columns}")
    compare_df = pd.merge(old_df, new_df, on=['depart_airport_code', 'arrive_airport_code', 'depart_date'], how='inner')
    compare_df["price_diff"] = compare_df['min_price_x'] - compare_df['min_price_y']
    filtered_data = compare_df.query('price_diff > 0')
    if  filtered_data.empty != True:   
        filtered_data_dict =  filtered_data.to_dict(orient="records")
        log_list = []
        for i in filtered_data_dict:
            print(i)
            log = (i['depart_airport_code'], i['arrive_airport_code'], i['depart_date'], i['min_price_x'], i['min_price_y'], i['search_date_x'], True)
            log_list.append(log)
        sql_log = """INSERT INTO price_history_logs(depart_airport_code, arrive_airport_code, depart_date, old_min_price, new_min_price, search_date, active) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
        cursor.executemany(sql_log, log_list)
    kwargs['ti'].xcom_push(key='noti_list', value=filtered_data)
    compare_price_by_date()

def send_email(depart, arrive, date, price, email):
    content = MIMEMultipart() 

    content["subject"] = f"<價格提醒通知>{depart}-{arrive}機票已下跌{price}元" 
    content["from"] = "airhunter.biz@gmail.com"  #寄件者
    content["to"] = email #收件者
    
    template = Template(Path("/opt/airflow/dags/modules/email.html").read_text())
    body = template.substitute({ "depart": depart, "arrive":arrive, "date": date,  "price": price})
    content.attach(MIMEText(body, "html"))

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("airhunter.biz@gmail.com", os.getenv("GOOGLE_EMAIL"))  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print(f"Complete!, email: {email}")
        except Exception as e:
            print("Error message: ", e)

def send_notification(**kwargs):
    ti = kwargs['ti']
    noti_list = ti.xcom_pull(key='noti_list')
    print(noti_list)
    sql_track_list = """SELECT DISTINCT uf.depart_airport_code,
                                        uf.arrive_airport_code,
                                        uf.depart_date,
                                        uf.return_date,
                                        uf.schedule,
                                        u.id,
                                        u.account
                        FROM user_favorites uf
                        INNER JOIN user u ON uf.user_id = u.id
                        where uf.active = true;"""
    cursor.execute(sql_track_list)
    data = cursor.fetchall()
    df = pd.DataFrame.from_dict(data)
    compare_df = pd.merge(df, noti_list, on=['depart_airport_code', 'arrive_airport_code', 'depart_date'], how='inner')
    airports = {'MZG':'澎湖', 'KHH':'高雄', 'KNH':'金門', 
            'RMQ':'台中', 'TSA':'台北', 'TNN':'台南',
            'MFK':'馬祖', 'LZN':'馬祖(南竿)', 'TTT':'台東',
            'HUN':'花蓮', 'CYI':'嘉義'}
    if compare_df.empty != True:
        user_list = compare_df.to_dict(orient="records")
        for item in user_list:
            date = item['depart_date'].strftime("%Y年%m月%d日")
            send_email(airports[item['depart_airport_code']], airports[item['arrive_airport_code']], date, abs(item['price_diff']), item['account'])

