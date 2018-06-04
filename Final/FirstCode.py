import numpy as np
import cv2
import MySQLdb
import urllib.request

def arrangeSeats():
	sql = "SELECT x1,y1,x2,y2 FROM temp_coord ORDER BY x1"
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		cursor.execute("INSERT INTO coordinates(x1,y1, x2, y2) VALUES (%s, %s, %s, %s)",
			(row[0],row[1],row[2],row[3]))
		db.commit()
	return

db = MySQLdb.connect("localhost","root","","occupancy")
cursor = db.cursor()

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

url='http://192.168.43.1:8080/shot.jpg'
imgResp=urllib.request.urlopen(url)
imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
image=cv2.imdecode(imgNp,-1)
cv2.imwrite("images/demo/seat_ref.jpg", image)
(h, w) = image.shape[:2]
blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)),
	 0.007843, (300, 300), 127.5)
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt',
	 'MobileNetSSD_deploy.caffemodel')
net.setInput(blob)
detections = net.forward()
for i in np.arange(0, detections.shape[2]):
	confidence = detections[0, 0, i, 2]
	if confidence > 0.2:
		idx = int(detections[0, 0, i, 1])
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")
		label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
		print("[INFO] {}".format(label))
		cv2.rectangle(image, (startX, startY), (endX, endY),
			COLORS[idx], 2)
		y = startY - 15 if startY - 15 > 15 else startY + 15
		cv2.putText(image, label, (startX, y),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
		if CLASSES[idx]=="chair":
			print(startX,startY,endX,endY)
			cursor.execute("INSERT INTO temp_coord(x1,y1, x2, y2)VALUES (%s, %s, %s, %s)",
				(startX,startY,endX,endY))
			db.commit()
arrangeSeats()
cv2.imshow("Output", image)
cv2.waitKey(0)