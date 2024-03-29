// Get Elements by ID
const elements = {
  videoPath: document.getElementById('videoPath'),
  nmeaPath: document.getElementById('nmeaPath'),
  savePath: document.getElementById('savePath'),
  bitmaskPath: document.getElementById('pathToBitmask'),
  firstFrame: document.getElementById('firstFrame'),
  firstNMEALine: document.getElementById('firstNMEALine'),
  cleanup: document.getElementById('cleanup'),
  startBtn: document.getElementById('btnStart'),
  accordionBtn: document.querySelector('.accordion')
};

// Get BTNs by ID
const btns = {
  videoPath: document.getElementById('btnVideoPath'),
  nmeaPath: document.getElementById('btnNMEA'),
  savePath: document.getElementById('btnSaveDic'),
  bitmask: document.getElementById('getBitMaks')
};

// Check inputs for startBTN
function areInputsValid() {
  return elements.videoPath.value && elements.nmeaPath.value && elements.savePath.value;
}

// Disable Start BTN on Load
// TODO: BTN noch ausgrauen und erst activ machen, wenn Daten da sind
document.addEventListener('DOMContentLoaded', () => {
  elements.startBtn.disabled = !areInputsValid();
  Object.values(elements).forEach(inputElement => {
    if (['INPUT', 'SELECT'].includes(inputElement.tagName)) {
      inputElement.addEventListener('input', () => {
        elements.startBtn.disabled = !areInputsValid();
      });
    }
  });
});

// Open Accordion
elements.accordionBtn.addEventListener('click', function() {
  this.classList.toggle('active');
  const panel = this.nextElementSibling;
  panel.style.maxHeight = this.classList.contains('active') ? panel.scrollHeight + "px" : null;
});

// File Selection
const fileSelection = (element, buttonText, fileType, extensions) => async () => {
  try {
    const selected = await window.__TAURI__.dialog.open({
      filters: [{ name: fileType, extensions }],
      directory: fileType === 'Directory',
      multiple: false,
    });
    if (selected) {
      element.value = selected;
      buttonText.innerHTML = `File Selected <img src="assets/icons/check-svgrepo-com.svg" alt="File selected" width="24" height="24">`;
    }
  } catch (err) {
    // TODO: Error auf Display ausgeben
    console.error(err);
  }
};

// Assign Event Listeners
btns.videoPath.addEventListener('click', fileSelection(elements.videoPath, btns.videoPath, 'Video Files', ['mp4']));
btns.nmeaPath.addEventListener('click', fileSelection(elements.nmeaPath, btns.nmeaPath, 'NMEA Files', ['nmea']));
btns.savePath.addEventListener('click', fileSelection(elements.savePath, btns.savePath, 'Directory'));
btns.bitmask.addEventListener('click', fileSelection(elements.bitmaskPath, btns.bitmask, 'Bitmask file', ['txt']));


// Start Script
elements.startBtn.addEventListener('click', () => {

  if (!areInputsValid()) {
    // TODO: Alert einfügen und BTN noch ausblenden
    console.log("Tryed to press STart")
    return;
  }

  const startFrame = parseInt(elements.firstFrame.value, 10) || 0;
  const startNMEALine = parseInt(elements.firstNMEALine.value, 10) || 0;
  const bitmaskProvided = isNaN(Number(elements.bitmaskPath.value));
  const cleanUp = elements.cleanup.checked;

  const parameters = [
    elements.videoPath.value,
    elements.nmeaPath.value,
    elements.bitmaskPath.value,
    startFrame,
    startNMEALine,
    elements.savePath.value,
    bitmaskProvided,
    cleanUp
  ];

  const paramsObject = parameters.reduce((obj, param, index) => {
    obj[`param${index + 1}`] = String(param);
    return obj;
  }, {});

  window.__TAURI__.invoke('run_backend', paramsObject);
});
