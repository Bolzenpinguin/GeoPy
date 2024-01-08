# GeoPy

GeoPy is a Python program that splits an MP4 movie into frames
and assigns GPS data to these frames using the values from a NMEA file. 

## Arguments

- argv0: Path to the video file
- argv1: Path to the NMEA string file
- argv2: Path to the boolean bitmask file (specifies which NMEA lines to use)
- argv3: Start of the first frame (set to 0 to begin from the start, or specify the exact frame number, e.g., 724)
- argv4: Start of line from NMEA file 

## How to Use
1. Make sure that you have an MP4 video file, a NMEA file and a bitmask file ready. The NMEA file must contain GPS data in the '$GPGGA' format and the bitmask file should only be a sequence of boolean values.
2. Now you can execute the script with the required arguments like this:
    ```python geopy.py /path/to/video.mp4 /path/to/nmea.txt /path/to/bitmask.txt 0 0``` 
   
    This will process the video from the beginning and use the NMEA from the start.

## Functionality Overview
### CheckPathStartFiles(pathFunc)
**Description:** Checks the existence of a given file path.

**Usage:** 
```CheckPathStartFiles("path/to/video.mp4")```

### CheckReadability(pathFunc)
**Description:** Checks if the path is readable.

**Usage:**
```CheckReadability("path/to/video.mp4") ```

### CreateDir(nameFunc)
**Description:** Checks if directory doesn't exist and create it otherwise.

**Usage:**
```CreateDir("output_frames")``` 

### ExtractFramesFromVideo(videoFunc, frameRateFunc, outputDirFunc, startFrameFunc)
**Description:** Extracts frames from the video file at a given frame rate starting from a specified frame (like 0 in the example).

**Usage:**
``` 
videoCap = cv2.VideoCapture(videoPath) 
frameRate = int(videoCap.get(cv2.CAP_PROP_FPS))
ExtractFramesFromVideo(videoCap, frameRate, "output_frames", 0) 
```

### CountGPGGALines(nmeaPathCountingFunc)
**Description:** Counts the '$GPGGA' lines in the NMEA file.

**Usage:** ```gpggaCount = CountGPGGALines("/path/to/nmea.txt")```

### ReadAndParseBitMask(bitMaskPathReadAndParseFunc)
**Description:** Reads a bitmask file and converts it into a boolean array.

**Usage:** ```bitMask = ReadAndParseBitMask("/path/to/bitmask.txt")```


### MatchBitMaskGPGGA(lengthBitFunc, lengthGPGGAFunc)
**Description:** Compares the length of the bitmask with the number of '$GPGGA' lines and ensure that the lines of the bit mask and the GPGGA lines match. 

**Usage:** ```MatchBitMaskGPGGA(len(bitMask), gpggaCount)```

### PrepareNMEAString(nmeaPathPreparingFunc, bitMaskPreparingFunc, nmeaStartLinePreparingFunc)
**Description:** Processes the NMEA string based on the bitmask, setting unwanted values to 'None'.

**Usage:** ```arrayNMEAString = PrepareNMEAString(nmeaPath, bitMask, nmeaStartLine)```

### CalcGPSinEXIF(decimalDegreesFunc)
**Description:** Converts decimal degree values to GPS data in EXIF format.

**Usage:** ```gpsLat = CalcGPSinEXIF(6724.449)```

### ExtractGPSDataFromNMEAString(nmeaStringFunc)
**Description:** Extracts GPS latitude and longitude data from an NMEA string.

**Usage:** ```gpsData = ExtractGPSDataFromNMEAString(nmeaString)```

### WriteMetadataToImage(outputFramesDirFunc, arrayNMEAStringFunc, outputDirCompFunc)
**Description:** Writes GPS metadata to images based on the NMEA string values.

**Usage:** ```WriteMetadataToImage("output_frames", arrayNMEAString, "outputJPGGPS")```
