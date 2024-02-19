import cv2
import requests
import pandas as pd
import csv
from jsonpath_ng import parse
from pyzbar import pyzbar

def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    decoded_isbns = set()
    for barcode in barcodes:
        barcode_info = barcode.data.decode('utf-8')
        decoded_isbns.add(barcode_info)
        left, top, width, height = barcode.rect
        cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (left + 6, top - 6), font, 2, (255, 255, 255), 1)
    return frame, decoded_isbns

def video_capture():
    camera = cv2.VideoCapture(0)
    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            break
        frame, decoded_isbns = read_barcodes(frame)
        img = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
        cv2.imshow('Frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()
    return decoded_isbns

def fetch_book_info(isbns):
    headers = ['title', 'subtitle', 'author', 'publisher']
    with open('data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        for isbn in isbns:
            url = f'https://www.googleapis.com/books/v1/volumes?q={isbn}'
            response = requests.get(url)
            if response.ok:
                json_data = response.json()
                items = json_data.get('items', [])
                if items:
                    volume_info = items[0].get('volumeInfo', {})
                    title = volume_info.get('title', '')
                    subtitle = volume_info.get('subtitle', '')
                    authors = ', '.join(volume_info.get('authors', []))
                    publisher = volume_info.get('publisher', '')
                    writer.writerow([title, subtitle, authors, publisher])
                else:
                    writer.writerow(['', '', '', ''])

def main():
    decoded_isbns = video_capture()
    if decoded_isbns:
        fetch_book_info(decoded_isbns)

if __name__ == '__main__':
    main()
