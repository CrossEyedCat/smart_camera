from imutils import paths
import face_recognition
import pickle
import cv2
import os
import time

count_of_last_users = 0
while True:
    while True:
        # в директории Images хранятся папки со всеми изображениями
        imagePaths = list(paths.list_images('H:/My Drive/Images'))
        # проводим проверку
        if count_of_last_users != imagePaths.__len__():
            count_of_last_users = imagePaths.__len__()
            break
        time.sleep(10)

    knownEncodings = []
    knownNames = []
    # перебираем все папки с изображениями
    for (i, imagePath) in enumerate(imagePaths):
        # извлекаем имя человека из названия папки
        name = imagePath.split(os.path.sep)[-2]
        # загружаем изображение и конвертируем его из BGR (OpenCV ordering)
        # в dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # используем библиотеку Face_recognition для обнаружения лиц
        boxes = face_recognition.face_locations(rgb, model='hog')
        # вычисляем эмбеддинги для каждого лица
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    # сохраним эмбеддинги вместе с их именами в формате словаря
    data = {"encodings": knownEncodings, "names": knownNames}
    # записываем в файл
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()
    time.sleep(60)
