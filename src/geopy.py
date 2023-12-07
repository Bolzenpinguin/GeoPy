# ************************************ Import Modules *********************************
import shutil
import os
import sys
import cv2
import piexif
from PIL import Image


# ************************************ Function Definitions *********************************

def CheckPathStartFiles(path):
    """
    Checks if the given path exists
    :param path: Path as a String Value
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File in '{path}' does not exist.")


def CheckReadability(path):
    """
    Checks if the given path is readable
    :param path: Path as a String Value
    """
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Cannot read the file '{path}'.")


def CreateDir(name):
    """
    Create a directory if it not exists
    :param name: Name of the directory as String
    """
    if not os.path.exists(name):
        os.makedirs(name)
    return os.path.isdir(name)


def ExtractFramesFromVideo(video, frameRate, outputDir, startFrame):
    """
    Extracts frames from the video file.
    :param video: Open Video File
    :param frameRate: Frame rate of the video
    :param outputDir: Directory to save frames
    :param startFrame: Starting frame position in the video
    """
    frameCounter = startFrame
    frameSortingNumber = 0

    video.set(cv2.CAP_PROP_POS_FRAMES, startFrame)

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        if frameCounter % frameRate == 0:
            frameFilename = os.path.join(outputDir, f'{frameSortingNumber:05d}.jpg')
            cv2.imwrite(frameFilename, frame)
            frameSortingNumber += 1
        frameCounter += 1
        # print(f"Frame: {frameCounter}")
    video.release()


def CountGPGGALines(nmeaPathCounting):
    """
    Counts the number of GPGGA lines in the NMEA file
    :param nmeaPathCounting: Path to the NMEA File
    :return: Number of GPGGA lines
    """
    gpggaCount = 0
    with open(nmeaPathCounting, 'r') as nmeaFile:
        for line in nmeaFile:
            if line.startswith('$GPGGA'):
                gpggaCount += 1
    return gpggaCount


def ReadAndParseBitMask(bitMaskPathReadAndParse):
    """
    Reads and parses the bit mask file as boolean in an array
    :param bitMaskPathReadAndParse: Path to the Bit Mask File
    :return: Bit mask array
    """
    with open(bitMaskPathReadAndParse, 'r') as bitMaskFile:
        bitMaskString = bitMaskFile.read().strip()
        bitMask = [bool(int(bit)) for bit in bitMaskString]
    return bitMask


def MatchBitMaskGPGGA(lengthBit, lengthGPGGA):
    """
    Compares the length of bit mask with the number of GPGGA lines
    :param lengthBit: Length of the bit mask
    :param lengthGPGGA: Number of GPGGA lines
    """
    if lengthBit != lengthGPGGA:
        if lengthBit < lengthGPGGA:
            exit(f"Bit mask ({lengthBit}) is shorter than the number of $GPGGA lines ({lengthGPGGA})")


def PrepareNMEAString(nmeaPathPreparing, bitMaskPreparing, nmeaStartLinePreparing):
    """
    Prepares the NMEA string based on the bit mask, positions with False get set to None
    :param nmeaPathPreparing: Path to the NMEA File
    :param bitMaskPreparing: Bit Mask array
    :param nmeaStartLinePreparing: Starting line of the NMEA data
    :return: Array of NMEA strings
    """

    arrayNMEA = []
    gpggaIndex = 0

    with open(nmeaPathPreparing, 'r') as nmeaFile:
        for index, line in enumerate(nmeaFile):
            if line.startswith('$GPGGA') and index >= nmeaStartLinePreparing:
                if gpggaIndex < len(bitMaskPreparing):
                    if bitMaskPreparing[gpggaIndex]:
                        arrayNMEA.append(line.strip())
                    else:
                        arrayNMEA.append(None)
                gpggaIndex += 1
                # print(f"NMEA line: {index}")
    return arrayNMEA


def CalcGPSinEXIF(decimalDegrees):
    """
    :param decimalDegrees: Decimal degree value
    :return: GPS data in EXIF format

    example: 6724.449 \n
    degrees = int(6724.449 / 100) = 67 \n
    minutes = int(6724.449 - (67 * 100)) = int(6724.449 - 6700) = int(24.449) = 24 \n
    decimalMinutes = 6724.449 - (67 * 100) - 24 = 24.449 - 24 = 0.449 \n
    seconds = int(0.449 * 60) = int(26.94) = 26 \n

    return (67, 1), (24, 1), (26, 1) \n
    -> The 1 means that the value is finished -> (6700, 100) would be converted into 67
    """
    degrees = int(decimalDegrees / 100)
    minutes = int(decimalDegrees - (degrees * 100))
    decimalMinutes = decimalDegrees - (degrees * 100) - minutes
    seconds = int(decimalMinutes * 60)

    return (degrees, 1), (minutes, 1), (seconds, 1)


def ExtractGPSDataFromNMEAString(nmeaString):
    """
    Extracts GPS data from NMEA string
    :param nmeaString: A single NMEA string
    :return: Tuple containing GPS latitude reference, longitude reference, latitude, and longitude.
    """
    gpsLatRef = nmeaString.split(',')[3]
    gpsLongRef = nmeaString.split(',')[5]
    gpsLat = CalcGPSinEXIF(float(nmeaString.split(',')[2]))
    gpsLong = CalcGPSinEXIF(float(nmeaString.split(',')[4]))
    return gpsLatRef, gpsLongRef, gpsLat, gpsLong


def WriteMetadataToImage(outputFramesDir, arrayNMEAString, outputDirComp):
    """
    Writes metadata to images based on the NMEA string
    :param outputFramesDir: Directory containing the frame images.
    :param arrayNMEAString: Array of NMEA strings corresponding to each image.
    :param outputDirComp: Directory where the processed images will be saved.
    """
    count = 0
    firstCheckNMEA = False
    endWrittenImage = None

    # Iterate through sorted images and write metadata
    for fileName in sorted(os.listdir(outputFramesDir)):
        if fileName.endswith('.jpg'):
            imgPath = os.path.join(outputFramesDir, fileName)

            if count < len(arrayNMEAString):
                if arrayNMEAString[count] is not None:
                    exifDict = piexif.load(imgPath)
                    gpsLatRef, gpsLongRef, gpsLat, gpsLong = ExtractGPSDataFromNMEAString(arrayNMEAString[count])

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
            else:
                shutil.copy(imgPath, os.path.join(outputDirComp, fileName))
                if not firstCheckNMEA:
                    endWrittenImage = fileName
                    firstCheckNMEA = True
            count += 1

    if firstCheckNMEA:
        print(f"No Metadata written up Image: {endWrittenImage}")


def ProcessVideoAndNMEA(videoPathGiven, nmeaPathGiven, bitMaskPathGiven, videoStartFrameGiven, nmeaStartLineGiven,
                        cleanUpGiven):
    """
    Main processing function for video and NMEA data
    :param videoPathGiven: Path to the video file
    :param nmeaPathGiven: Path to the NMEA file
    :param bitMaskPathGiven: Path to the Bit Mask file
    :param videoStartFrameGiven: Start frame of video
    :param nmeaStartLineGiven: Start line of NMEA data
    :param cleanUpGiven: Boolean removes images without metadat
    """
    outputDir = 'output_frames'
    CreateDir(outputDir)

    outputDirComp = 'outputJPGGPS'
    CreateDir(outputDirComp)

    CheckPathStartFiles(videoPathGiven)
    CheckReadability(videoPathGiven)

    videoCap = cv2.VideoCapture(videoPathGiven)
    frameRate = int(videoCap.get(cv2.CAP_PROP_FPS))
    ExtractFramesFromVideo(videoCap, frameRate, outputDir, videoStartFrameGiven)

    CheckPathStartFiles(nmeaPathGiven)
    CheckReadability(nmeaPathGiven)
    gpggaCount = CountGPGGALines(nmeaPathGiven)

    CheckPathStartFiles(bitMaskPathGiven)
    CheckReadability(bitMaskPathGiven)
    bitMask = ReadAndParseBitMask(bitMaskPathGiven)

    MatchBitMaskGPGGA(len(bitMask), gpggaCount)
    arrayNMEAString = PrepareNMEAString(nmeaPathGiven, bitMask, nmeaStartLineGiven)

    WriteMetadataToImage(outputDir, arrayNMEAString, outputDirComp)

    if cleanUpGiven:
        shutil.rmtree(outputDir)


# ************************************ Main Script *********************************
if __name__ == "__main__":

    # Check for arguments
    if len(sys.argv) < 6:
        sys.exit("Usage: geopy.py [videoPath] [nmeaPath] [bitMaskPath] [videoStartFrame] [nmeaStartLine]")

    videoPath = sys.argv[1]
    nmeaPath = sys.argv[2]
    bitMaskPath = sys.argv[3]
    videoStartFrame = int(sys.argv[4])
    nmeaStartLine = int(sys.argv[5])
    cleanUp = True  # False if you want to keep images without metadata

    # start the script
    ProcessVideoAndNMEA(videoPath, nmeaPath, bitMaskPath, videoStartFrame, nmeaStartLine, cleanUp)
