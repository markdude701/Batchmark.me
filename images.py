#http://effbot.org/imagingbook/image.htm
#Mark Makowski - DIGIT 400 - Python Imaging Library (PIL) - Image Module
#import Flask
#from Flask import flash
import PIL as pillow #Image library
import glob, os, os.path #Import the images
from PIL import Image
from flask import send_file
#im = Image.open("img.jpg")

newIm = ""

def savePrompt(im): #Will need to write function to POST new image to a directory
    try:
        wmImg = newImg.save(pn + "WaterMarked.JPG", "JPEG")
        return send_file(pn + "WaterMarked.JPG", attachment_filename='WaterMarked.jpg')
        #flash("Saved/Sent File")
    except Exception as e:
        print(str(e))
    
    
    

def firstResize(im, photo_local):
    pn = photo_local
    global pn
    global new_Name
    
    #UserImage = uploaded_photo
    size = 128, 128 #Documentation called for this for some reason
    #imDir = "".join(['/var/www/FlaskApp/FlaskApp/uploads/', str(uploaded_photo)])
    #imOpen = Image.open(im)
    #imDir = "/uploads/{{uploaded_photo}}"
    #imDir.append(uploaded_photo)
   
    
    imResized = im.resize((1920,1080), Image.BILINEAR)
    #size = ims.size #Size of the image in pixels
    #print(str(size)) #Size will return 1920x1080
    new_Name = photo_local + "-1080.JPG"
    savedIm = imResized.save(new_Name, "JPEG") #Change this to POST somehow
    
    #flash("Successfully created " + newIm)

#print("Where would you like to see?") #User Selection - Options
#print("1. Top Left Watermark")
#print("2. Top Right Watermark")
#print("3. Bottom Left")
#print("4. Bottom Right Watermark")

#Will need to collect user option somehow
#userInput = input("Option#: ") #User Selection; Will need to be called from the radio button input



def processTopLeft(wm, im, userInput, photo_local, wm_local):
    newIm = Image.open(photo_local + "-1080.JPG")
    #Place a Image in the bottom right hand corner of the page - Where most photographers would put their watermark of a 1920x1080
    smSz = (250,100) #New Size of watermark
    leftTopPlc = (100,100,350,200) #Location on Image
    smWM = wm.resize(smSz, Image.BILINEAR) #Resize Watermark to fit image
    savedWm = smWM.save(wm_local + "SMALL.JPG", "JPEG")
    newIm.paste(smWM, leftTopPlc)#(Start X,Start Y,End X, End Y)
    #im.show()#SHows the Image 
    #flash("Paste Completed")
    #savePrompt(newIm)
    wmSaved = newIm.save(photo_local + "Watermark.JPG", "JPEG")
    #return send_file(photo_local + "Watermark.JPG", attachment_filename='WaterMarked.jpg')

def processTopRight(wm, im, userInput, photo_local, wm_local):
    newIm = Image.open(photo_local + "-1080.JPG")
    #Place a Image in the bottom right hand corner of the page - Where most photographers would put their watermark of a 1920x1080
    smSz = (250,100) #New Size of watermark
    rightTopPlc = (1600,100,1850,200) #Location on Image
    smWM = wm.resize(smSz, Image.BILINEAR) #Resize Watermark to fit image
    savedWm = smWM.save(wm_local + "SMALL.JPG", "JPEG")
    newIm.paste(smWM, rightTopPlc)#(Start X,Start Y,End X, End Y)
    #im.show()#SHows the Image 
    #flash("Paste Completed")
    #savePrompt(newIm)
    wmSaved = newIm.save(photo_local + "Watermark.JPG", "JPEG")
    return send_file(photo_local + "Watermark.JPG", attachment_filename='WaterMarked.jpg')

def processBottomLeft(wm, im, userInput, photo_local, wm_local):
    newIm = Image.open(photo_local + "-1080.JPG")
    #Place a Image in the bottom right hand corner of the page - Where most photographers would put their watermark of a 1920x1080
    smSz = (250,100) #New Size of watermark
    rightTopPlc = (100,900,350,1000) #Location on Image
    smWM = wm.resize(smSz, Image.BILINEAR) #Resize Watermark to fit image
    savedWm = smWM.save(wm_local + "SMALL.JPG", "JPEG")
    newIm.paste(smWM, rightTopPlc)#(Start X,Start Y,End X, End Y)
    #im.show()#SHows the Image 
    #flash("Paste Completed")
    #savePrompt(newIm)
    wmSaved = newIm.save(photo_local + "Watermark.JPG", "JPEG")
    return send_file(photo_local + "Watermark.JPG", attachment_filename='WaterMarked.jpg')
    
def processBottomRight(wm, im, userInput, photo_local, wm_local):
    newIm = Image.open(photo_local + "-1080.JPG")
    #Place a Image in the bottom right hand corner of the page - Where most photographers would put their watermark of a 1920x1080
    smSz = (250,100) #New Size of watermark
    rightTopPlc = (1600,900,1850,1000) #Location on Image
    smWM = wm.resize(smSz, Image.BILINEAR) #Resize Watermark to fit image
    savedWm = smWM.save(wm_local + "SMALL.JPG", "JPEG")
    newIm.paste(smWM, rightTopPlc)#(Start X,Start Y,End X, End Y)
    #im.show()#SHows the Image 
    #flash("Paste Completed")
    #savePrompt(newIm)
    wmSaved = newIm.save(photo_local + "Watermark.JPG", "JPEG")
    return send_file(photo_local + "Watermark.JPG", attachment_filename='WaterMarked.jpg')
    