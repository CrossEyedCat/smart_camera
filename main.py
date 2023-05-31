import face_recognition
import pickle
import cv2
from datetime import datetime, timedelta
from psycopg2 import Error, OperationalError
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="ep-misty-fire-374016.eu-central-1.aws.neon.tech",
        database="neondb",
        user="gabyfollow",
        password="e3iJTC6bMFxq")


def main():
    insert_query = """INSERT INTO visitors(id, id_person, id_room, date) VALUES(%s, %s, %s, %s);"""
    id_room = 1
    conn = get_connection()
    cursor = conn.cursor()
    # find path of xml file containing haarcascade file
    cascPathface = "haarcascade_frontalface_default.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())

    print("Streaming started")
    # loop over frames from the video file stream7
    id = 1
    while True:
        video_capture = cv2.VideoCapture("rtsp://admin:@192.168.1.10/1")
        # grab the frame from the threaded video stream
        ret, frame = video_capture.read()
        print(frame.__sizeof__())
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # make 4 times smaller frame
        small_frame = cv2.resize(gray, (0, 0), fx=0.25, fy=0.25)
        print("Frame caught!")
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
            name = "0"
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
                item_tuple = (id, int(cur_name), id_room, datetime.now())
                id = id + 1
                print(item_tuple)
                cursor.execute(insert_query, item_tuple)
                conn.commit()
            except Exception as err:
                print(err)
        if cv2.waitKey(1) == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
