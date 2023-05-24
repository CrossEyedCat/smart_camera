import face_recognition
import pickle
import cv2
from datetime import datetime, timedelta
from psycopg2 import Error
import psycopg2
id_room = 1
conn = 0
cursor = 0
try:
    conn = psycopg2.connect(
        host="ep-misty-fire-374016.eu-central-1.aws.neon.tech",
        database="neondb",
        user="gabyfollow",
        password="e3iJTC6bMFxq")
    cursor = conn.cursor()
except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
# find path of xml file containing haarcascade file
cascPathface = "haarcascade_frontalface_default.xml"
# load the harcaascade in the cascade classifier
faceCascade = cv2.CascadeClassifier(cascPathface)
# load the known faces and embeddings saved in last file
data = pickle.loads(open('face_enc', "rb").read())

print("Streaming started")
video_capture = cv2.VideoCapture(0)
# loop over frames from the video file stream7
id =100000
while True:
    # grab the frame from the threaded video stream
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(30, 30),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
    # make 16 times smaller frame
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # convert the input frame from BGR to RGB
    rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # the facial embeddings for face in input
    encodings = face_recognition.face_encodings(rgb)
    names = []
    # loop over the facial embeddings incase
    # we have multiple embeddings for multiple fcaes
    for encoding in encodings:
        # Compare encodings with encodings in data["encodings"]
        # Matches contain array with boolean values and True for the embeddings it matches closely
        # and False for rest
        matches = face_recognition.compare_faces(data["encodings"],
                                                 encoding)
        # set name =inknown if no encoding matches
        name = "Unknown"
        # check to see if we have found a match
        if True in matches:

            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)
        # update the list of names
        names.append(name)
        # loop over the recognized faces
    for cur_name in names:
        try:
            insert_query = """INSERT INTO visitors(id, id_person, id_room, date) VALUES(%s, %s, %s, %s);"""
            item_tuple = (id, int(cur_name), id_room, datetime.now())
            id=id+1
            print(item_tuple)
            cursor.execute(insert_query, item_tuple)
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            print("Error while send to PostgreSQL", error)
    if cv2.waitKey(1) == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()
