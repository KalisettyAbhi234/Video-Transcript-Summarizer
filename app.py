# from flask import Flask, render_template, request, jsonify
# import os
# import moviepy.editor as mp
# import speech_recognition as sr
# from transformers import pipeline
# from pytube import YouTube
# from pydub import AudioSegment

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Summarization model
# summarizer = pipeline("summarization")

# # Home route
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Upload and process video route
# @app.route('/upload', methods=['POST'])
# def upload():
#     # Check if a file was uploaded
#     if 'file' in request.files and request.files['file']:
#         file = request.files['file']
#         video_path = save_uploaded_file(file)

#     # Check if a URL was submitted
#     elif 'url' in request.form and request.form['url']:
#         video_url = request.form['url']
#         video_path = download_video_from_url(video_url)
#         if video_path is None:
#             return jsonify({'error': 'Failed to download video from URL'}), 400

#     else:
#         return jsonify({'error': 'No file or URL provided'}), 400

#     # Extract audio from video
#     audio_path = extract_audio(video_path)
#     if audio_path is None:
#         return jsonify({'error': 'Failed to extract audio from video'}), 500

#     # Convert audio to text
#     transcript = audio_to_text(audio_path)

#     # Summarize the text
#     summary = summarize_text(transcript)

#     return jsonify({'summary': summary})

# def save_uploaded_file(file):
#     video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#     file.save(video_path)
#     return video_path

# def download_video_from_url(url):
#     try:
#         yt = YouTube(url)
#         video = yt.streams.filter(progressive=True, file_extension='mp4').first()
#         if video is None:
#             return None  # Return None if no video stream is found

#         # Sanitize the file name
#         video_title = yt.title.replace(" ", "_").replace("/", "_")
#         video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{video_title}.mp4")
#         video.download(output_path=app.config['UPLOAD_FOLDER'], filename=f"{video_title}.mp4")
#         return video_path
#     except Exception as e:
#         print(f"Error downloading video: {e}")
#         return None

# def extract_audio(video_path):
#     try:
#         video = mp.VideoFileClip(video_path)
#         audio_path = video_path.replace('.mp4', '.wav')
#         video.audio.write_audiofile(audio_path)
#         return audio_path
#     except Exception as e:
#         print(f"Error extracting audio: {e}")
#         return None

# def audio_to_text(audio_path):
#     recognizer = sr.Recognizer()
#     audio = AudioSegment.from_wav(audio_path)

#     # Split audio into chunks of 1 minute each
#     chunk_length_ms = 60000  # 1 minute
#     chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
#     transcript = ""

#     for i, chunk in enumerate(chunks):
#         chunk_path = f"{audio_path}_chunk_{i}.wav"
#         chunk.export(chunk_path, format="wav")

#         # Process each chunk with Google Speech Recognition API
#         with sr.AudioFile(chunk_path) as source:
#             audio_data = recognizer.record(source)
#             try:
#                 text = recognizer.recognize_google(audio_data)
#                 transcript += " " + text
#             except sr.RequestError as e:
#                 return f"API request failed: {e}"
#             except sr.UnknownValueError:
#                 transcript += " [unrecognized audio] "

#         os.remove(chunk_path)  # Clean up chunk files

#     return transcript

# def summarize_text(text, chunk_size=1000):
#     # Break text into chunks for summarization if it's too long
#     text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
#     summaries = []
#     for chunk in text_chunks:
#         summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
#         summaries.append(summary[0]['summary_text'])
    
#     combined_summary = " ".join(summaries)
#     final_summary = summarizer(combined_summary, max_length=150, min_length=30, do_sample=False)
#     return final_summary[0]['summary_text']

# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)


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

# def download_video_from_url(url):
#     try:
#         yt = YouTube(url)
#         # stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
#         stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution="360p").first()
#         filename = f"{uuid.uuid4()}.mp4"
#         video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)
#         print(f"Title: {yt.title}")
#         print(f"Length: {yt.length} seconds")
#         print(f"Author: {yt.author}")
#         return video_path
#     except Exception as e:
#         print("Download error:", e)
#         return None
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
