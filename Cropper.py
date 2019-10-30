# from PyPDF2 import PdfFileReader
import ghostscript, pdb, glob
import cv2
from matplotlib import pyplot as plt
import numpy as np
import pytesseract

class Cropper:

    def __init__(self, signafier_size, dilate_iterations=7, right_bound=0.25, illegal_signafiers=[]):
        self.signafier_size = signafier_size
        self.dilate_iterations = dilate_iterations
        self.right_bound = right_bound
        self.illegal_signafiers = illegal_signafiers
        self.pngs = []

    def pdf2png(self, pdf_input_path):
        args = ("""
        pdf2png -dNOPAUSE -q -r500 -sPAPERSIZE=a4 -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -dUseTrimBox -sDEVICE=png16m -dFirstPage=2 -sOutputFile=working/page_%03d.png
        """ + pdf_input_path).encode("utf-8").split()
        ghostscript.Ghostscript(*args)

    def __scan(self):
        return(sorted(glob.glob("working/*.png"), key=str.lower))

    def __preprocessing(self, png):
        img = cv2.imread(png)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)
        #Binary Dilation
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(edged, kernel, iterations=self.dilate_iterations)
        return img, gray, dilated

    def __find_signafiers(self, orig, grayscale, working, size_min = 0, size_max = 10^10):
        contours, heirarchy = cv2.findContours(working, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if(area > size_min and area < size_max):
                #Check pos of contour, needs to be less than 1/4 in to page
                x,y,w,h = cv2.boundingRect(cnt)
                if(x < (self.right_bound * working.shape[1])):
                    if(self.__is_legal(grayscale, cnt)):
                        cv2.drawContours(orig, [cnt], 0, (0,255,0), 3)
        plt.imshow(orig, cmap = 'gray', interpolation = 'bicubic')
        plt.show()

    def __is_legal(self, img, cnt):
        #Simplier to specify what can't be used. Then see can we find that.
        x,y,w,h = cv2.boundingRect(cnt)
        contour = img[y:y+h,x:x+w]
        if(any(substring in pytesseract.image_to_string(contour, config=r'--psm 8') for substring in self.illegal_signafiers)):
            return False
        return True

    def Crop(self):
        self.pngs = self.__scan()
        for png in self.pngs:
            #Pre-Processing
            orig, grayscale, dilated = self.__preprocessing(png)
            #Lets find some contours
            self.__find_signafiers(orig, grayscale, dilated, size_max=(self.signafier_size * 1.1))
