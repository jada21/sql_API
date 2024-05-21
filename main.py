from fastapi import FastAPI, Body, Request, HTTPException, status
from fastapi.responses import Response, JSONResponse
from dotenv import load_dotenv
import os
import pymysql
import mysql.connector
import requests
import json
from datetime import datetime, timedelta, date
from urllib.parse import quote
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
db_password = os.getenv("db_password")

# Database connection details
host = '3.145.165.110'
port = 3306                         # Default MySQL port
user = 'root'
password = db_password
database = 'SheButton_Data'

apiKey = "9704054"
phoneNum = "18765883488"
apiKey2 = "1582004"
phoneNum2 = "18763081860"

status_flag = None

# Establish connection
try:
    my_db = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
    print("Connected to the database successfully!")
    
    # Execute SQL queries using the 'my_db' object
    # For example:
    # cursor = my_db.cursor()
    # cursor.execute("SELECT * FROM your_table")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)
except mysql.connector.Error as err:
    print("Error connecting to MySQL: ", err)

cursor = my_db.cursor()

app = FastAPI()    #["*"]
origins = ["*"]


app.add_middleware(                         #instance of middle ware class  
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],                   # HTTP request types like get, post etc. * means all of dem
    allow_headers=["*"],
)

global count 
count = 1
time_sent = datetime.now()

@app.get("/", status_code=200)  
async def welcome(request: Request):
    return ("jadas cool capstone")

@app.post("/data", status_code=201)
async def post_data(request: Request):
    data_object = await request.json()
    lat_input = data_object["lat"]
    str_lat = json.dumps(lat_input)
    lng_input = data_object["lng"]
    str_lng = json.dumps(lng_input)
    temp_input = data_object["temp"]
    str_temp = json.dumps(temp_input)
   
    sql = "INSERT INTO Sensor_Data2 (lat, lng, temp, time, message) VALUES ( %s, %s, %s, %s, %s)"
    current_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    current_time_dto = datetime.now()
    message_data = "HELP! " + "\nLat: " + str_lat + "\nLng: " + str_lng + "\nTemp: " + str_temp + "\nLink: " + "http://3.145.165.110/SheButtonJC.html"      #will only concatenate if data is posted as string
    val = (lat_input, lng_input, temp_input, current_time, message_data)
    cursor.execute(sql, val)
    my_db.commit()

    message_url = quote(message_data)   
    waURL = "https://api.callmebot.com/whatsapp.php?phone="+phoneNum + "&apikey=" + apiKey + "&text=" + message_url
    waURL2 = "https://api.callmebot.com/whatsapp.php?phone="+phoneNum2 + "&apikey=" + apiKey2 + "&text=" + message_url
    
    global status_flag
    global time_sent
    global count
    response1 = None
    response2 = None

    five_min =  timedelta(minutes=5)
    time_diff = current_time_dto - time_sent

    # print("Time Sent:", time_sent)
    # print("Current Time:", current_time_dto)
    # print("Time Difference:", time_diff)
    # print("count: ", count)

    if count >1:
        print("count is greater than 1, in subsequent loop")                                                            #for subsequent requests, check if 5 minutes has elapsed since last request before sending new message
        if time_diff >= five_min: 
            response1 = requests.post(waURL)
            response2 = requests.post(waURL2)
            time_sent = current_time_dto
            print("more than 5 min passed")
        
    else:                                                                   #for first request, send as normal
        response1 = requests.post(waURL)
        response2 = requests.post(waURL2)
        print("in first loop")
        time_sent = current_time_dto
    
    if response1 is not None and response2 is not None:                     #subsequent requests under 5 min threshold will have None for response value since WA message is not sent
        if response1.status_code == 200 and response2.status_code == 200:
            status_flag = 1
        else:
            status_flag = 0         #this part aint working fam....................................................
    
    count += 1
    return ("201 created")

@app.get("/website", status_code=200)  
async def get_data(request: Request):
    sql2 = "SELECT lat, lng, temp FROM Sensor_Data2 ORDER BY id DESC LIMIT 1"
    cursor.execute(sql2)
    results = cursor.fetchone()         #fetchall() would also work
    return results

@app.get("/data", status_code=200) 
async def get_data(request: Request):
    global status_flag
    status_grab = status_flag
    status_flag = None
    return {"status": status_grab}
   
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# finally:
#     if 'my_db' in locals() and my_db.is_connected():
#         my_db.close()
#         print("Connection closed.")
