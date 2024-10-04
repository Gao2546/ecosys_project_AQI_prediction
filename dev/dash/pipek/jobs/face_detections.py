# import datetime
# import dlib
# import cv2
# import json
# from sqlalchemy import select

# from pipek import models


# def detect(image_id):
#     print("detect", image_id)
#     session = models.get_session()
#     image = session.get(models.Image, image_id)

#     print("process", image.id)
#     image.status = "processing"
#     image.updated_date = datetime.datetime.now()
#     session.add(image)
#     session.commit()

#     detector = dlib.get_frontal_face_detector()
#     img = cv2.imread(image.path)
#     dets = detector(img, 1)

#     results = dict(faces=len(dets))
#     print(dets)

#     image.status = "completed"
#     image.results = json.dumps(results)
#     image.updated_date = datetime.datetime.now()
#     session.add(image)
#     session.commit()
