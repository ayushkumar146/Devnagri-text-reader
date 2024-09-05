# -*- coding: utf-8 -*-
"""Blues.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yxbv_xM3Hn9_BaI9kOAHd36uSDycC7tw
"""

import numpy as np
import cv2
from google.colab.patches import cv2_imshow
from random import randint
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import confusion_matrix
import itertools
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from tensorflow import keras
import tensorflow.keras as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation , Dense , Flatten , BatchNormalization , Dropout, Conv2D,MaxPool2D
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import imagenet_utils
import shutil
import random
from keras.callbacks import ModelCheckpoint

def sort_contours(cnts,i):
    reverse = False
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
    key=lambda b:b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return (cnts)

def word_segment(img):
  #--------------------------Image Processing----------------------------#
  kernel=np.array((5,5),np.uint8)
  img2 = cv2.medianBlur(img,5)
    
  imgfn = cv2.adaptiveThreshold(img2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV, 199, 5)

  height=imgfn.shape[0]
  width=imgfn.shape[1]

  plol=imgfn[int (height*.02):int (height*.98),int (width*.02):int (width*.98)]
  img3=img[int (height*.02):int (height*.98),int (width*.02):int (width*.98)]


  noise=(plol.shape[0]*plol.shape[1])/1000

  ret, binary_map = cv2.threshold(plol,127,255,0)
  # do connected components processing
  nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, None, None, None, 8, cv2.CV_32S)
  #get CC_STAT_AREA component as stats[label, COLUMN] 
  areas = stats[1:,cv2.CC_STAT_AREA]

  dn2_img = np.zeros((labels.shape), np.uint8)

  for i in range(0, nlabels - 1):
      if areas[i] >=noise :   #keep
          dn2_img[labels == i + 1] = 255

  #------------------------------------------------------------------------#


  #---------------------------ROTATION CORRECTNESS-------------------------#

  #finding the angle at which the image is present
  coords = np.column_stack(np.where(dn2_img > 0))
  angle = cv2.minAreaRect(coords)[-1]
  if angle < -45:
    angle = -(90 + angle)
  else:
    angle = -angle

  #rotating the image around the centre with the angle from above
  (h, w) = dn2_img.shape[:2]
  center = (w // 2, h // 2)
  M = cv2.getRotationMatrix2D(center, angle, 1.0)
  dn2_img=cv2.bitwise_not(dn2_img)
  rot_img = cv2.warpAffine(dn2_img, M, (w, h),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
  img3 = cv2.warpAffine(img3, M, (w, h),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
  #------------------------------------------------------------------------#

  
  #for line detection
  xt=rot_img
  xt=cv2.bitwise_not(rot_img)
  kernel = np.ones((1, 1), np.uint8)
  est=cv2.erode(xt,kernel)
  
  kernel = np.ones((5, 100), np.uint8)
  pit=cv2.dilate(xt,kernel)

  #for line detection
  ctrs,_ = cv2.findContours(pit.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  #ctrs,_= cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  ctrs=sort_contours(ctrs,1)
     
  lines=[]
  legs=[]
  for d, ctr in enumerate(ctrs):
      # Get bounding box
      x, y, w, h = cv2.boundingRect(ctr)
      
      
      # Getting ROI
    
  
      roi = img3[y:y+h, x:x+w]
      roi2=rot_img[y:y+h, x:x+w]
      roi2=cv2.bitwise_not(roi)


      legs.append(roi)
      lines.append(roi2)

      cv2.rectangle(pit,(x,y),( x + w, y + h ),(90,0,255),2)


  lines=tuple(lines)
  legs=tuple(legs)
  chara=[]
  for i,imgs in enumerate(lines):
      ret, imgx = cv2.threshold(imgs, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
      #imgx=cv2.bitwise_not(imgx)    
      kernel = np.ones((1, 1), np.uint8)
      ero=cv2.erode(imgx,kernel)
      
      kernel = np.ones((5, 9), np.uint8)
      dil=cv2.dilate(ero,kernel)
      
      cv2.waitKey(0)
      cv2.destroyAllWindows()
      
      ctrs,_= cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
      ctrs=sort_contours(ctrs,0)
      print(i)

      for d, ctr in enumerate(ctrs):
          # Get bounding box
          x, y, w, h = cv2.boundingRect(ctr)

          # Getting ROI

          bru=legs[i]
          roi = imgs[y:y+h, x:x+w]
          roi2=bru[y:y+h, x:x+w]

          chara.append(roi2)

  
  chara=tuple(chara)
  words=chara[0]
  Marea=words.shape[0]*words.shape[1]
  for word in chara:
    if Marea<word.shape[0]*word.shape[1]:
      Marea=word.shape[0]*word.shape[1]
  charac=list()

  for word in chara:
    if word.shape[0]*word.shape[1]>.05*Marea:
      charac.append(word)


  charac=tuple(charac)
  return charac

def segment(img):
  # img=cv2.imread("/content/drive/MyDrive/mosaic_2/Images/teri to.jpeg" , 1)
  # cv2_imshow(img)
  # print(img.shape)
  # cv2_imshow(img)
  # kernel1 = np.ones((3,3) , 'uint8')
  # kernel2 = np.ones((3,3) , 'uint8')
  # img2=cv2.dilate(img,kernel1,iterations=1)
  # img3=cv2.erode(img,kernel2,iterations=1)
  # cv2_imshow(img2)
  # cv2_imshow(img3)
  
  # # Read image 
  # # img = cv2.imread('lanes.jpg', cv2.IMREAD_COLOR) # road.png is the filename
  # # Convert the image to gray-scale
  # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  # # Find the edges in the image using canny detector
  # edges = cv2.Canny(gray, 50, 100)
  # cv2_imshow(edges)
  # # Detect points that form a line
  # lines = cv2.HoughLinesP(edges, 1, np.pi/180, 120 , minLineLength=10, maxLineGap=250)
  # # Draw lines on the image
  # # for line in lines:
  # x1, y1, x2, y2 = lines[0][0]
  # print(x2-x1)
  # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
  # # Show result
  # cv2_imshow( img)
  #img=cv2.imread("/content/WhatsApp Image 2021-04-09 at 1.48.08 AM.jpeg" , 1)

  #img=cv2.imread("/content/WhatsApp Image 2021-04-09 at 1.48.08 AM.jpeg" , 1)
  #cv2_imshow(img)
  for i in range(3):
    img2 = cv2.medianBlur(img, 3 )
  # cv2_imshow(img2)
  # img3 = cv2.GaussianBlur(img, 3 , iterations=4)
  #cv2_imshow(img2)

  # rgb_planes = cv2.split(img2)

  # result_planes = []
  # result_norm_planes = []
  # for plane in rgb_planes:
  #     dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
  #     bg_img = cv2.medianBlur(dilated_img, 21)
  #     diff_img = 255 - cv2.absdiff(plane, bg_img)
  #     norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
  #     result_planes.append(diff_img)
  #     result_norm_planes.append(norm_img)

  # result = cv2.merge(result_planes)
  # result_norm = cv2.merge(result_norm_planes)

  # cv2_imshow(result)

  # cv2.imwrite('shadows_out.png', result)
  # cv2.imwrite('shadows_out_norm.png', result_norm)?

  # img = cv2.imread('/content/drive/MyDrive/mosaic_2/Images/bakat.jpeg',0)
  # edges = cv2.Canny(img,50,100)

  # plt.subplot(121),plt.imshow(img,cmap = 'gray')
  # plt.title('Original Image'), plt.xticks([]), plt.yticks([])
  # plt.subplot(122),plt.imshow(edges,cmap = 'gray')
  # plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

  # # plt.show()
  # cv2_imshow(edges)

  #gray_img=cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
  gray_img=img
  #cv2_imshow(gray_img)

  # #denoising 

  # dn_img=cv2.fastNlMeansDenoising(gray_img);
  # cv2_imshow(dn_img)
  # #= cv.fastNlMeansDenoisingMulti(noisy, 2, 5, None, 4, 7, 35)

  #ret, bw_img = cv2.threshold(gray_img, 140, 255, cv2.THRESH_BINARY)
  bw_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV, 199, 5)
  #cv2_imshow(bw_img)

  # th, th_img = cv2.threshold(bw_img, 220, 255, cv2.THRESH_BINARY_INV) 
  # cv2_imshow(th_img) #"Thresholded Image Binary inverse", 
  # print(th_img.shape)

  #ALWAYS REMEMBER THAT THE TOTAL WORD HAS TO BE CONNECTED BY A LINE

  noise=(bw_img.shape[0]*bw_img.shape[1])/1000
  #print(noise)

  ret, binary_map = cv2.threshold(bw_img,127,255,0)

  # do connected components processing
  nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, None, None, None, 8, cv2.CV_32S)

  #get CC_STAT_AREA component as stats[label, COLUMN] 
  areas = stats[1:,cv2.CC_STAT_AREA]

  dn2_img = np.zeros((labels.shape), np.uint8)

  for i in range(0, nlabels - 1):
      if areas[i] >= noise:   #keep
          dn2_img[labels == i + 1] = 255
  #cv2_imshow(dn2_img)  #"Result",

  #ROTATION CORRECTNESS

  #finding the angle at which the image is present
  coords = np.column_stack(np.where(dn2_img > 0))
  angle = cv2.minAreaRect(coords)[-1]
  if angle < -45:
    angle = -(90 + angle)
  else:
    angle = -angle

  #rotating the image around the centre with the angle from above
  (h, w) = dn2_img.shape[:2]
  center = (w // 2, h // 2)
  M = cv2.getRotationMatrix2D(center, angle, 1.0)
  rot_img = cv2.warpAffine(dn2_img, M, (w, h),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

  #cv2_imshow(rot_img)

  def crop_image(img,tol=0):
      # img is 2D image data
      # tol  is tolerance
      mask = img>tol
      return img[np.ix_(mask.any(1),mask.any(0))]

  crop_img=crop_image(rot_img)
  #cv2_imshow(crop_img)

  #print(crop_img.shape)

  resize_parm=(800/crop_img.shape[1])
  resize_width=(int)(resize_parm*crop_img.shape[1])
  resize_height=(int)(resize_parm*crop_img.shape[0])
  crop_img = cv2.resize(crop_img , (resize_width, resize_height))

  #print(crop_img.shape)

  #cv2_imshow(crop_img)


def segment(img):
    # img=cv2.imread("/content/drive/MyDrive/mosaic_2/Images/teri to.jpeg" , 1)
    # cv2_imshow(img)
    # print(img.shape)
    # cv2_imshow(img)
    # kernel1 = np.ones((3,3) , 'uint8')
    # kernel2 = np.ones((3,3) , 'uint8')
    # img2=cv2.dilate(img,kernel1,iterations=1)
    # img3=cv2.erode(img,kernel2,iterations=1)
    # cv2_imshow(img2)
    # cv2_imshow(img3)

    # # Read image
    # # img = cv2.imread('lanes.jpg', cv2.IMREAD_COLOR) # road.png is the filename
    # # Convert the image to gray-scale
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # # Find the edges in the image using canny detector
    # edges = cv2.Canny(gray, 50, 100)
    # cv2_imshow(edges)
    # # Detect points that form a line
    # lines = cv2.HoughLinesP(edges, 1, np.pi/180, 120 , minLineLength=10, maxLineGap=250)
    # # Draw lines on the image
    # # for line in lines:
    # x1, y1, x2, y2 = lines[0][0]
    # print(x2-x1)
    # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
    # # Show result
    # cv2_imshow( img)

    # cv2_imshow(img)
    for i in range(3):
        img2 = cv2.medianBlur(img, 3)
    # cv2_imshow(img2)
    # img3 = cv2.GaussianBlur(img, 3 , iterations=4)
    # cv2_imshow(img2)

    # rgb_planes = cv2.split(img2)

    # result_planes = []
    # result_norm_planes = []
    # for plane in rgb_planes:
    #     dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
    #     bg_img = cv2.medianBlur(dilated_img, 21)
    #     diff_img = 255 - cv2.absdiff(plane, bg_img)
    #     norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    #     result_planes.append(diff_img)
    #     result_norm_planes.append(norm_img)

    # result = cv2.merge(result_planes)
    # result_norm = cv2.merge(result_norm_planes)

    # cv2_imshow(result)

    # cv2.imwrite('shadows_out.png', result)
    # cv2.imwrite('shadows_out_norm.png', result_norm)?

    # img = cv2.imread('/content/drive/MyDrive/mosaic_2/Images/bakat.jpeg',0)
    # edges = cv2.Canny(img,50,100)

    # plt.subplot(121),plt.imshow(img,cmap = 'gray')
    # plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    # plt.subplot(122),plt.imshow(edges,cmap = 'gray')
    # plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

    # # plt.show()
    # cv2_imshow(edges)

    #gray_img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    gray_img=img
    # cv2_imshow(gray_img)

    # #denoising

    # dn_img=cv2.fastNlMeansDenoising(gray_img);
    # cv2_imshow(dn_img)
    # #= cv.fastNlMeansDenoisingMulti(noisy, 2, 5, None, 4, 7, 35)

    # ret, bw_img = cv2.threshold(gray_img, 140, 255, cv2.THRESH_BINARY)
    bw_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 199, 5)
    # cv2_imshow(bw_img)

    # th, th_img = cv2.threshold(bw_img, 220, 255, cv2.THRESH_BINARY_INV)
    # cv2_imshow(th_img) #"Thresholded Image Binary inverse",
    # print(th_img.shape)

    # ALWAYS REMEMBER THAT THE TOTAL WORD HAS TO BE CONNECTED BY A LINE

    noise = (bw_img.shape[0] * bw_img.shape[1]) / 100
    print(noise)

    ret, binary_map = cv2.threshold(bw_img, 127, 255, 0)

    # do connected components processing
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, None, None, None, 8, cv2.CV_32S)

    # get CC_STAT_AREA component as stats[label, COLUMN]
    areas = stats[1:, cv2.CC_STAT_AREA]

    dn2_img = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if areas[i] >= noise:  # keep
            dn2_img[labels == i + 1] = 255
    # cv2_imshow(dn2_img)  #"Result",

    # ROTATION CORRECTNESS

    # finding the angle at which the image is present
    coords = np.column_stack(np.where(dn2_img > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # rotating the image around the centre with the angle from above
    (h, w) = dn2_img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rot_img = cv2.warpAffine(dn2_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # cv2_imshow(rot_img)

    def crop_image(img, tol=0):
        # img is 2D image data
        # tol  is tolerance
        mask = img > tol
        return img[np.ix_(mask.any(1), mask.any(0))]

    crop_img = crop_image(rot_img)
    cv2_imshow(crop_img)

    print(crop_img.shape)

    resize_parm = (800 / crop_img.shape[1])
    resize_width = (int)(resize_parm * crop_img.shape[1])
    resize_height = (int)(resize_parm * crop_img.shape[0])
    crop_img = cv2.resize(crop_img, (resize_width, resize_height))

    print(crop_img.shape)

    # cv2_imshow(crop_img)

    def segmentation(bordered, thresh=255, min_seg=50, scheck=0.25):
        try:
            shape = bordered.shape
            check = int(scheck * shape[0])
            image = bordered[:]
            image = image[check:].T
            shape = image.shape
            # plt.imshow(image)
            # plt.show()

            # find the background color for empty column
            bg = np.repeat(255 - thresh, shape[1])
            bg_keys = []
            for row in range(1, shape[0]):
                if (np.equal(bg, image[row]).all()):
                    bg_keys.append(row)

            lenkeys = len(bg_keys) - 1
            new_keys = [bg_keys[1], bg_keys[-1]]
            # print(lenkeys)
            for i in range(1, lenkeys):
                if (bg_keys[i + 1] - bg_keys[i]) > check:
                    new_keys.append(bg_keys[i])
                    # print(i)

            new_keys = sorted(new_keys)
            # print(new_keys)
            segmented_templates = []
            first = 0
            bounding_boxes = []
            for key in new_keys[1:]:
                segment = bordered.T[first:key]
                if segment.shape[0] >= min_seg and segment.shape[1] >= min_seg:
                    segmented_templates.append(segment.T)
                    bounding_boxes.append((first, key))
                first = key

            last_segment = bordered.T[new_keys[-1]:]
            if last_segment.shape[0] >= min_seg and last_segment.shape[1] >= min_seg:
                segmented_templates.append(last_segment.T)
                bounding_boxes.append((new_keys[-1], new_keys[-1] + last_segment.shape[0]))

            return (segmented_templates, bounding_boxes)
        except:
            return [bordered, (0, bordered.shape[1])]

    segments = segmentation(crop_img)

    images = list()

    for simg in segments[0]:
        # if we detect an image with only rekha on it then it would work
        simg_copy = simg.copy()

        # ret, binary_map = cv2.threshold(simg,127,255,0)
        # nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, None, None, None, 8, cv2.CV_32S)
        # areas = stats[1:,cv2.CC_STAT_AREA]
        # simg = np.zeros((labels.shape), np.uint8)
        # needed_area=0;
        # for i in range(0, nlabels - 1):
        #     needed_area+=areas[i]
        # if needed_area >= 0: #keep
        #   simg_copy=crop_image(simg_copy)
        images.append(simg_copy)

    im = list()

    for image in images:
        roi = image
        # add Shirorekha and small padding
        image = cv2.copyMakeBorder(roi, int(.1 * roi.shape[0]), int(.1 * roi.shape[0]), int(.1 * roi.shape[1]),
                                   int(.1 * roi.shape[1]), cv2.BORDER_CONSTANT, None, 0)

        # Make the shape of Image Square By using pads
        if image.shape[0] > image.shape[1]:
            h = (image.shape[0] - image.shape[1]) / 2
            added_image = cv2.copyMakeBorder(image, 0, 0, int(h), int(h), cv2.BORDER_CONSTANT, None, 0)

            im.append(added_image)
        else:
            h = (image.shape[1] - image.shape[0]) / 2
            added_image = cv2.copyMakeBorder(image, int(h), int(h), 0, 0, cv2.BORDER_CONSTANT, None, 0)

            im.append(added_image)

    return im

def preduct(x,model2):

    mapping={
    7:"क", 21:"ज", 0:"ट", 1:"ठ", 2:"ड", 3:"ढ", 4:"त", 5:"द", 6:"ध", 8:"न",
    9:"प", 10:"फ", 11:"ब", 12:"म",
    13:"र", 14:"ल", 15:"व", 16:"ष",
    17:"स", 18:"ह", 19:"क्ष", 20:"त्र"}

    x=cv2.resize(x,(32,32))

    x = np.expand_dims(x, axis=0)

    #ans1=model1.predict(x)
    ans2=model2.predict(x)

    #a=mapping[np.argmax(ans1)]
    b=mapping[np.argmax(ans2)]

    lizto = (b )

    print( b  )
    return b

def listToString(s): 
    str1 = " "   
    return (str1.join(s))

def predrict(img):

  #--------------------------ENTER THE LOCATION OF THE MODELS HERE----------------------------#

  # model1=keras.models.load_model("/content/gdrive/MyDrive/mosaic_2/aryan_folder/all_models2/res_simple_model.h5")
  # model1.load_weights("/content/gdrive/MyDrive/mosaic_2/aryan_folder/all_models2/res_simple_weights.hdf5")

  model2=keras.models.load_model("/content/drive/MyDrive/mosaic_2/aryan_folder/res_model.h5")
  #model2.load_weights("/content/gdrive/MyDrive/mosaic_2/aryan_folder/all_models2/res_norm_weights.hdf5")


  ans=list()
  img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  # Image is Segmented into separate Words
  words=word_segment(img)
  #We  iterate through Each word
  for word in words:
    # Word is Segmented into separate Character
    characters=segment(word)
    #we iterate through each character
    for character in characters:
      character = cv2.cvtColor(character , cv2.COLOR_GRAY2BGR)
      cv2_imshow(character)
      a=preduct(character,model2)
      ans.append(a)
    ans.append(" ")
    
  
  if ans[-1]==" ":
      ans.pop
  #print(ans)
  return ans

def predict(image):
    #--------------------------ENTER THE LOCATION OF THE MODELS HERE----------------------------#

  # model1=keras.models.load_model("/content/gdrive/MyDrive/mosaic_2/aryan_folder/all_models2/res_simple_model.h5")
  # model1.load_weights("/content/gdrive/MyDrive/mosaic_2/aryan_folder/all_models2/res_simple_weights.hdf5")

  model2=keras.models.load_model("/content/drive/MyDrive/mosaic_2/aryan_folder/res_model.h5")
  #model2.load_weights("/content/gdrive/MyDrive/mosaic_2/aryan_folder/all_models2/res_norm_weights.hdf5")




  ans=list()
  img=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
  

  Contains_only_one_word=False

  if Contains_only_one_word==True:
    print(Contains_only_one_word)
    characters=segment(img)
    #we iterate through each character
    for character in characters:
      character = cv2.cvtColor(character , cv2.COLOR_GRAY2BGR)
      cv2_imshow(character)
      a=preduct(character,model2)
      ans.append(a)
  else:
      # Image is Segmented into separate Words
      words=word_segment(img)
      #We  iterate through Each word
      for word in words:
        # Word is Segmented into separate Character
        characters=segment(word)
        #we iterate through each character
        for character in characters:
          character = cv2.cvtColor(character , cv2.COLOR_GRAY2BGR)
          cv2_imshow(character)
          a=preduct(character,model2)
          ans.append(a)
        ans.append(" ")
    
  
  if ans[-1]==" ":
      ans.pop
  #print(ans)
  return ans



