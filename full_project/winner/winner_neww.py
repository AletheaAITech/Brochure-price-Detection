import collections
import glob
import os
import re
import time

BASE_DIR = os.getcwd()
import numpy as np
import cv2
from pdf2image import convert_from_path
import pandas as pd
from paddleocr import PaddleOCR, draw_ocr
ocr = PaddleOCR(use_angle_cls=True, lang='en')

full_list=[]

def pdff_to_jpg(filename):
    images = convert_from_path(str(filename))
    if not os.path.exists(BASE_DIR+'/images1/'):
        os.makedirs(BASE_DIR+'/images1/')

    for i in range(len(images)):
         images[i].save(BASE_DIR+'/images1/page' + str(i) + '.jpg', 'JPEG')

def pre_process(image):
    original = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # lower = np.array([22, 93, 0], dtype="uint8")
    # upper = np.array([45, 255, 255], dtype="uint8")
    lower = np.array([20, 170, 170], dtype="uint8")
    upper = np.array([45, 255, 255], dtype="uint8")
    mask = cv2.inRange(image, lower, upper)

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    height_list = []
    width_lsit = []
    boxes = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        print(w, 'lll')

        if  w > 150 and h > 60:
            width_lsit.append(w)
            height_list.append(h)
            print(h)

            boxes.append([x, y, w, h])
            cv2.rectangle(original, (x, y), (x + w, y + h), (36, 255, 12), 2)
    # cv2.imshow('ssss',original)
    cv2.imwrite('images/ssss.png', original)
    # cv2.waitKey(0)
    return boxes


def get_text(image, box):
    # try:
    full_list = []
    for i in box:

        # h=i[3]
        #
        # if h>120:
        #     y=h-120
        #     h=150
        #
        # else:
        #     h=i[3]+50
        x = i[0]-5
        y = i[1]
        w = i[2]+5
        h = i[3]+50
        print(h,'ddddddddddd')
        try:
            price_cropped = image[int(y):y + h, int(x):x + w]


            price_result = ocr.ocr(price_cropped, cls=True)
        except:

            continue
        # for m in price_result:
        #     print(m[1][0])
        print(price_result)
        le=0
        # for le in range(0,len(price_result)+1):
        #     try:
        #         float(price_result[le][1][0])
        #         break
        #     except ValueError:
        #         print('next')
        if price_result!=[]:
            previous_price=price_result[le][1][0]
            print(previous_price,'hhhhhhhhhhhhhhhhhhhhhhhhhh')
            if len(previous_price)>=3:
                if previous_price[-3]!='.':
                    previous_price=previous_price[:-2]+'.'+previous_price[-2:]
            try:
                new_price=price_result[le+1][1][0]
            except:
                new_price=''

            new_price = re.sub('[!@#$:%;*&]', '', new_price)
            new_price = re.sub("[a-zA-Z]+", '', new_price)
            bb=re.findall('[a-zA-Z]+',previous_price)
            print(bb,'gg')
            if len(bb)>0:
                previous_price = re.sub('[!@#$:%;*&]', '', previous_price)
                previous_price = re.sub("[a-zA-Z]+", '', previous_price)
                if previous_price=='.':
                    previous_price=''
            print(new_price)
            name=''
            for i in range(le+2,len(price_result)):
                name+=price_result[i][1][0]
                name+=' '

            if new_price!='' and new_price[-1]=='.':
                new_price+='00'
            elif '.' not in new_price:
                new_price+='.00'
            print(previous_price)
            print(new_price)
            print(name)
            if previous_price != '' and new_price != '' and name != '':
                try:
                    brand=name.split(' ')[0]
                    brand= re.sub('[0-9]+','', brand)
                    if brand=='':
                        brand=name.split(' ')[1]
                        name=' '.join(name.split(' ')[1:])


                except:
                    brand=name
                if brand!='.':
                    full_list.append([name,brand,new_price,previous_price])
    # except:
    #     pass
    full_list.append(['','','',''])
    full_list.append(['','','',''])

    return full_list


def get_dataa(image_list):
    data_list=[]
    for image in image_list:
        image = cv2.imread(image, flags=cv2.IMREAD_COLOR)
        boxx = pre_process(image)
        full_list=get_text(image,boxx)
        print(full_list,'ggggggggggggggggg')
        print(len(boxx))
        if len(full_list)>1:
            df=pd.DataFrame(full_list)

            data_list.append(df)
    if data_list!=[]:
        final_df = pd.concat(data_list, ignore_index=True)
        final_df.columns = ['Products', 'Brand', 'New_price', 'Previous_price']
        if not os.path.exists(BASE_DIR + '/csvs/'):
            os.makedirs(BASE_DIR + '/csvs/')
        final_df.to_csv(BASE_DIR + '/csvs/winner_extracted2.csv', index=False)


if __name__ == "__main__":
    pdff_to_jpg('Brochure-MOM-MAY-2020.pdf')
    time.sleep(2)
    files=glob.glob(BASE_DIR+'/images/*.jpg')
    files = sorted(files, key=lambda x: float(re.findall("(\d+)", x)[0]))
    get_dataa(files)
