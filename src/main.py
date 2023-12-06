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


def CheckPathStartFiles(path):
    """
    :param path: Path as a String Value
    """
    if not os.path.exists(path):
        exit(f"File in '{path}' dose not exist.")


def ChekReadabllty(path):
    """
    :param path: Path as a String Value
    """
    if not os.access(path, os.R_OK):
        exit(f"Cannot read the file '{path}' .")


def CreateDir(name):
    """
    :param name: check if there is a folder, if not create one
    """
    if not os.path.exists(name):
        os.makedirs(name)


# create the directories if they don't already exist
outputDir = 'output_frames'
CreateDir(outputDir)

outputDirComp = 'outputJPGGPS'
CreateDir(outputDirComp)

videoPath = sys.argv[1]

# check if video exits and if is readable
CheckPathStartFiles(videoPath)
ChekReadabllty(videoPath)

nmeaPath = sys.argv[2]

# check if nmea exits and if is readable
CheckPathStartFiles(nmeaPath)
ChekReadabllty(nmeaPath)

# open the video file
videoCap = cv2.VideoCapture(videoPath)

# get Frame rate
frameRate = int(videoCap.get(cv2.CAP_PROP_FPS))

bitMaskPath = sys.argv[3]

# Check if bit mask file exists and is readable
CheckPathStartFiles(bitMaskPath)
ChekReadabllty(bitMaskPath)


# ****************************************** extract the frames ******************************************

def ExtractFramesFromVideo(videoCap, frameRate, outputDir):
    """
    :param videoCap: open Video File
    :param frameRate: from the open Video
    :param outputDir: There the frames should be saved (temporally if you set cleanup True)

    Loop through the frames in the video, if the frame counter is divisible by the interval, extracts the frame
    """
    frameCounter = 0
    sortingNumber = 0

    while videoCap.isOpened():
        ret, frame = videoCap.read()
        if not ret:
            break
        frameCounter += 1
        if frameCounter % frameRate == 0:
            frame_filename = os.path.join(outputDir, f'{sortingNumber:05d}.jpg')
            cv2.imwrite(frame_filename, frame)
            sortingNumber += 1

    videoCap.release()


# Calling the function
ExtractFramesFromVideo(videoCap, frameRate, outputDir)


# ****************************************** extract the nmea Strings ******************************************

def CountGPGGALines(nmeaPath):
    """
    :param nmeaPath: Path to the NMEA File as String
    :return: number of lines as int
    """
    gpggaCount = 0
    with open(nmeaPath, 'r') as nmeaFile:
        for line in nmeaFile:
            if line.startswith('$GPGGA'):
                gpggaCount += 1
    return gpggaCount


# Count the number of $GPGGA lines in the NMEA file
gpggaCount = CountGPGGALines(nmeaPath)


def ReadAndParseBitMask(bitMaskPath):
    """
    :param bitMaskPath: Path to the Bit Mask as String
    :return: the bit mask as array with bool values
    with open -> File open and close if finish with reading ('r')
    strip -> delete space in front or end of the bit mask
    bitMask = [bool(int(bit)) for bit in bitMaskString] -> parse the integer as bool values
    """
    with open(bitMaskPath, 'r') as bitMaskFile:
        bitMaskString = bitMaskFile.read().strip()
        bitMask = [bool(int(bit)) for bit in bitMaskString]
    return bitMask


# Read and parse the bit mask
bitMask = ReadAndParseBitMask(bitMaskPath)


def MatchBitMaskGPGGA(lengthBit, lengthGPGGA):
    """
    :param lengthBit: length from array bit mask as int
    :param lengthGPGGA: int-counted lines from NMEA File
    :return: only throw the error if the bit mask is shorter than the gpgga file
    """
    if lengthBit != lengthGPGGA:
        if lengthBit < lengthGPGGA:
            exit(f"Bit mask ({lengthBit}) is shorter than the number of $GPGGA lines ({lengthGPGGA})")


# Check if the lengths match
MatchBitMaskGPGGA(len(bitMask), gpggaCount)


def PrepareNMEAString(nmeaPath, bitMask):
    """
    :param nmeaPath: Path to the NMEA File as String
    :param bitMask: bit Mask already converted into True and False
    :return: THe array with the places that should not be included (False) declared as None -> no value
    gpggaIndex is for comparison the place to the correct place in the bit mask
    """
    arrayNMEA = []
    gpggaIndex = 0

    with open(nmeaPath, 'r') as nmeaFile:
        for line in nmeaFile:
            if line.startswith('$GPGGA'):
                if gpggaIndex < len(bitMask):
                    if bitMask[gpggaIndex] == True:
                        arrayNMEA.append(line.strip())
                    else:
                        arrayNMEA.append(None)
                gpggaIndex += 1
    return arrayNMEA


# get the nmea Array with the mathing bit mask values
arrayNMEAString = PrepareNMEAString(nmeaPath, bitMask)

# ****************************************** write the metadata ******************************************

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
    -> The 1 means that the value is finished -> (6700, 100) would be converted into 67
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
            # Check if the NMEA string is None -> (Bit Mask) else copy without Metadata
            if arrayNMEAString[count] is not None:
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
                # copy image without Metadata
                shutil.copy(imgPath, os.path.join(outputDirComp, fileName))

            count += 1
        else:
            shutil.copy(imgPath, os.path.join(outputDirComp, fileName))
            if not firstCheckNMEA:
                endWrittenImage = fileName
                firstCheckNMEA = True
            count += 1

if firstCheckNMEA:
    print(f"Metadata written up to image {endWrittenImage}")

# ****************************************** clean up ******************************************

# delete all images without GPS
if cleanUp:
    shutil.rmtree(outputDir)
