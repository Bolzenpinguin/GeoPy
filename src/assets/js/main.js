// Get Elements by ID
const elements = {
    videoPath: document.getElementById('videoPath'),
    nmeaPath: document.getElementById('nmeaPath'),
    savePath: document.getElementById('browseSavePath'),
    bitmaskPath: document.getElementById('pathToBitmask'),
    firstFrame: document.getElementById('firstFrame'),
    firstNMEALine: document.getElementById('firstNMEALine'),
    cleanup: document.getElementById('cleanup'),
    startBtn: document.getElementById('btnStart'),
    accordionBtn: document.querySelector('.accordion')
};

// Open Accordion
elements.accordionBtn.addEventListener('click', function () {
    this.classList.toggle('active');
    const panel = this.nextElementSibling;
    panel.style.maxHeight = this.classList.contains('active') ? panel.scrollHeight + "px" : null;
});

// File Selection
const fileSelection = (element, dragDropArea, fileType, extensions) => async () => {
    try {
        const selected = await window.__TAURI__.dialog.open({
            filters: [{name: fileType, extensions}], directory: false, multiple: false,
        });
        if (selected) {
            element.value = selected;
            const fileName = selected.split('\\').pop().split('/').pop();
            dragDropArea.innerHTML = `<p>File Selected: <strong>${fileName}</strong></p>`;
        }
    } catch (err) {
        console.error('Error selecting file: ', err);
    }
};

// Folder selection
const folderSelection = (element, dragDropArea) => async () => {
    try {
        const selectedDirectory = await window.__TAURI__.dialog.open({
            directory: true, multiple: false
        });
        if (selectedDirectory) {
            element.value = selectedDirectory;
            const fileName = selectedDirectory.split('\\').pop().split('/').pop();
            dragDropArea.innerHTML = `<p>Directory Selected: <strong>${fileName}</strong></p>`;
        }
    } catch (err) {
        console.error('Error selecting directory:', err);
    }

};


// Assign Event Listeners
elements.videoPath.addEventListener('click', fileSelection(elements.videoPath, elements.videoPath, 'Video Files', ['mp4']));
elements.nmeaPath.addEventListener('click', fileSelection(elements.nmeaPath, elements.nmeaPath, 'NMEA Files', ['nmea']));
elements.savePath.addEventListener('click', folderSelection(elements.savePath, elements.savePath));
elements.bitmaskPath.addEventListener('click', fileSelection(elements.bitmaskPath, elements.bitmaskPath, 'Bitmask file', ['txt']));


// Start Script
elements.startBtn.addEventListener('click', () => {

    const startFrame = parseInt(elements.firstFrame.value, 10) || 0;
    const startNMEALine = parseInt(elements.firstNMEALine.value, 10) || 0;
    const bitmaskProvided = isNaN(Number(elements.bitmaskPath.value));
    const cleanUp = elements.cleanup.checked;

    console.log(elements.savePath.value)

    const parameters = [elements.videoPath.value, elements.nmeaPath.value, elements.bitmaskPath.value, startFrame, startNMEALine, elements.savePath.value, bitmaskProvided, cleanUp];

    const paramsObject = parameters.reduce((obj, param, index) => {
        obj[`param${index + 1}`] = String(param);
        return obj;
    }, {});

    window.__TAURI__.invoke('run_backend', paramsObject);
});


