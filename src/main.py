# ************************************ check if all modules are installed *********************************
import shutil
import platform
import subprocess
import os
import sys

# set to False if you want to keep all images without Metadata
cleanUp = True

try:
    import cv2
except ModuleNotFoundError:
    print("Module cv2 is not installed, please install it first.")
    exit(2)

try:
    import piexif
except ModuleNotFoundError:
    print("Module piexif is not installed, please install it first.")
    exit(4)

try:
    from PIL import Image
except ModuleNotFoundError:
    print("Module PIL is not installed, please install it first.")
    exit(5)

# ****************************************** extract the frames ******************************************

# create the output directory if it doesn't already exist
outputDir = 'output_frames'
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

videoPath = sys.argv[1]

# check if video exits and if is readable
if not os.path.exists(videoPath):
    print(f"Video file '{videoPath}' does not exist.")
    exit(6)

if not os.access(videoPath, os.R_OK):
    print(f"Cannot read the video file '{videoPath}'.")
    exit(7)

# open the video file
videoCap = cv2.VideoCapture(videoPath)

# initialize frame counter and interval
frameCounter = 0
interval = 30  # extract one frame every 30 frames ( = every second)

# loop through the frames in the video
while videoCap.isOpened():
    # read the next frame
    ret, frame = videoCap.read()

    if ret:
        # increment the frame counter
        frameCounter += 1

        # if the frame counter is divisible by the interval, extract the frame
        if frameCounter % interval == 0:
            # save the frame as an image file
            frameFilename = os.path.join(outputDir, f'frame{frameCounter}.jpg')
            cv2.imwrite(frameFilename, frame)

    else:
        # if reached the end of the video, break out of the loop
        break

# release the video file
videoCap.release()

# ****************************************** extract the nmea Strings ******************************************

nmeaPath = sys.argv[2]

# check if nmea exits and if is readable
if not os.path.exists(nmeaPath):
    print(f"NMEA file '{nmeaPath}' does not exist.")
    exit(8)

if not os.access(nmeaPath, os.R_OK):
    print(f"Cannot read the NMEA file '{nmeaPath}' .")
    exit(9)

# Array for all the lines in the NMEA FIle -> only read the $GPGGA lines
arrayNMEAString = []

with open(nmeaPath, 'r') as nmeaFile:
    for line in nmeaFile:
        if line.startswith('$GPGGA'):
            arrayNMEAString.append(line.strip())

# ****************************************** write the metadata ******************************************

# create output Folder
outputDirComp = 'outputJPGGPS'
if not os.path.exists(outputDirComp):
    os.makedirs(outputDirComp)

# give the place in the array of the nmea string
count = 0

# calculate the GPS times
def calcGPS(number):
    degrees = int(number // 100)
    minutes = int(number % 100)
    centiseconds = int(((number % 100) * 100) % 100)

    return ((degrees, 1), (minutes, 1), (centiseconds, 100))


# loop through all JPG files in output_frames
for fileName in os.listdir('output_frames'):
    if fileName.endswith('.jpg'):
        # load image and original metadat
        imgPath = os.path.join('output_frames', fileName)
        exifDict = piexif.load(imgPath)

        # if there are fewer points then frames, last point is set as default
        if count >= len(arrayNMEAString):
            count = len(arrayNMEAString) - 1

        # get the data
        gpsLatRef = arrayNMEAString[count].split(',')[3].encode()
        gpsLongRef = arrayNMEAString[count].split(',')[5].encode()

        gpsLat = calcGPS(float(arrayNMEAString[count].split(',')[2]))
        gpsLong = calcGPS(float(arrayNMEAString[count].split(',')[4]))

        # modify GPS metadata
        gpsIfd = {
            piexif.GPSIFD.GPSLongitude: gpsLong,
            piexif.GPSIFD.GPSLongitudeRef: gpsLongRef,
            piexif.GPSIFD.GPSLatitude: gpsLat,
            piexif.GPSIFD.GPSLatitudeRef: gpsLatRef
        }

        exifDict["GPS"] = gpsIfd

        # save modified images to output folder
        exifBytes = piexif.dump(exifDict)
        img = Image.open(imgPath)
        img.save(os.path.join(outputDirComp, fileName), exif=exifBytes)
        count = count + 1

# ****************************************** clean up ******************************************

# delete all images without GPS
if cleanUp:
    shutil.rmtree(outputDir)

# open folder with the images
def openFile(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

openFile(outputDirComp)

