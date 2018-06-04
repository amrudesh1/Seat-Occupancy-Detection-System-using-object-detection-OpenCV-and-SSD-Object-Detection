import cv2
import urllib.request
import numpy as np
import time
import MySQLdb
from datetime import datetime

db = MySQLdb.connect("localhost","root","","occupancy")
cursor = db.cursor()

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

def program_effect():
    sql1 = "SELECT COUNT(*) FROM coordinates WHERE person=1"
    cursor.execute(sql1)
    results = cursor.fetchone()
    person_count=results[0]
    sql = "INSERT INTO audience_count VALUES(%s,%s)"
    data=(person_count,str(datetime.now()))
    cursor.execute(sql,data)
    db.commit()
    return

def control_signal():
    sql1="SELECT appliance FROM appliances"
    cursor.execute(sql1)
    results1 = cursor.fetchall()
    for row in results1:
        sql2="SELECT person FROM coordinates WHERE appliance=%s"
        data=(row[0],)
        cursor.execute(sql2,data)
        results2 = cursor.fetchall()
        for row in results2:
            if(row[0]==1):
                sql3="UPDATE appliances SET power=1"
                break
            else:
                sql3="UPDATE appliances SET power=0"
        cursor.execute(sql3)
        db.commit()
    return

counter=0
url='http://192.168.43.1:8080/shot.jpg'
program_effect()
while True:
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img_real=cv2.imdecode(imgNp,-1)
    sql = "SELECT * FROM coordinates"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        x1=row[0]
        y1=row[1]
        x2=row[2]
        y2=row[3]
        seat=row[6]
        crop_image= img_real[y1:y2, x1:x2]
        net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')
        (h, w) = crop_image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(crop_image, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.7:
                idx = int(detections[0, 0, i, 1])
                if CLASSES[idx]=="person":
                    print('HUMAN')
                    sql = "UPDATE coordinates SET person = 1 WHERE seatno=%s"
                    data=(seat,)
                    cursor.execute(sql,data)
                    db.commit()
                    break
                else:
                    sql = "UPDATE coordinates SET person = 0 WHERE seatno=%s"
                    data=(seat,)
                    cursor.execute(sql,data)
                    db.commit()
    control_signal()
    time.sleep(3.4)
    counter=counter+1
    if(counter==60):
        program_effect()
        counter=0
