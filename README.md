
# Video Transcript Summarizer

The **Video Transcript Summarizer** is a web application that allows users to upload a video or enter a YouTube video URL to automatically extract the transcript and generate a concise summary. Built using Python and Flask, this tool helps users quickly grasp the core content of long videos such as lectures, interviews, and tutorials.

---

## Features

- Upload local videos or provide YouTube video links
- Speech-to-text transcription using OpenAI Whisper or SpeechRecognition
- AI-powered summarization using Hugging Face Transformers (e.g.,BART)
- Displays both full transcript and summary
- Progress bar with real-time feedback and video preview

---

## Tech Stack

### Frontend:
- HTML, CSS, JavaScript

### Backend:
- Python 3.x
- Flask (for routing and API handling)
- moviepy (video processing)
- whisper / speechrecognition (transcription)
- transformers / nltk / sumy (for summarization)

---

## Project Structure

Video-Transcript-summarizer/
├── app.py # Flask backend
├── static/
│ └── style.css 
│ └── script.js 
├── templates/
│ └── index.html # Frontend UI
├── uploads/ # Uploaded video files
├── requirements.txt # Python dependencies
└── README.md


---

## How to Run the Project

### Prerequisites

- Python 3.8+
- `ffmpeg` installed and added to PATH (required by moviepy/whisper)

### Installation Steps

1. Clone the repository:
   git clone https://github.com/KalisettyAbhi234/Video-Transcript-Summarizer
   cd Video-Transcript-Summarizer

2. Run the Flask server
   python app.py

3. Open your browser and go to:
   http://127.0.0.1:5000

### Future Enhancements
- Add user login to save summaries
- Improve transcription speed and accuracy with faster models
- PDF export option for summaries
- Support for more video formats and longer YouTube videos
