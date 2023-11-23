import json
import time
import os
import logging
import pymysql.cursors
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

from airflow.models import Variable

from modules.cloud import download_from_s3, get_sqs_message_num

load_dotenv()

SEARCH_DATE = Variable.get("search_date_key")
date_obj = datetime.strptime(SEARCH_DATE, '%Y-%m-%d')
current_date = date_obj + timedelta(days=1)
DATE_LIST = [current_date.date() + timedelta(days=i) for i in range(61)]


logging.basicConfig(level=logging.INFO)
connection = pymysql.connect(host=os.getenv("DB_HOST"),
                             user=os.getenv("DB_USERNAME"),
                             password=os.getenv("DB_PASSWORD"),
                             database=os.getenv("DB_DATABASE"),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

def generate_sql(data_list):
    data = data_list[0]
    cols = ", ".join('`{}`'.format(k) for k in data.keys())
    val_cols = ', '.join('%({})s'.format(k) for k in data.keys())
    sql = """
    INSERT INTO flights_domestic_main(%s) VALUES(%s)
    """ % (cols, val_cols)
    return sql

def get_utc_8_date():
    utc_date = datetime.utcnow()
    utc_8_date = utc_date + timedelta(hours=8)
    formatted_date = utc_8_date.strftime('%Y-%m-%d')
    return formatted_date

def parse_raw_data_richmond(item: BeautifulSoup, date: str) -> dict:
    info = {}
    try:
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
        info["search_date"] = SEARCH_DATE
        return info
    except Exception as e:
        logging.error(f"error in parse_raw_data_richmond: {e}")

def clean_data_richmond():
    for date in DATE_LIST:
        filename = f"{date}_domestic_richmond_{SEARCH_DATE}.json"
        raw_data = download_from_s3(filename)
        date = filename.split("_")[0]
        total = []
        for d in raw_data["data"]:
            soup = BeautifulSoup(d, "html.parser")   
            flight_info = soup.find_all(class_="flight-wrap")      
            for item in flight_info:
                try:
                    info = parse_raw_data_richmond(item, date)
                    if info:
                        total.append(info)
                except:
                    logging.error(f"error when parsing richmond data: {e}")
        sql = generate_sql(total)
        sql_del = "DELETE FROM flights_domestic_main WHERE search_date=%s AND DATE(depart_time)=%s AND agentName=\"richmond\";"
        try:
            cursor.execute(sql_del, (SEARCH_DATE, date))
            cursor.executemany(sql, total)
            connection.commit()
            logging.info(f"Done. counts: {len(total)}, filename: {filename}")
        except Exception as e:
            connection.rollback()
            logging.info(f"Error: {e}, filename: {filename}")

def parse_raw_data_ezTravel(item: BeautifulSoup) -> dict:
    info ={}
    try:
        if (item["ageRestriction"] == "" and 
            item["FarePenalties"]["CityAllowed"] == "" and 
            item["FarePenalties"]["NationAllowed"] == ""):
            
            flightInfo = json.loads(item["selectedFlightInfo"])
            info["depart_airport_code"] = flightInfo["DepartureAirport"]["Code"]
            info["arrive_airport_code"] = flightInfo["ArrivalAirport"]["Code"]
            info["airlineName"] = flightInfo["Airline"]["Name"]
            info["flightCode"] = flightInfo["FlightNo"][2::]
            info["clsType"] = item["classType"]
            info["depart_time"] = flightInfo["GoTime"].replace("年", "-").replace("月", "-").replace("日", "")
            info["arrive_time"] = flightInfo["ToTime"].replace("年", "-").replace("月", "-").replace("日", "")
            info['price'] = item['priceWithTax']
            info["agentName"] = "ezTravel"
            info["search_date"] = SEARCH_DATE
            return info
    except Exception as e:
        logging.error(f"error in parse_raw_data_ezTravel: {e}")
    

def clean_data_ezTravel():
    for date in DATE_LIST:
        filename = f"{date}_domestic_ezTravel_{SEARCH_DATE}.json"
        raw_data = download_from_s3(filename)
        total = []
        for d in raw_data["data"]:
            for item in d["flightList"]:
                info ={}
                if item["crossDays"] == 0:
                    for i in item['seats']:
                        try:
                            info = parse_raw_data_ezTravel(i)
                            if info:    
                                total.append(info)
                        except Exception as e:
                            logging.error(f"error when parsing ezTravel data: {e}")   
        if total:
            sql = generate_sql(total)
            sql_del = "DELETE FROM flights_domestic_main WHERE search_date=%s AND DATE(depart_time)=%s AND agentName=\"ezTravel\";"
            try:
                cursor.execute(sql_del, (SEARCH_DATE, date))
                cursor.executemany(sql, total)
                connection.commit()
                logging.info(f"Done. counts: {len(total)}, filename: {filename}")
            except Exception as e:
                connection.rollback()
                logging.error(f"Error: {e}, filename: {filename}")
        else:
            logging.info(f"No data for filename: {filename}")

def parse_ezFly_element(d: dict, formatted_date: str, element: BeautifulSoup) -> dict:
    try:
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
            info["price"] = int(total_price[2])
        elif total_price[2] == None and total_price[0] != None:
            info["price"] = int(total_price[0])
        elif total_price[0] == None and total_price[2] == None:
            info["price"] = None
        else:
            info["price"] = int(min(total_price[0], total_price[2]))
        info["agentName"] = "ezFly"
        info["search_date"] = SEARCH_DATE         
        return info
    
    except Exception as e:
        logging.error(f"error in parse_ezFly_element: {e}")

def parse_raw_data_ezFly(raw_data: dict) -> dict:
    try:
        total = []
        for d in raw_data:
            date = d["date"]
            date_obj = datetime.strptime(date, "%Y%m%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            soup = BeautifulSoup(d["info"], "html.parser")
            elements = soup.find_all(class_="ticket")
            for element in elements[1::]:
                info = parse_ezFly_element(d, formatted_date, element)
                if info:
                    total.append(info)
        return total
    except Exception as e:
        logging.error(f"error in parse_raw_data_ezFly: {e}")


def clean_data_ezFly():
    for date in DATE_LIST:
        filename = f"{date}_domestic_ezFly_{SEARCH_DATE}.json"
        raw_data = download_from_s3(filename)
        total = parse_raw_data_ezFly(raw_data["data"])
        if total:
            sql = generate_sql(total)
            sql_del = "DELETE FROM flights_domestic_main WHERE search_date=%s AND DATE(depart_time)=%s AND agentName=\"ezFly\";"
            try:
                cursor.execute(sql_del, (SEARCH_DATE, date))
                cursor.executemany(sql, total)
                connection.commit()
                logging.info(f"Done. counts: {len(total)}, filename: {filename}")
            except Exception as e:
                connection.rollback()
                logging.error(f"Error: {e}, filename: {filename}")

def parse_raw_data_lifetour(item: dict) -> dict:
    info ={}
    try:
        info["depart_airport_code"] = item["Origin"]
        info["arrive_airport_code"] = item["Destination"]
        info["airlineName"] = item["AirlineName"]
        info["flightCode"] = item["Trips"][0]["SegmentList"][0]["FlightNumber"]
        info["clsType"] = item["Trips"][0]["SegmentList"][0]["CabinDesc"]
        info["depart_time"] = item["GoTime"][0:16].replace("T", " ")
        info["arrive_time"] = item["BackEndTime"][0:16].replace("T", " ")
        info["price"] = int(item["AdultPriceString"].replace(",", ""))
        info["agentName"] = "lifetour"
        info["search_date"] = SEARCH_DATE
        return info
    except Exception as e:
        logging.error(f"error in parse_raw_data_lifetour: {e}")


def clean_data_lifetour():
    for date in DATE_LIST:
        filename = f"{date}_domestic_lifeTour_{SEARCH_DATE}.json"
        raw_data = download_from_s3(filename)
        total = []
        for d in raw_data["data"]:
            if d["groupFareListCount"] != 0:
                total_flights = d["groupFareList"]
                for flights in total_flights:
                    for item in flights["GroupItineraryList"]:
                        info = parse_raw_data_lifetour(item)
                        if info:
                            total.append(info)
        sql = generate_sql(total)
        sql_del = "DELETE FROM flights_domestic_main WHERE search_date=%s AND DATE(depart_time)=%s AND agentName=\"lifeTour\";"
        try:
            cursor.execute(sql_del, (SEARCH_DATE, date))
            cursor.executemany(sql, total)
            connection.commit()
            logging.info(f"Done. counts: {len(total)}, filename: {filename}")
        except Exception as e:
            connection.rollback()
            logging.error(f"Error: {e}, filename: {filename}")


