import cv2
import numpy as np
import MySQLdb
import os
from matplotlib import pyplot as plt



db = MySQLdb.connect("localhost","root","","occupancy")
cursor = db.cursor()
sql = "SELECT x1,y1,x2,y2 FROM coordinates"
cursor.execute(sql)
results = cursor.fetchall()
for row in results:
	x1 = row[0]
	y1 = row[1]
	x2 = row[2]
	y2 = row[3]
img_real = cv2.imread('images/example_02.jpg',0)
img_ref=cv2.imread('images/example_03.jpg',0)
crop_img_real = img_real[y1:y2, x1:x2]
crop_img_ref = img_ref[y1:y2, x1:x2]
img1 = cv2.Canny(crop_img_real,90,200)
img2 = cv2.Canny(crop_img_ref,90,200)
img3=img2-img1
ret,thresh = cv2.threshold(img3,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
if ret > 0:
	sql = "UPDATE coordinates SET status = 1 where seatno=1"
	os.system("python objectdetect.py -i img_real.jpg -p MobileNetSSD_deploy.prototxt -m MobileNetSSD_deploy.caffemodel")

else:
	sql = "UPDATE coordinates SET status = 0 where seatno=1"


cursor.execute(sql)
db.commit()

"""print (ret)
cv2.imshow("Edge1",img1)
cv2.imshow("Edge2",img2)
cv2.imshow("Edge3",img3)
"""


'''cv2.imshow("img_original",img_real)
cv2.imshow("img_real",crop_img_real)
cv2.imshow("img_ref",crop_img_ref)
'''
