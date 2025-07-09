from flask import Flask, render_template, request, jsonify
import os
import whisper
from transformers import pipeline
from pytube import YouTube
from moviepy.editor import VideoFileClip
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
whisper_model = whisper.load_model("base")

# Load summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Handle file or URL input
    if 'file' in request.files and request.files['file']:
        file = request.files['file']
        video_path = save_uploaded_file(file)
    elif 'url' in request.form and request.form['url']:
        video_url = request.form['url']
        video_path = download_video_from_url(video_url)
        if video_path is None:
            return jsonify({'error': 'Failed to download video'}), 400
    else:
        return jsonify({'error': 'No file or URL provided'}), 400

    # Extract audio and transcribe
    audio_path = extract_audio(video_path)
    if not audio_path:
        return jsonify({'error': 'Audio extraction failed'}), 500

    transcript = transcribe_audio(audio_path)
    summary = summarize_text(transcript)

    return jsonify({'summary': summary, 'transcript': transcript})

def save_uploaded_file(file):
    filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(video_path)
    return video_path

def download_video_from_url(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution="360p").first()
        if stream is None:
            print("No suitable stream found.")
            return None
        filename = f"{uuid.uuid4()}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)
        return video_path
    except Exception as e:
        print("Download error:", e)
        return None


def extract_audio(video_path):
    try:
        clip = VideoFileClip(video_path)
        audio_path = video_path.replace('.mp4', '.wav')
        clip.audio.write_audiofile(audio_path)
        return audio_path
    except Exception as e:
        print("Audio extraction error:", e)
        return None

def transcribe_audio(audio_path):
    try:
        result = whisper_model.transcribe(audio_path)
        return result['text']
    except Exception as e:
        print("Transcription error:", e)
        return ""

def summarize_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])

    final = summarizer(" ".join(summaries), max_length=150, min_length=30, do_sample=False)
    return final[0]['summary_text']

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
