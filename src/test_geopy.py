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
    with tempfile.TemporaryDirectory() as tempDir:
        # temporary directory
        existingPath = tempDir
        try:
            CheckPathStartFiles(existingPath)
        except FileNotFoundError:
            pytest.fail(f"Unexpected FileNotFoundError for path: {existingPath}")

        # Non-existing path
        nonExistingPath = 'random/Path'
        with pytest.raises(FileNotFoundError):
            CheckPathStartFiles(nonExistingPath)


def test_CheckReadability():
    with tempfile.NamedTemporaryFile(delete=False) as tempFile:
        readablePath = tempFile.name
        try:
            CheckReadability(readablePath)
        except PermissionError:
            pytest.fail(f"Unexpected PermissionError for path: {readablePath}")

        # Non-readable path scenario remains the same
        nonReadablePath = 'testNonReadable.txt'
        with open(nonReadablePath, 'w'):
            os.chmod(nonReadablePath, 0o000)
        try:
            with pytest.raises(PermissionError):
                CheckReadability(nonReadablePath)
        finally:
            os.remove(nonReadablePath)


def test_CreateDir():
    with tempfile.TemporaryDirectory() as tempDir:
        nameDir = os.path.join(tempDir, 'testDir')
        assert CreateDir(nameDir) is True, "CreateDir did not return True"
        assert os.path.isdir(nameDir), "Directory wasn't created"


def test_CountGPGGALines():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tempNMEAFile:
        tempNMEAFilePath = tempNMEAFile.name
        tempNMEAFile.write('$GPGGA, line 1\n'
                           'Test line \n'
                           '$GPGGA, line 2\n'
                           '$GPGGA, line 3\n')

    try:
        actualCount = CountGPGGALines(tempNMEAFilePath)
        expectedCount = 3
        assert actualCount == expectedCount, f"Expected {expectedCount} but got {actualCount}"
    finally:
        os.remove(tempNMEAFilePath)


def test_ReadAndParseBitMask():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tempBitMaskFile:
        tempBitMaskFilePath = tempBitMaskFile.name
        tempBitMaskFile.write('1011')

    try:
        actualBitMask = ReadAndParseBitMask(tempBitMaskFilePath)
        expectedBitMask = [True, False, True, True]
        assert actualBitMask == expectedBitMask, f"Expected {expectedBitMask} but got {actualBitMask}"
    finally:
        os.remove(tempBitMaskFilePath)


def test_MatchBitMaskGPGGA():
    lengthBit = 5
    lengthGPGGA = 5
    try:
        MatchBitMaskGPGGA(lengthBit, lengthGPGGA)
    except SystemExit:
        pytest.fail("Unexpected exit")

    lengthBit = 4
    lengthGPGGA = 5
    with pytest.raises(SystemExit):
        MatchBitMaskGPGGA(lengthBit, lengthGPGGA)


def test_CalcGPSinEXIF():
    example = 6724.449

    testDecimalDegree = CalcGPSinEXIF(example)
    degrees = int(example / 100)
    minutes = int(example - (degrees * 100))
    decimalMinutes = example - (degrees * 100) - minutes
    seconds = int(decimalMinutes * 60)
    expectedDecimalDegree = (degrees, 1), (minutes, 1), (seconds, 1)

    assert testDecimalDegree == expectedDecimalDegree, f"Expected {expectedDecimalDegree} but got {testDecimalDegree}"
