
const pathToTheVideoFile = document.getElementById('videoPath');
const btnPathToVideo = document.getElementById('btnVideoPath');

const pathToTheNMEAFile = document.getElementById('nmeaPath');
const btnPathToNMEA = document.getElementById('btnNMEA');

const btnAccordion = document.querySelector('.accordion');

const pathToTheSaveFolder = document.getElementById('savePath');
const btnSavePlace = document.getElementById('btnSaveDic');

const btnBitmask = document.getElementById('getBitMaks');
const pathToBitmask = document.getElementById('pathToBitmask');

const startFrame = document.getElementById('firstFrame').value;
const startNMEALine = document.getElementById('firstNMEALine').value;

const startBTN = document.getElementById('btnStart');


// Start the Python Script
startBTN.addEventListener('click', async () => {
  const param1 = document.getElementById('videoPath').value;
  const param2 = document.getElementById('nmeaPath').value;
  const param3 = pathToBitmask.value;
  const param4 = startFrame.value;
  const param5 = startNMEALine.value;
  const param6 = pathToTheSaveFolder.value;
  const param7 = 'true';
  const param8 = 'false';

  window.__TAURI__.invoke('run_python_script', {
    param1,
    param2,
    param3,
    param4,
    param5,
    param6,
    param7,
    param8
  })
      .then((output) => {
        console.log(output);
      })
      .catch((error) => {
        console.error(error);
      });
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
