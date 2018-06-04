import cv2
import numpy as np
import MySQLdb
import time
import urllib.request
import threading
import datetime

def img_acquisition():
	url='http://192.168.43.1:8080/shot.jpg'
	imgResp=urllib.request.urlopen(url)
	imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
	img_real=cv2.imdecode(imgNp,-1)
	img_real = cv2.cvtColor(img_real, cv2.COLOR_BGR2GRAY)
	#cv2.imshow("RealImg",img_real);
	return img_real
    
def img_partitioning(img,x1,y1,x2,y2):
	crop_img=img[y1:y2, x1:x2]
	return crop_img
	
def edge_detection(img):
	edg_img=cv2.Canny(img,700,750)
	return edg_img
	
def img_subtraction(img1,img2):
	img3=img1-img2
	return img3

def def_ref_img():
	img_ref=cv2.imread('images/demo/seat_ref.jpg',cv2.IMREAD_GRAYSCALE)
	return img_ref
	
def programme_effect():
	threading.Timer(18000.0, programme_effect).start()
	currentDT = datetime.datetime.now()
	sql="SELECT COUNT(person) FROM coordinates WHERE person=1" 
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		cursor.execute("INSERT INTO audience_count(person_count,day,month,year,hour,minute,second) VALUES(%s,%s,%s,%s,%s,%s,%s)",(row[0], currentDT.day, 
			currentDT.month, currentDT.year, currentDT.hour, currentDT.minute, currentDT.second))
		db.commit()
	return

def control_signal():
	sql="SELECT person FROM coordinates"
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		if row[0]==1:
			sql="UPDATE appliances SET power=1 WHERE appliance='FL1'"
			break
		else:
			sql="UPDATE appliances SET power=0 WHERE appliance='FL1'"
	cursor.execute(sql)
	db.commit()
	return 

db = MySQLdb.connect(host="localhost",user="root",passwd="",db="occupancy")
cursor = db.cursor()
#programme_effect()
while True:
	img_real=img_acquisition()
	img_ref=def_ref_img()
	sql = "SELECT * FROM coordinates"
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		x1 = row[0]
		y1 = row[1]
		x2 = row[2]
		y2 = row[3]
		seat=row[6]
		crop_img_real = img_partitioning(img_real,x1,y1,x2,y2)
		crop_img_ref = img_partitioning(img_ref,x1,y1,x2,y2)
		img1 = edge_detection(crop_img_real)
		img2 = edge_detection(crop_img_ref)
		img3=img_subtraction(img1,img2)
		cv2.imwrite("images/demo/cropped.jpg", crop_img_real)
		ret,thresh = cv2.threshold(img3,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

		print (ret)

		if ret > 0:
			CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
				"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
				"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
				"sofa", "train", "tvmonitor"]
			COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
			net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt',
		        'MobileNetSSD_deploy.caffemodel')
			image = cv2.imread("images/demo/cropped.jpg")
			(h, w) = image.shape[:2]
			blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)),
				0.007843, (300, 300), 127.5)
			net.setInput(blob)
			detections = net.forward()
			for i in np.arange(0, detections.shape[2]):
				confidence = detections[0, 0, i, 2]
				if confidence > 0.1:
					idx = int(detections[0, 0, i, 1])
					box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
					(startX, startY, endX, endY) = box.astype("int")
					label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
					cv2.rectangle(image, (startX, startY), (endX, endY),COLORS[idx], 2)
					y = startY - 15 if startY - 15 > 15 else startY + 15
					cv2.putText(image, label, (startX, y),
						cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
					if CLASSES[idx]=="person":
						query="UPDATE coordinates SET status = 1 , person = 1 WHERE seatno=%s"
						data=(seat,)
						break
					else:
						query="UPDATE coordinates SET status = 1 , person = 0 WHERE seatno=%s"
						data=(seat,)
		else:
			query="UPDATE coordinates SET status = 0 , person = 0 WHERE seatno=%s"
			data=(seat,)
			print("nothing")
	cursor.execute(query,data)
	db.commit()
	control_signal()
	#cv2.waitKey(0)
	#if ord('q')==cv2.waitKey(10):
	#	query="UPDATE coordinates SET status = 0 , person = 0"
	#	cursor.execute(query)
	#	db.commit()
	#	query="UPDATE appliances SET power=0 WHERE appliance='FL1'"
	#	cursor.execute(query)
	#	db.commit()
	#	break
	#time.sleep(1)
