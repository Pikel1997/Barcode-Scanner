import cv2
import requests
import os
import pandas as pd
import json
import csv
from jsonpath_ng import parse
from pyzbar import pyzbar


def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        barcode_info = barcode.data.decode('utf-8')
        isbn.add(barcode_info)
        left, top, width, height = barcode.rect
        cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (left + 6, top - 6), font, 2, (255, 255, 255), 1)
    return frame


def video_cap():
    global isbn
    isbn = set()
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    while ret:
        ret, frame = camera.read()
        frame = read_barcodes(frame)
        img = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
        cv2.imshow('Frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()
    
    
def csv_file():
    if os.path.isfile('data.csv'):
        pass
    else:
        headers = ['title', 'subtitle', 'author', 'publisher']
        df = pd.DataFrame(headers).T
        df.to_csv('data.csv', index=False, mode='a', header=False)
    
def get_info():
    global barcodedata
    headers = ['title', 'subtitle', 'author', 'publisher']
    barcodedata = ['', '', '', '']
    for isbns in isbn:
        url = f'https://www.googleapis.com/books/v1/volumes?q={isbns}'
        response = requests.request("GET", url)
        json_data = json.loads(response.text)
        title = parse('items[0].volumeInfo.title')
        subtitle = parse('items[0].volumeInfo.subtitle')
        author = parse('items[0].volumeInfo.authors')
        publisher = parse('items[0].volumeInfo.publisher')
        info = [title, subtitle, author, publisher]
        for obj in info:
            index_val = info.index(obj)
            for val in obj.find(json_data):
                barcodedata[index_val] = val.value
        print(barcodedata)
        with open('data.csv', 'a') as f:
            write = csv.writer(f)
            write.writerows([barcodedata])
                

def main():
    csv_file()
    video_cap()
    get_info()

if __name__ == '__main__':
    main()
    
