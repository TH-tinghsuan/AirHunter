import os
import logging
import pandas as pd
import pymysql.cursors
from datetime import datetime, timedelta
from dotenv import load_dotenv
from string import Template
from pathlib import Path

from airflow.models import Variable

from modules.notification import send_noti_email

load_dotenv()

logging.basicConfig(level=logging.INFO)
connection = pymysql.connect(host=os.getenv("DB_HOST"),
                             user=os.getenv("DB_USERNAME"),
                             password=os.getenv("DB_PASSWORD"),
                             database=os.getenv("DB_DATABASE"),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

# Compare the prices scraped this time with the prices scraped last time, 
# and if there is a difference, send an email notification to the user.
def get_old_price_history_data(**kwargs):
    """get old price history data before insert new data in table."""
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
        logging.info("get yesterday data", yesterday)
       
    else:
        old_df = pd.DataFrame.from_dict(data)
        logging.info("get today data", search_date)
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
        logging.error("An error occurred:", e)
        connection.rollback()

def compare_price_difference(**kwargs):
    """"Compare the price updated at different times on the same day."""
    sql_search = """select * from price_history where search_date = %s"""  
    search_date = Variable.get("search_date_key")  
    cursor.execute(sql_search, search_date)
    new_data = cursor.fetchall()
    new_df = pd.DataFrame.from_dict(new_data)

    ti = kwargs['ti']
    old_df = ti.xcom_pull(key='old_dataframe')

    compare_df = pd.merge(old_df, new_df, on=['depart_airport_code', 'arrive_airport_code', 'depart_date'], how='inner')
    compare_df["price_diff"] = compare_df['min_price_x'] - compare_df['min_price_y']
    filtered_data = compare_df.query('price_diff > 0')
    if filtered_data.empty != True:
        log_list = filtered_data[['depart_airport_code', 'arrive_airport_code','depart_date', 'min_price_x', 'min_price_y', 'search_date_x']].to_records(index=False)
        sql_log = """INSERT INTO price_history_logs(depart_airport_code, arrive_airport_code, depart_date, old_min_price, new_min_price, search_date, active) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
        try:
            cursor.executemany(sql_log, log_list)
            connection.commit()
            logging.info("done")
        except Exception as e:
            logging.info(f"error: {e}")  
    kwargs['ti'].xcom_push(key='noti_list', value=filtered_data)


def send_notification(**kwargs):
    ti = kwargs['ti']
    noti_list = ti.xcom_pull(key='noti_list')
    sql_track_list = """SELECT DISTINCT uf.depart_airport_code,
                                        uf.arrive_airport_code,
                                        uf.depart_date,
                                        uf.return_date,
                                        uf.schedule,
                                        u.id,
                                        u.account
                        FROM user_favorites uf
                        INNER JOIN user u ON uf.user_id = u.id
                        where uf.active = true and uf.schedule=\"oneWay\""""
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
            title = f"<價格提醒通知>{airports[item['depart_airport_code']]}-{airports[item['arrive_airport_code']]}機票已下跌{abs(item['price_diff'])}元" 
            template = Template(Path("/opt/airflow/dags/modules/email.html").read_text())
            body = template.substitute({ "depart": airports[item['depart_airport_code']], "arrive":airports[item['arrive_airport_code']], "date": date,  "price": abs(item['price_diff'])})
            send_noti_email(title, body, item['account'], is_html=True)
    else:
        logging.info("In the user's tracked flights, there are no price changes.")

# compare today's price with yesterday's, 
# if there's any change, store it in 'price_change' table
def get_price_history(search_date: str, depart_date: str) -> pd.DataFrame:
    sql = """select depart_airport_code, arrive_airport_code, DATE(depart_date) AS depart_date, min_price, search_date
            from price_history where search_date = %s and depart_date > %s"""
    cursor.execute(sql, (search_date, depart_date))
    data = cursor.fetchall()
    df = pd.DataFrame.from_dict(data)
    return df

def compare_price(df_today: pd.DataFrame, df_yesterday: pd.DataFrame) -> pd.DataFrame:
    compare_df = pd.merge(df_yesterday, df_today, on=['depart_airport_code', 'arrive_airport_code', 'depart_date'], how='inner')
    selected_compare_df = compare_df[['depart_airport_code', 'arrive_airport_code', 'depart_date', 'min_price_x', 'min_price_y', 'search_date_y']]
    selected_compare_df = selected_compare_df.rename(columns={'min_price_x':'yesterday_price', 'min_price_y':'today_price', 'search_date_y':'search_date'})
        
    selected_compare_df["change_range"] =  selected_compare_df['today_price'] -  selected_compare_df['yesterday_price']
    selected_compare_df["change_type"] =  selected_compare_df.apply(lambda row: "drop" if row["change_range"] < 0 else "raise", axis=1)

    filtered_df =  selected_compare_df.query("change_range != 0")
    filtered_df.loc[:, 'change_range'] = abs(filtered_df['change_range'])
    return filtered_df

def insert_to_price_change(price_change_list: list, search_date: str):
    try:
        sql_del = """DELETE FROM price_change WHERE search_date = %s"""
        cursor.execute(sql_del, search_date)
        connection.commit()

        sql = """INSERT INTO price_change (depart_airport_code, arrive_airport_code, 
                depart_date, today_price, yesterday_price, change_type, change_range, search_date) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.executemany(sql, price_change_list)
        connection.commit()
        logging.info(f"compare_price_by_date task done, total counts: {len(price_change_list)}")
    except Exception as e:
        logging.info(f"error in compare_price_by_date: {e}")


def compare_price_by_date():    
    search_date = Variable.get("search_date_key") 
    search_date_obj = datetime.strptime(search_date, '%Y-%m-%d')
    yesterday_date_obj = search_date_obj - timedelta(days=1)
    yesterday_date = yesterday_date_obj.strftime('%Y-%m-%d')
    
    df_today = get_price_history(search_date, search_date)
    df_yesterday = get_price_history(yesterday_date, search_date)
    
    price_change_list = compare_price(df_today, df_yesterday)[['depart_airport_code', 'arrive_airport_code', 'depart_date', 'today_price', 'yesterday_price', 'change_type', 'change_range', 'search_date']]
    price_change_list['search_date'] = price_change_list['search_date'].astype(str)
    price_change_list = price_change_list.to_records(index=False)
    price_change_list = price_change_list.tolist()

    if len(price_change_list) != 0:
        insert_to_price_change(price_change_list, search_date)
        logging.info(price_change_list) 
    else:
        logging.info(search_date, "no price change")

