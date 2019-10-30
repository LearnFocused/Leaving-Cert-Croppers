from Cropper import Cropper
import argparse

EconomicsCropper = Cropper(12000, dilate_iterations=8, right_bound=0.15, illegal_signafiers={'i', 'ii', 'iii', 'iv', 'v'})

#Get the PDF we will crop
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--pdf", required=True, help="path to input pdf")
args = vars(ap.parse_args())

#Turn it into PNGs
print("Cropping...")
# EconomicsCropper.pdf2png(args['pdf'])

EconomicsCropper.Crop()
