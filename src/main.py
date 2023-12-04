# ************************************ check if all modules are installed *********************************
import shutil
import os
import sys
import cv2
import piexif
import pytz
from PIL import Image
from datetime import datetime, timedelta

# ****************************************** preparation ******************************************

# set to False if you want to keep all images without Metadata
cleanUp = True

# create the output directory if it doesn't already exist
outputDir = 'output_frames'
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

videoPath = sys.argv[1]

# check if video exits and if is readable
if not os.path.exists(videoPath):
    print(f"Video file '{videoPath}' does not exist.")
    exit()

if not os.access(videoPath, os.R_OK):
    print(f"Cannot read the video file '{videoPath}'.")
    exit()

nmeaPath = sys.argv[2]

# check if nmea exits and if is readable
if not os.path.exists(nmeaPath):
    print(f"NMEA file '{nmeaPath}' does not exist.")
    exit()

if not os.access(nmeaPath, os.R_OK):
    print(f"Cannot read the NMEA file '{nmeaPath}' .")
    exit()

# open the video file
videoCap = cv2.VideoCapture(videoPath)

# get Frame rate
frameRate = int(videoCap.get(cv2.CAP_PROP_FPS))
frameCounter = 0
sortingNumber = 0


"""
    Because NMEA is in UTC and in Germany its CEST I first have to look if its winter or summer time
"""
def IsSummerTime(timeZoneString):
    timeZone = pytz.timezone(timeZoneString)
    now = datetime.now(timeZone)
    return now.dst() != timedelta(0)


isSummer = IsSummerTime("Europe/Berlin")

if isSummer == True:
    plusUTC = 2
else:
    plusUTC = 1

# ****************************************** extract the frames ******************************************

# loop through the frames in the video
while videoCap.isOpened():
    ret, frame = videoCap.read()
    if not ret:
        break

    frameCounter += 1
    # if the frame counter is divisible by the interval, extract the frame
    if frameCounter % frameRate == 0:
        frame_filename = os.path.join(outputDir, f'{sortingNumber:05d}.jpg')
        cv2.imwrite(frame_filename, frame)
        sortingNumber += 1

videoCap.release()
# ****************************************** extract the nmea Strings ******************************************

"""
    Array for all the lines in the NMEA FIle -> only read the $GPGGA lines
    get also the timestamp
"""
arrayNMEAString = []

with open(nmeaPath, 'r') as nmeaFile:
    for line in nmeaFile:
        if line.startswith('$GPGGA'):
            arrayNMEAString.append(line.strip())
            print(arrayNMEAString)

# ****************************************** write the metadata ******************************************

outputDirComp = 'outputJPGGPS'
if not os.path.exists(outputDirComp):
    os.makedirs(outputDirComp)

# give the place in the array of the nmea string
count = 0

# check for enough NMEA data to write -> only imported for the print statement
firstCheckNMEA = False


def CalcGPSinEXIF(decimalDegrees):
    """
    example: 6724.449
    degrees = int(6724.449 / 100) = 67
    minutes = int(6724.449 - (67 * 100)) = int(6724.449 - 6700) = int(24.449) = 24
    decimalMinutes = 6724.449 - (67 * 100) - 24 = 24.449 - 24 = 0.449
    seconds = int(0.449 * 60) = int(26.94) = 26

    return (67, 1), (24, 1), (26, 1)
    -> The 1 mean that the value is finished -> (6700, 100) would be converted into 67
    """
    degrees = int(decimalDegrees / 100)
    minutes = int(decimalDegrees - (degrees * 100))
    decimalMinutes = decimalDegrees - (degrees * 100) - minutes
    seconds = int(decimalMinutes * 60)

    return (degrees, 1), (minutes, 1), (seconds, 1)


# sorted the files from 0 to the highest numer and write the metadata
for fileName in sorted(os.listdir('output_frames')):
    if fileName.endswith('.jpg'):
        imgPath = os.path.join('output_frames', fileName)

        if count < len(arrayNMEAString):
            exifDict = piexif.load(imgPath)

            gpsLatRef = arrayNMEAString[count].split(',')[3]
            gpsLongRef = arrayNMEAString[count].split(',')[5]

            gpsLat = CalcGPSinEXIF(float(arrayNMEAString[count].split(',')[2]))
            gpsLong = CalcGPSinEXIF(float(arrayNMEAString[count].split(',')[4]))

            gpsIfd = {
                piexif.GPSIFD.GPSLatitude: gpsLat,
                piexif.GPSIFD.GPSLatitudeRef: gpsLatRef.encode(),
                piexif.GPSIFD.GPSLongitude: gpsLong,
                piexif.GPSIFD.GPSLongitudeRef: gpsLongRef.encode()
            }

            exifDict["GPS"] = gpsIfd

            exifBytes = piexif.dump(exifDict)
            img = Image.open(imgPath)
            img.save(os.path.join(outputDirComp, fileName), exif=exifBytes)
        else:
            shutil.copy(imgPath, os.path.join(outputDirComp, fileName))
            if firstCheckNMEA == False:
                endWrittenImage = fileName
                checkNMEA = True
        count += 1

if firstCheckNMEA:
    print(f"Metadata written up to image {endWrittenImage}")

# ****************************************** clean up ******************************************

# delete all images without GPS
if cleanUp:
    shutil.rmtree(outputDir)
