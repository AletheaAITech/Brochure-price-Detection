import glob
import re
import time

import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import os
import cv2
import keras_ocr
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
pipeline = keras_ocr.pipeline.Pipeline()
BASE_DIR = os.getcwd()
from paddleocr import PaddleOCR, draw_ocr
ocr = PaddleOCR(use_angle_cls=True,
                                lang='en')


def pdff_to_jpg(pdf_path):
    images = convert_from_path(str(pdf_path))
    if not os.path.exists(BASE_DIR+'/images/'):
        os.makedirs(BASE_DIR+'/images/')
    time.sleep(4)
    for i in range(len(images)):
         images[i].save(BASE_DIR+'/images/page' + str(i) + '.jpg', 'JPEG')




def method1(prediction_groups):
    coordinates=[]
    pricee=[]
    status=''
    for i in prediction_groups[0]:
        numbers = re.findall('[0-9]+', i[0])
        alphabett = re.findall('[a-zA-Z]+', i[0])
        if numbers:
            if alphabett==[]:
                bounding_boxx = i[1].tolist()
                # bounding_boxx=i[1].tolist()
                # print(i[0], 'uuuuuuuu', bounding_boxx[1][0], bounding_boxx[0][0],'ssssssss',(bounding_boxx[1][0]-bounding_boxx[0][0]))
                if 75 < (bounding_boxx[1][0] - bounding_boxx[0][0]) < 165:
                    if bounding_boxx[0][1]>160:

                        # print(i[0], i[1].tolist())
                        pricee.append(i[0])
                        coordinates.append(i[1].tolist())
                    if  bounding_boxx[0][1]>150:
                        status= 'space'
    return coordinates,pricee,status




def get_type(roi):
    typee=''
    if len(roi) <= 8:
        typee='big'
    # elif roi[0][0][1]
    # elif 1700>roi[-2][0][1]>1600:
    #     typee='method2'
    elif roi[-2][0][1]>2000 and roi[0][0][1]>500:
        typee='method2'
    elif 1900>roi[-2][0][1]>1880:
        typee='method3'

    return typee





def get_names(pred):
    name_list = []
    brand_name=[]
    extraa=['zero', 'vat','ad', 'nil','tor','nca','nci','incl','zeno','tero','s','zeso','t','atincl','ro','rs','o','rd','stc','cl']
    for i in pred[0]:
        if i[0] not in extraa:
            name_list.append(i[0])
    return name_list


def actual_pricee(typ,status,r,image):
    print(typ,status)
    real_amount=[]
    if typ == 'big' and status == 'space':
        x1 = int(r[0][0])+20
        y1 = int(r[0][1]) - 50
        x2 = 120
        y2 = 50
    elif typ == 'big':
        x1 = int(r[0][0]) + 20
        y1 = int(r[0][1]) - 50
        x2 = 120
        y2 = 50
    elif typ == 'method3':
        x1 = int(r[0][0]) + 20
        y1 = int(r[0][1]) - 50
        x2 = 120
        y2 = 50
    elif typ == 'method2':
        x1 = int(r[0][0])
        y1 = int(r[0][1]) - 50
        x2 = 100
        y2 = 50
    else:
        x1 = int(r[0][0]) + 20
        y1 = int(r[0][1]) - 50
        x2 = 120
        y2 = 50
    roi_cropped = image[int(y1):y1 + y2, int(x1):x1 + x2]
    pred = get_data(roi_cropped)
    # print(pred[0],'jjjjjjjjjjj')
    for m in pred[0]:
        value=str(m[0])
        # print(value[0:2],'hhhhhhhhhhhh')
        mm=value.replace("o", "0")
        # print(mm,'ggggggggggg')
        alphabetss=re.findall("[a-zA-Z]+", mm)
        if not alphabetss:
            real_amount.append(mm)
    actual_p = ''.join(real_amount)
    try:
        if actual_p[0:2] == '00' or actual_p[0:2] == 'o0' :
            actual_p = actual_p[2:] + '00'
    except:
        pass
    try:
        if actual_p[-3] == '1' and len(actual_p) >= 5:
            actual_p=actual_p[:-3] + actual_p[-2:]
    except:
        pass
    # print(discounted_price,'discounted')
    try:
        previous_price = int(actual_p) / 100
    except:
        previous_price=''
    return previous_price


def get_data(image_path):
    prediction_groups = pipeline.recognize([image_path])  # print image with annotation and boxes
    return prediction_groups

