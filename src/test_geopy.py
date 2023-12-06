import os

import pytest

from src.geopy import *


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
        with open(nonReadablePath, 'w') as f:
            os.chmod(nonReadablePath, 0o000)

        with pytest.raises(PermissionError):
            CheckReadability(nonReadablePath)
    finally:
        # delete test file
        os.remove(nonReadablePath)

