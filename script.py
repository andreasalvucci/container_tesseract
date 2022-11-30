import numpy as np
import cv2
import imutils
import re
from imutils.object_detection import non_max_suppression
import pytesseract
from matplotlib import pyplot as plt
import socket, select


server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("localhost",1312))
server.listen()


while True:
    print("Il server è in ascolto")
    try:

        client_socket, client_address = server.accept()
    except Exception:
        print(Exception)
    print(f"Accettata la connessione con ",client_address)

    file = open("received.jpg", "wb")

    cont = 0

    print("Ricevo l'immagine dal client...")
    image_chunk = client_socket.recv(2048)
    while image_chunk:
        cont+=1
        file.write(image_chunk)
        image_chunk = client_socket.recv(2048)



    file.close()
    
    print("Immagine interamente ricevuta")
    print("Processo l'immagine...")

    image = cv2.imread("received.jpg")
    orig = image.copy()
    (origH, origW) = image.shape[:2]
    (newW, newH) = (320, 320)
    rW = origW / float(newW)
    rH = origH / float(newH)
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]
    cv2.imwrite("imageresized.jpg",image)
    blob = cv2.dnn.blobFromImage(image, 1.0, (320, 320),(123.68, 116.78, 103.94), swapRB=True, crop=False)
    net = cv2.dnn.readNet("east.pb")
    layerNames = ["feature_fusion/Conv_7/Sigmoid","feature_fusion/concat_3"]
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    def predictions(prob_score, geo):
        (numR, numC) = prob_score.shape[2:4]
        boxes = []
        confidence_val = []

        # loop over rows
        for y in range(0, numR):
            scoresData = prob_score[0, 0, y]
            x0 = geo[0, 0, y]
            x1 = geo[0, 1, y]
            x2 = geo[0, 2, y]
            x3 = geo[0, 3, y]
            anglesData = geo[0, 4, y]

            # loop over the number of columns
            for i in range(0, numC):
                if scoresData[i] < 0.5:
                    continue

                (offX, offY) = (i * 4.0, y * 4.0)

                # extracting the rotation angle for the prediction and computing the sine and cosine
                angle = anglesData[i]
                cos = np.cos(angle)
                sin = np.sin(angle)

                # using the geo volume to get the dimensions of the bounding box
                h = x0[i] + x2[i]
                w = x1[i] + x3[i]

                # compute start and end for the text pred bbox
                endX = int(offX + (cos * x1[i]) + (sin * x2[i]))
                endY = int(offY - (sin * x1[i]) + (cos * x2[i]))
                startX = int(endX - w)
                startY = int(endY - h)

                boxes.append((startX, startY, endX, endY))
                confidence_val.append(scoresData[i])

        # return bounding boxes and associated confidence_val
        return (boxes, confidence_val)

    (boxes, confidence_val) = predictions(scores, geometry)
    boxes = non_max_suppression(np.array(boxes), probs=confidence_val)

    results = []
    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        #extract the region of interest
        r = orig[startY:endY, startX:endX]

        #configuration setting to convert image to string.  
        configuration = ("-l ita --oem 1 --psm 8")
        ##This will recognize the text from the image of bounding box
        text = pytesseract.image_to_string(r, config=configuration)

        # append bbox coordinate and associated text to the list of results 
        results.append(((startX, startY, endX, endY), text))


        orig_image = orig.copy()


    print(text)
    print("Immagine processata, invio il risultato al client...")
    cleanedText = text.replace(" ", "")
    cleanedText = cleanedText.replace("\n","")
    cleanedText = re.sub('[^A-Za-z0-9]+', '', cleanedText)

    print(cleanedText)

    client_socket.send(cleanedText.encode())

    client_socket.close()

