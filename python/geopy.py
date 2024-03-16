# ************************************ Import Modules *********************************
import argparse
import shutil
import os
import cv2
import piexif
from PIL import Image


# ************************************ Function Definitions *********************************

def CheckPathStartFiles(pathFunc):
    """
    :param pathFunc: Path as a String Value

    Checks if the given path exists
    """

    if not os.path.exists(pathFunc):
        raise FileNotFoundError(f"File in '{pathFunc}' does not exist.")


def CheckReadability(pathFunc):
    """
    :param pathFunc: Path as a String Value

    Checks if the given path is readable
    """

    if not os.access(pathFunc, os.R_OK):
        raise PermissionError(f"Cannot read the file '{pathFunc}'.")


def CreateDir(nameFunc):
    """
    :param nameFunc: Name of the directory as String

    Create a directory if it not exists
    """

    if not os.path.exists(nameFunc):
        os.makedirs(nameFunc)
    return os.path.isdir(nameFunc)


def ExtractFramesFromVideo(videoFunc, frameRateFunc, outputDirFunc, startFrameFunc):
    """
    :param videoFunc: Open Video File
    :param frameRateFunc: Frame rate of the video
    :param outputDirFunc: Directory to save frames
    :param startFrameFunc: Starting frame position in the video

    Extracts frames from the video file.
    """

    frameCounter = startFrameFunc
    frameSortingNumber = 0

    videoFunc.set(cv2.CAP_PROP_POS_FRAMES, startFrameFunc)

    while videoFunc.isOpened():
        success, frame = videoFunc.read()
        if not success:
            break
        if frameCounter % frameRateFunc == 0:
            frameFilename = os.path.join(outputDirFunc, f'{frameSortingNumber:05d}.jpg')
            cv2.imwrite(frameFilename, frame)
            frameSortingNumber += 1
        frameCounter += 1
        # print(f"Frame: {frameCounter}")
    videoFunc.release()


def CountGPGGALines(nmeaPathCountingFunc):
    """
    :param nmeaPathCountingFunc: Path to the NMEA File
    :return: Number of GPGGA lines

    Counts the number of GPGGA lines in the NMEA file
    """

    gpggaCount = 0
    with open(nmeaPathCountingFunc, 'r') as nmeaFile:
        for line in nmeaFile:
            if line.startswith('$GPGGA'):
                gpggaCount += 1
    return gpggaCount


def ReadAndParseBitMask(bitMaskPathReadAndParseFunc):
    """
    :param bitMaskPathReadAndParseFunc: Path to the Bit Mask File
    :return: Bit mask array

    Reads and parses the bit mask file as boolean in an array
    """

    with open(bitMaskPathReadAndParseFunc, 'r') as bitMaskFile:
        bitMaskString = bitMaskFile.read().strip()
        bitMask = [bool(int(bit)) for bit in bitMaskString]
    return bitMask


def MatchBitMaskGPGGA(lengthBitFunc, lengthGPGGAFunc):
    """
    :param lengthBitFunc: Length of the bit mask
    :param: lengthGPGGAFunc: Number of GPGGA lines

    Compares the length of bit mask with the number of GPGGA lines
    """

    if lengthBitFunc != lengthGPGGAFunc:
        if lengthBitFunc < lengthGPGGAFunc:
            exit(f"Bit mask ({lengthBitFunc}) is shorter than the number of $GPGGA lines ({lengthGPGGAFunc})")


def PrepareNMEAString(nmeaPathPreparingFunc, bitMaskPreparingFunc, nmeaStartLinePreparingFunc):
    """
    :param nmeaPathPreparingFunc: Path to the NMEA File
    :param bitMaskPreparingFunc: Bit Mask array
    :param nmeaStartLinePreparingFunc: Starting line of the NMEA data
    :return: Array of NMEA strings

    Prepares the NMEA string based on the bit mask, positions with False get set to None
    """

    arrayNMEA = []
    gpggaIndex = 0

    with open(nmeaPathPreparingFunc, 'r') as nmeaFile:
        for index, line in enumerate(nmeaFile):
            if line.startswith('$GPGGA') and index >= nmeaStartLinePreparingFunc:
                if gpggaIndex < len(bitMaskPreparingFunc):
                    if bitMaskPreparingFunc[gpggaIndex]:
                        arrayNMEA.append(line.strip())
                    else:
                        arrayNMEA.append(None)
                gpggaIndex += 1

    return arrayNMEA


def CalcGPSinEXIF(decimalDegreesFunc):
    """
    :param decimalDegreesFunc: Decimal degree value
    :return: GPS data in EXIF format

    example: 6724.449 \n
    degrees = int(6724.449 / 100) = 67 \n
    minutes = int(6724.449 - (67 * 100)) = int(6724.449 - 6700) = int(24.449) = 24 \n
    decimalMinutes = 6724.449 - (67 * 100) - 24 = 24.449 - 24 = 0.449 \n
    seconds = int(0.449 * 60) = int(26.94) = 26 \n

    return (67, 1), (24, 1), (26, 1) \n
    -> The 1 means that the value is finished -> (6700, 100) would be converted into 67
    """

    degrees = int(decimalDegreesFunc / 100)
    minutes = int(decimalDegreesFunc - (degrees * 100))
    decimalMinutes = decimalDegreesFunc - (degrees * 100) - minutes
    seconds = int(decimalMinutes * 60)

    return (degrees, 1), (minutes, 1), (seconds, 1)


