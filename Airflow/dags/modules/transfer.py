from bs4 import BeautifulSoup
import json, re
from datetime import datetime, timedelta
import pymysql.cursors
import os
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from dotenv import load_dotenv
from modules.cloud import download_from_s3

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
    INSERT INTO flights_domestic(%s) VALUES(%s)
    """ % (cols, val_cols)
    return sql

#0924 OK
def clean_data_richmond(filename):
    raw_data = download_from_s3(filename)
    date = filename.split("_")[0]
    version = filename.split("_")[-1]
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
            info["batch_version"] = version.split(".")[0]
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
    version = filename.split("_")[-1]
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
                    info["batch_version"] = version.split(".")[0]
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
    version = filename.split("_")[-1]
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
            info["batch_version"] = version.split(".")[0]           
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
    version = filename.split("_")[-1]
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
                info["batch_version"] = version.split(".")[0]
                total.append(info)
    sql = generate_sql(total)
    try:
        cursor.executemany(sql, total)
        connection.commit()
        print(f"Done. counts: {len(total)}, filename: {filename}")
    except Exception as e:
        print(f"Error: {e}, filename: {filename}")

