function processVideo() {
    const fileInput = document.getElementById('video-file');
    const videoFile = fileInput.files[0];
    const videoUrl = document.getElementById('video-url').value;

    const formData = new FormData();
    if (videoFile) {
        formData.append('file', videoFile);
    } else if (videoUrl) {
        formData.append('url', videoUrl);
    } else {
        alert('Please provide a video file or a URL.');
        return;
    }

    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-bar-container');
    const summaryList = document.getElementById('summary-list');
    const transcriptBox = document.getElementById('transcript-box');

    summaryList.innerHTML = '';
    transcriptBox.value = '';
    progressBar.style.width = '0%';
    progressContainer.style.display = 'block';

    let progress = 10;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 5;
            progressBar.style.width = `${progress}%`;
        }
    }, 300);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(interval);
        progressBar.style.width = '100%';

        transcriptBox.value = data.transcript || "Transcript not available.";

        const points = data.summary.split('.').map(s => s.trim()).filter(s => s);
        points.forEach(point => {
            const li = document.createElement('li');
            li.textContent = point;
            summaryList.appendChild(li);
        });
    })
    .catch(error => {
        clearInterval(interval);
        console.error('Error:', error);
        alert("An error occurred during processing.");
    });
}
