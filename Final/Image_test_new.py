import cv2
import numpy as np
import MySQLdb
import os
from matplotlib import pyplot as plt

# MySQL database connection code
db = MySQLdb.connect("localhost","root","","occupancy")
cursor = db.cursor()
sql = "SELECT * FROM coordinates"
cursor.execute(sql)
results = cursor.fetchall()

#for loop for real time image accquisition should be given here
img_real = cv2.imread('images/example_002.jpg',0)

for row in results:
	
	img_ref=cv2.imread('images/example_02.jpg',0)
	crop_img_real = img_real[row[1]:row[3], row[0]:row[2]]
	crop_img_ref = img_ref[row[1]:row[3], row[0]:row[2]]
	img1 = cv2.Canny(crop_img_real,90,200)
	img2 = cv2.Canny(crop_img_ref,90,200)
	img3 = img2-img1
	ret,thresh = cv2.threshold(img3,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


	if ret > 0: #if any object is present on the seat
		
		#intilising the list of classes which need to be detected
		CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
		"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
		"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
		"sofa", "train", "tvmonitor"]
		COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
		
		#Loading Model From the Disk
		net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')
			
		#Acqusition of Image
		image = crop_img_real

		(h, w) = image.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

		#passing the blob and getting the value
		net.setInput(blob)
		detections = net.forward()	

		# loop over the detections
		for i in np.arange(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with the
			# prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence` is
			# greater than the minimum confidence
			if confidence > 0.2:
				# extract the index of the class label from the `detections`,
				# then compute the (x, y)-coordinates of the bounding box for
				# the object
				idx = int(detections[0, 0, i, 1])
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")
				
				if CLASS[idx]=="person":
					sql = "UPDATE coordinates SET status=1 , person = 1 where seatno=".row[6]
				else:
					sql = "UPDATE coordinates SET status=0 , person = 1 where seatno=".row[6]
				
				'''# display the prediction
				label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
				print("[INFO] {}".format(label))
				cv2.rectangle(image, (startX, startY), (endX, endY),
					COLORS[idx], 2)
				print (startX,startY,endX,endY)
				y = startY - 15 if startY - 15 > 15 else startY + 15
				cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)'''

	else: #if no object is present on the seat
		sql = "UPDATE coordinates SET status = 0 where seatno=".row[6]

	cursor.execute(sql)
	db.commit()

#cv2.imshow("Output", image)
#cv2.waitkey(0)

"""print (ret)
cv2.imshow("Edge1",img1)
cv2.imshow("Edge2",img2)
cv2.imshow("Edge3",img3)
"""


'''cv2.imshow("img_original",img_real)
cv2.imshow("img_real",crop_img_real)
cv2.imshow("img_ref",crop_img_ref)
'''