def main(imagee):
    # name = imagee.split('.')[0].split('/')[-1]
    # read image
    image = cv2.imread(imagee, flags=cv2.IMREAD_COLOR)
    # main function
    # df = get_roii(image, name)
    all_names = []
    brand_list=[]
    real_price_list=[]
    brand_name=''
    #Get result of full text extracted from image
    rrr = get_data(image)

    #Get prices and their coordinates from image
    roi,price_list,status=method1(rrr)
    price_list = [int(elem) / 100 for elem in price_list]
    print(price_list)
    #list of extra words which we have to delete if incuded

    #Get and categorize type of broucher
    typee=get_type(roi)
    blank=0

    # Croping of image to get name based on type of broucher
    for r in roi:
        indexx=roi.index(r)
        discounted_price=price_list[indexx]
        real_price = actual_pricee(typee,status, r, image)

        if real_price!='':
            if discounted_price> real_price:
                get_index = str(discounted_price).index('.')
                l = list(str(discounted_price))
                del (l[get_index-1])
                price_list[indexx]=''.join(l)

            if real_price<1000 and (real_price-discounted_price)>250:
                r_index=str(real_price).index('.')
                ree=list(str(real_price))
                del ree[r_index-1]
                real_price=''.join(ree)
        real_price_list.append(real_price)



        if typee=='big' and status=='space':

            x1 = int(r[0][0]) + 190
            y1 = int(r[0][1]) - 50
            x2 = 210
            y2 = 100
        elif typee=='big':
            x1 = int(r[0][0]) + 170
            y1 = int(r[0][1]) - 50
            x2 = 180
            y2 = 100
        elif typee=='method3':
            x1 = int(r[0][0])+150
            y1 = int(r[0][1])-50
            x2 = 220
            y2 = 100
        elif typee=='method2':
            x1 = int(r[0][0]) + 130
            y1 = int(r[0][1]) - 20
            x2 = 190
            y2 = 100
        else:
            x1 = int(r[0][0]) + 130
            y1 = int(r[0][1]) - 50
            x2 = 180
            y2 = 100
        roi_cropped = image[int(y1):y1+y2,int(x1):x1+x2]



        try:
            pred=get_data(roi_cropped)
            # print(pred)
            # name_list=pred[0]
            # print(name_list)
            name_list = get_names(pred)
            # print(name_list)
            namee = ' '.join(name_list)
            try:
                if len(name_list[0])>2:
                    brand_name=name_list[0]
                elif len(name_list[0])<=2 :
                    brand_name=name_list[0]+' '+name_list[1]
            except:
                brand_name=''
            if namee=='':
                blank+=1
            if blank==4 and roi.index(r)<6:
                print('yesss')
                # method2()
            brand_list.append(brand_name)
            all_names.append(namee)


            # show cropped image
            # cv2.imshow("ROI", roi_cropped)
            # cv2.waitKey(0)
        except:
            pass

    # for n ,p ,b in zip(all_names,price_list,brand_list):
    #     print('Name== ',n)
    #     print('Price== ',p)
    #     print('Brand== ',b)
    all_names.append(' ')
    brand_list.append(' ')
    real_price_list.append(' ')
    price_list.append(' ')
    df=pd.DataFrame([all_names,brand_list,real_price_list,price_list])
    df=df.T
    return df
    # df.columns = ['Name','Brand','Price']
    # df = df.dropna(how='any', axis=0)
    # print(df)
    # df.to_csv(BASE_DIR+'/dream_price/csvs/'+str(count)+'.csv',index=False)




def get_dfs(imagee_dir):
    df_list=[]

    for imagee in imagee_dir:

        dff=main(imagee)
        df_list.append(dff)
    final_df = pd.concat(df_list, ignore_index=True)
    final_df.columns=['Name','Brand','old_price','Discount_Price']
    if not os.path.exists(BASE_DIR+'/csvs/'):
        os.makedirs(BASE_DIR+'/csvs/')
    final_df.to_csv(BASE_DIR+'/csvs/Dream_price_extracted.csv',index=False)



if __name__ == "__main__":
    pdf_path='/home/webtunix/Music/price_detection/Brochure/DreamPrice/Dreamprice_180222_130322.pdf'
    pdff_to_jpg(pdf_path)
    time.sleep(2)
    files = glob.glob(BASE_DIR + '/images/*.jpg')
    files = sorted(files, key=lambda x: float(re.findall("(\d+)", x)[0]))
    get_dfs(files)

