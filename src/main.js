
const pathToTheVideoFile = document.getElementById('videoPath');
const btnPathToVideo = document.getElementById('btnVideoPath');

const pathToTheNMEAFile = document.getElementById('nmeaPath');
const btnPathToNMEA = document.getElementById('btnNMEA');

const btnAccordion = document.querySelector('.accordion');

const pathToTheSaveFolder = document.getElementById('savePath');
const btnSavePlace = document.getElementById('btnSaveDic');

const btnBitmask = document.getElementById('getBitMaks');
const pathToBitmask = document.getElementById('pathToBitmask');

const startFrameField = document.getElementById('firstFrame');
const startNMEALineField = document.getElementById('firstNMEALine');

const startBTN = document.getElementById('btnStart');


// Start the Python Script
startBTN.addEventListener('click', async () => {

  // Int Defaults for the start lines
  let startFrame= parseInt(startFrameField.value, 10);
  let startNMEALine= parseInt(startNMEALineField.value, 10);

  // Bitmask
  let bitmaskProvided = true;
  if (!isNaN(Number(pathToBitmask.value))) {
    bitmaskProvided = false;
  }

  // cleanup
  let cleanUp = document.getElementById('cleanup').checked;

  console.log(cleanUp);

  // set to default values if not declared
  if (isNaN(startFrame) )
    startFrame = 0;

  if (isNaN(startNMEALine) )
    startNMEALine = 0;

  // create parameter list
  const parameter = [
      pathToTheVideoFile.value,
      pathToTheNMEAFile.value,
      pathToBitmask.value,
      startFrame,
      startNMEALine,
      pathToTheSaveFolder.value,
      bitmaskProvided,
      cleanUp
  ]

  // prepare Array for transfer to backend -> convert everything to a string
  const paramsObject = parameter.map(param => String(param)).reduce((obj, param, index) => {
    obj[`param${index + 1}`] = param;
    return obj;
  }, {});


  // run python script
  window.__TAURI__.invoke('run_backend', paramsObject);

});

// Open Bitmask File
btnBitmask.addEventListener('click', async () => {
  try {
    const selected = await window.__TAURI__.dialog.open({
      filters: [
        {name: 'Bitmask file', extensions: ['txt']}
      ],
      directory: false,
      multiple: false,
    });
    if (selected) {
      pathToBitmask.value = selected;
      document.getElementById('getBitMaks').innerHTML = `
        File Selected
        <img src="assets/icons/check-svgrepo-com.svg" alt="File selected" width="24" height="24">
      `;
    }
  } catch (err) {
    console.log(err);
  }
});

// Open Saving Directory
btnSavePlace.addEventListener('click', async () => {
  try {
    const selected = await window.__TAURI__.dialog.open({
      directory: true,
      multiple: false,
    });
    if (selected) {
      pathToTheSaveFolder.value = selected;
      document.getElementById('btnSaveDic').innerHTML = `
        Directory Selected
        <img src="assets/icons/check-svgrepo-com.svg" alt="File selected" width="24" height="24">
      `;
    }
  } catch (err) {
    console.log(err);
  }
});

// Open Video Explorer
btnPathToVideo.addEventListener('click', async () => {
  try {
    const selected = await window.__TAURI__.dialog.open({
      filters: [
          {name: 'Video Files', extensions: ['mp4']}
      ],
      multiple: false,
      directory: false,
    });

    if (selected) {
      pathToTheVideoFile.value = selected;
      document.getElementById('btnVideoPath').innerHTML = `
        File Selected
        <img src="assets/icons/check-svgrepo-com.svg" alt="File selected" width="24" height="24">
      `;
    }
  } catch (err) {
    console.log(err);
  }
});

// Open NMEA Explorer
btnPathToNMEA.addEventListener('click', async () => {
  try {
    const selected = await window.__TAURI__.dialog.open({
      filters: [
        {name: 'NMEA Files', extensions: ['nmea']}
      ],
      multiple: false,
      directory: false,
    });

    if (selected) {
      pathToTheNMEAFile.value = selected;
      document.getElementById('btnNMEA').innerHTML = `
        File Selected
        <img src="assets/icons/check-svgrepo-com.svg" alt="File selected" width="24" height="24">
      `;
    }
  } catch (err) {
    console.log(err);
  }
});

// Open Accordion
document.addEventListener('DOMContentLoaded', () => {

  btnAccordion.addEventListener('click', function() {
    this.classList.toggle('active');
    const panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
      this.classList.remove('active');
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
      this.classList.remove('active');
    }
  });
});
