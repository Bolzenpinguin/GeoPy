import os.path
import tempfile
import pytest
from src.geopy import *



def test_WriteMetadataToImage():
    # TODO ----------------------------------------------------
    pass


def test_ProcessVideoAndNMEA():
    # TODO ----------------------------------------------------
    pass

def test_ExtractFramesFromVideo():
    sampleVideoPath = 'sample24Frames16Seconds.mp4'

    with tempfile.TemporaryDirectory() as tempOutputDir:
        video = cv2.VideoCapture(sampleVideoPath)

        frameRate = 24
        startFrame = 0

        ExtractFramesFromVideo(video, frameRate, tempOutputDir, startFrame)

        extractedFiles = os.listdir(tempOutputDir)
        expectedNumberOfFrames = 16
        assert len(extractedFiles) == expectedNumberOfFrames, "Incorrect number of frames"


def test_PrepareNMEAString():
    mockNMEAData = [
        "$GPGGA,095805.000,5247.568,N,01309.697,E,1,12,1.0,0.0,M,0.0,M,,*63",
        "$GPGGA,095806.000,5221.681,N,01315.630,E,1,12,1.0,0.0,M,0.0,M,,*64",
        "$GPGGA,095807.000,5124.364,N,01234.761,E,1,12,1.0,0.0,M,0.0,M,,*6A"
    ]

    # create temp NMEA file
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tempNMEAFile:
        tempNMEAFile.writelines('\n'.join(mockNMEAData))
        tempNMEAFileName = tempNMEAFile.name

    try:
        # Bitmask for the lines
        bitmask = [True, False, True]
        nmeaStartLineTest = 0

        expectedOutput = [mockNMEAData[0], None, mockNMEAData[2]]
        actualOutput = PrepareNMEAString(tempNMEAFileName, bitmask, nmeaStartLineTest)

        assert actualOutput == expectedOutput, "Output missmatch Input"
    finally:
        os.remove(tempNMEAFileName)


def test_ExtractGPSDataFromNMEAString():
    sampleNMEA = "$GPGGA,095805.000,5247.568,N,01309.697,E,1,12,1.0,0.0,M,0.0,M,,*63"

    expectedLatRef = "N"
    expectedLongRef = "E"

    expectedLat = CalcGPSinEXIF(5247.568)
    expectedLong = CalcGPSinEXIF(01309.697)

    # extracting the values
    latRef, longRef, lat, long = ExtractGPSDataFromNMEAString(sampleNMEA)

    assert latRef == expectedLatRef, "Latitude Reference missmatch"
    assert longRef == expectedLongRef, "Longitude Reference missmatch"
    assert lat == expectedLat, "Latitude value missmatch"
    assert long == expectedLong, "Longitude value missmatch"

def test_CheckPathStartFiles():
    # path exists
    existingPath = '.'  # -> current Directory
    try:
        CheckPathStartFiles(existingPath)
    except FileNotFoundError:
        pytest.fail(f"Unexpected FileNotFoundError for path: {existingPath}")

    # path doesn't exit
    nonExistingPath = 'random/Path'
    with pytest.raises(FileNotFoundError):
        CheckPathStartFiles(nonExistingPath)


def test_CheckReadability():
    # path readable
    readablePath = '.'  # -> current Directory -> definitely readable
    try:
        CheckReadability(readablePath)
    except PermissionError:
        pytest.fail(f"Unexpected PermissionError for path: {readablePath}")

    # path not readable
    nonReadablePath = 'testNonReadable.txt'
    try:
        # create the non-readable file
        with open(nonReadablePath, 'w'):
            os.chmod(nonReadablePath, 0o000)

        with pytest.raises(PermissionError):
            CheckReadability(nonReadablePath)
    finally:
        # delete test file
        os.remove(nonReadablePath)


def test_CreateDir():
    nameDri = 'testDir'
    try:
        assert CreateDir(nameDri) is True, "CreateDir did not return True"

        assert os.path.isdir(nameDri), "Directory wasn't created"
    finally:
        if os.path.exists(nameDri):
            os.rmdir(nameDri)  # remove testdir


def test_CountGPGGALines():
    testNMEAFile = 'testNMEAFile.nmea'
    expectedCount = 3

    with open(testNMEAFile, 'w') as file:
        file.write('$GPGGA, line 1\n')
        file.write('Test line \n')
        file.write('$GPGGA, line 2\n')
        file.write('$GPGGA, line 3\n')

    try:
        actualCount = CountGPGGALines(testNMEAFile)
        assert actualCount == expectedCount, f"Expected {expectedCount} but got {actualCount}"
    finally:
        # Cleanup
        os.remove(testNMEAFile)


def test_ReadAndParseBitMask():
    testBitMaskFile = 'testBitMask.txt'
    expectedBitMask = [True, False, True, True]

    with open(testBitMaskFile, 'w') as file:
        file.write('1011')

    try:
        actualBitMask = ReadAndParseBitMask(testBitMaskFile)
        assert actualBitMask == expectedBitMask, f"Expected {expectedBitMask} but got {actualBitMask}"
    finally:
        # cleanup
        os.remove(testBitMaskFile)


def test_MatchBitMaskGPGGA():
    lengthBit = 5
    lengthGPGPU = 5

    # if they are equal
    try:
        MatchBitMaskGPGGA(lengthBit, lengthGPGPU)
    except SystemExit:
        pytest.fail("Unexpected exit")

    # if they are not equal
    lengthBit = 4
    lengthGPGPU = 5
    with pytest.raises(SystemExit):
        MatchBitMaskGPGGA(lengthBit, lengthGPGPU)


def test_CalcGPSinEXIF():
    example = 6724.449

    degrees = int(example / 100)
    minutes = int(example - (degrees * 100))
    decimalMinutes = example - (degrees * 100) - minutes
    seconds = int(decimalMinutes * 60)

    testDecimalDegree = (degrees, 1), (minutes, 1), (seconds, 1)
    actualDecimalDegree = CalcGPSinEXIF(example)

    assert actualDecimalDegree == testDecimalDegree, f"Expected {testDecimalDegree} but got {actualDecimalDegree}"
