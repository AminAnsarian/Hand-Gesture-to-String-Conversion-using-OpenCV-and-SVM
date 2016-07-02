import cv2
import numpy as np
import operator
import os

MIN_CONTOUR_AREA = 100

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30


class ContourWithData():   #main class of detection
    npaContour = None
    boundingRect = None
    intRectX = 0
    intRectY = 0
    intRectWidth = 0
    intRectHeight = 0
    fltArea = 0.0

    def calculateRectTopLeftPointAndWidthAndHeight(self):   #setting up cordinates for contours
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):
        if self.fltArea < MIN_CONTOUR_AREA: return False
        return True

def main(filename):
    allContoursWithData = []
    validContoursWithData = []

    try:
        npaClassifications = np.loadtxt("classifications.txt", np.float32)
    except:
        print ("error, unable to open classifications.txt, exiting program\n")
        os.system("pause")
        return

    try:
        npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
    except:
        print ("error, unable to open flattened_images.txt, exiting program\n")
        os.system("pause")
        return

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))   #Transform into one dim matrix

    kNearest = cv2.ml.KNearest_create()         #Create a KNN algorithm

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)       #training the datasets

    imgTestingNumbers = cv2.imread(filename)

    if imgTestingNumbers is None:
        print ("error: image not read from file \n\n")
        os.system("pause")
        return

    imgGray = cv2.cvtColor(imgTestingNumbers, cv2.COLOR_BGR2GRAY)       #Negative Filter
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)

    imgThresh = cv2.adaptiveThreshold(imgBlurred,                       #Passing Only White Colour
                                      255,
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY_INV,
                                      11,
                                      2)

    imgThreshCopy = imgThresh.copy()

    imgContours, npaContours, npaHierarchy = cv2.findContours(imgThreshCopy,         #Finding Contours in User's Image
                                                 cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_SIMPLE)

    for npaContour in npaContours:                  #Contours ---> Class Contours
        contourWithData = ContourWithData()
        contourWithData.npaContour = npaContour
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)
        allContoursWithData.append(contourWithData)

    for contourWithData in allContoursWithData:
        if contourWithData.checkIfContourIsValid():
            validContoursWithData.append(contourWithData)

    validContoursWithData.sort(key=operator.attrgetter("intRectX"))

    strFinalString = ""
    first = validContoursWithData[0].intRectX
    for contourWithData in validContoursWithData:
        second = contourWithData.intRectX
        cv2.rectangle(imgTestingNumbers,
                      (contourWithData.intRectX, contourWithData.intRectY),
                      (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),
                      (0, 255, 0),
                      2)

        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,
                           contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))

        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))    # integer 1d matrix

        npaROIResized = np.float32(npaROIResized)   #float 1d matrix


        if(contourWithData.intRectWidth*contourWithData.intRectHeight) > 900:
            retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)  #Initiate Detection using KNN
            strCurrentChar = str(chr(int(npaResults[0][0])))

            if(second - first) > 30:
                strFinalString = strFinalString  + " "+ strCurrentChar
            else:
                strFinalString = strFinalString + strCurrentChar
            first = contourWithData.intRectX + contourWithData.intRectWidth

    print("\n" + strFinalString + "\n")
    # cv2.imshow("imgTestingNumbers", imgTestingNumbers)
    # cv2.waitKey(0)

    # cv2.destroyAllWindows()

    return strFinalString

if __name__ == "__main__":
    main("output.PNG")