def ExtractGPSDataFromNMEAString(nmeaStringFunc):
    """
    :param nmeaStringFunc: A single NMEA string
    :return: Tuple containing GPS latitude reference, longitude reference, latitude, and longitude.

    Extracts GPS data from NMEA string
    """

    gpsLatRef = nmeaStringFunc.split(',')[3]
    gpsLongRef = nmeaStringFunc.split(',')[5]
    gpsLat = CalcGPSinEXIF(float(nmeaStringFunc.split(',')[2]))
    gpsLong = CalcGPSinEXIF(float(nmeaStringFunc.split(',')[4]))
    return gpsLatRef, gpsLongRef, gpsLat, gpsLong


def WriteMetadataToImage(outputFramesDirFunc, arrayNMEAStringFunc, outputDirCompFunc):
    """
    :param outputFramesDirFunc: Directory containing the frame images.
    :param arrayNMEAStringFunc: Array of NMEA strings corresponding to each image.
    :param outputDirCompFunc: Directory where the processed images will be saved.

    Writes metadata to images based on the NMEA string
    """

    count = 0
    firstCheckNMEA = False
    endWrittenImage = None

    # Iterate through sorted images and write metadata
    for fileName in sorted(os.listdir(outputFramesDirFunc)):
        if fileName.endswith('.jpg'):
            imgPath = os.path.join(outputFramesDirFunc, fileName)

            if count < len(arrayNMEAStringFunc):
                if arrayNMEAStringFunc[count] is not None:
                    exifDict = piexif.load(imgPath)
                    gpsLatRef, gpsLongRef, gpsLat, gpsLong = ExtractGPSDataFromNMEAString(arrayNMEAStringFunc[count])

                    gpsIfd = {
                        piexif.GPSIFD.GPSLatitude: gpsLat,
                        piexif.GPSIFD.GPSLatitudeRef: gpsLatRef.encode(),
                        piexif.GPSIFD.GPSLongitude: gpsLong,
                        piexif.GPSIFD.GPSLongitudeRef: gpsLongRef.encode()
                    }

                    exifDict["GPS"] = gpsIfd
                    exifBytes = piexif.dump(exifDict)
                    img = Image.open(imgPath)
                    img.save(os.path.join(outputDirCompFunc, fileName), exif=exifBytes)
                else:
                    shutil.copy(imgPath, os.path.join(outputDirCompFunc, fileName))
            else:
                shutil.copy(imgPath, os.path.join(outputDirCompFunc, fileName))
                if not firstCheckNMEA:
                    endWrittenImage = fileName
                    firstCheckNMEA = True
            count += 1

    if firstCheckNMEA:
        print(f"No Metadata written up Image: {endWrittenImage}")


# ************************************ argparse ***********************************
parser = argparse.ArgumentParser(description="Get images from a MP4 File and write GPS positions to them.")
parser.add_argument("videoPath", help="Path to the video file as string")
parser.add_argument("nmeaPath", help="Path to the NMEA file as string")
parser.add_argument("bitMaskPath", help="Path to the boolean bitmask file (specifies which NMEA lines to use)")
parser.add_argument("videoStartFrame", type=int, help="Start of the first frame (set to 0 to begin from the start)")
parser.add_argument("nmeaStartLine", type=int, help="Start of the first line from the NMEA file (0 to begin from start")

args = parser.parse_args()

# ************************************ Main Script *********************************
if __name__ == "__main__":

    videoPath = args.videoPath
    nmeaPath = args.nmeaPath
    bitMaskPath = args.bitMaskPath
    videoStartFrame = args.videoStartFrame
    nmeaStartLine = args.nmeaStartLine

    cleanUp = True  # False if you want to keep images without metadata
    #bitMaskProvided = True  # False if not bitmask needed

    # start the script
    outputDir = 'output_frames'
    CreateDir(outputDir)

    outputDirComp = 'outputJPGGPS'
    CreateDir(outputDirComp)

    CheckPathStartFiles(videoPath)
    CheckReadability(videoPath)

    videoCap = cv2.VideoCapture(videoPath)
    frameRate = int(videoCap.get(cv2.CAP_PROP_FPS))
    ExtractFramesFromVideo(videoCap, frameRate, outputDir, videoStartFrame)

    CheckPathStartFiles(nmeaPath)
    CheckReadability(nmeaPath)
    gpggaCount = CountGPGGALines(nmeaPath)

    CheckPathStartFiles(bitMaskPath)
    CheckReadability(bitMaskPath)
    bitMask = ReadAndParseBitMask(bitMaskPath)

    MatchBitMaskGPGGA(len(bitMask), gpggaCount)
    arrayNMEAString = PrepareNMEAString(nmeaPath, bitMask, nmeaStartLine)

    WriteMetadataToImage(outputDir, arrayNMEAString, outputDirComp)

    if cleanUp:
        shutil.rmtree(outputDir)
