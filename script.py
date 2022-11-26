#================================== FIREBASE MODULE ==========================================#
import firebase_admin
from firebase_admin import credentials, db

#=================================== EMAIL MODULE =============================================#
from email.message import EmailMessage

import smtplib
import pyautogui
import imghdr

#==============================================================================================#
import pickle
import os.path
import time
from datetime import datetime

#================================= GOOGLE FIT MODULE ==========================================#
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#================================= ACCESS GOOGLE FIT ===========================================#
scopes = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
]

dataSourceId = {
    "steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
    "distance": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta",
    "calories" : "derived:com.google.calories.expended:com.google.android.gms:platform_calories_expended",
    "heart rate": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
    "move minutes": "derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes",
    "speed": "derived:com.google.speed:com.google.android.gms:merge_speed",
}

GoogleFit_credentials = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        GoogleFit_credentials = pickle.load(token)

if not GoogleFit_credentials or not GoogleFit_credentials.valid:
    if GoogleFit_credentials and GoogleFit_credentials.expired and GoogleFit_credentials.refresh_token:
        GoogleFit_credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'GoogleFit_credentials.json', scopes)
        GoogleFit_credentials = flow.run_console()

    with open('token.pickle', 'wb') as token:
        pickle.dump(GoogleFit_credentials, token)

fit = build('fitness', 'v1', credentials = GoogleFit_credentials)

#================================= ACCESS FIREBASE ===========================================#
Firebase_credentials = credentials.Certificate('Firebase_credentials.json')

firebase_admin.initialize_app(Firebase_credentials, {
    'databaseURL': "https://raspberrypi-health-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ref = db.reference('/')

#============================= FUNCTION UPDATE HEALTH DATA ====================================#
def updateData(key, valueType):
    currentTime = int(round(time.time() * 1000))

    requestBody = {
        'aggregateBy': [
            {
                'dataSourceId': dataSourceId[key]
            },
        ],

        "bucketByTime": {
            "period": 
            {
                "type": "day",
                "value": 1,
                "timeZoneId": "Asia/Ho_Chi_Minh"
            },
        },

        'startTimeMillis': 1668099600000,
        'endTimeMillis': currentTime
    }

    data = fit.users().dataset().aggregate(userId='me', body = requestBody).execute()

    dataValue = data['bucket'][-1]["dataset"][0]["point"][0]["value"][0][valueType]
    dataTime = data['bucket'][-1]["dataset"][0]["point"][0]["endTimeNanos"]

    dataTime = datetime.utcfromtimestamp((int(dataTime) + 25200000000000) // 1000000000)
    dateTime = dataTime.strftime('%Y-%m-%d %H:%M:%S')

    dataValue = round(float(dataValue), 1)

    new_ref = ref.child(key)

    new_ref.set({
        'time': dateTime,
        'value': dataValue
    })
    
    return dataValue

#============================== FUNCTION UPDATE HEART RATE ====================================#
def updateHeartRate():
    currentTime = int(round(time.time() * 1000))

    requestBody = {
        'aggregateBy': [
            {
                'dataSourceId': "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
            },
        ],

        "bucketByTime": {
            "period": 
            {
                "type": "day",
                "value": 1,
                "timeZoneId": "Asia/Ho_Chi_Minh"
            },
        },

        'startTimeMillis': currentTime - 10000,
        'endTimeMillis': currentTime
    }    

    data = fit.users().dataset().aggregate(userId='me', body = requestBody).execute()

    if data['bucket'][0]["dataset"][0]["point"]:
        # Data from Google Fits
        dataValue = data['bucket'][0]["dataset"][0]["point"][0]["value"][0]['fpVal']
        dataTime = data['bucket'][0]["dataset"][0]["point"][0]["endTimeNanos"]

        # Convert time nanos to datetime
        dataTime = datetime.utcfromtimestamp((int(dataTime) + 25200000000000) // 1000000000)
        dateTime = dataTime.strftime('%Y-%m-%d %H:%M:%S')

        heartRate = round(float(dataValue))

        print(heartRate)

        ref.update({
            'heart rate/value': heartRate,
            'heart rate/time': dateTime
        })

        #================================= SEND EMAIL WARNING ===================================#
        Sender_Email = "raspberrypi.health@gmail.com"
        Reciever_Email = "raspberrypi.health@gmail.com"
        Password = "kmjvoiexifzissnk"

        newMessage = EmailMessage()                         
        newMessage['Subject'] = "YOUR HEALTH DATA" 
        newMessage['From'] = Sender_Email                   
        newMessage['To'] = Reciever_Email                   
        newMessage.set_content(f' This is your health data today (image attachment).\n Your heart rate is {heartRate} (too high). You should meet the doctor for more advice') 

        time.sleep(5)


        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'C:\Users\Suu\Downloads\UET\Thesis\health.png')

        with open('health.png', 'rb') as f:
            image_data = f.read()
            image_type = imghdr.what(f.name)
            image_name = f.name

        newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

        if heartRate > 70:

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(Sender_Email, Password)              
                smtp.send_message(newMessage)

            print('Mail Sent successful')
        else:
            print("Mail Sent fail")
        
    return data

def main():

 #======================== UPDATE HEALTH DATA EVERY 10 SECONDS ================================#
    while True:
        print("UPDATING DATA...")
        
        updateData("steps", 'intVal')
        updateData("move minutes", 'intVal')
        updateData("distance", 'fpVal')
        updateData("calories", 'fpVal')
        updateData("speed", 'fpVal')
        updateHeartRate()

        time.sleep(1)

if __name__ == '__main__':
    main()