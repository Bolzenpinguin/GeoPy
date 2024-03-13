
const pathToTheVideoFile = document.getElementById('videoPath');
const btnPathToVideo = document.getElementById('getVideoPath');



window.addEventListener("DOMContentLoaded", () => {

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
    }

  } catch (err) {
    console.log(err);
  }

  });
});
