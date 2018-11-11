"""Audio Recording Socket.IO Example

Implements server-side audio recording.
"""
import os
import uuid
import wave
from flask import Blueprint, current_app, session, url_for, render_template
from flask_socketio import emit,send
from socketio_examples import socketio
from google.cloud import storage
from seperate_speakers import master
import json


bucket_name = "hackpton-bucket"

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

bp = Blueprint('audio', __name__, static_folder='static',
               template_folder='templates')


@bp.route('/')
def index():
    """Return the client application."""
    return render_template('audio/main.html')


@socketio.on('start-recording', namespace='/audio')
def start_recording(options):
    """Start recording audio from the client."""
    id = uuid.uuid4().hex  # server-side filename
    session['wavename'] = id + '.wav'
    wf = wave.open(current_app.config['FILEDIR'] + session['wavename'], 'wb')
    wf.setnchannels(options.get('numChannels', 1))
    wf.setsampwidth(options.get('bps', 16) // 8)
    wf.setframerate(options.get('fps', 44100))
    session['wavefile'] = wf


@socketio.on('write-audio', namespace='/audio')
def write_audio(data):
    """Write a chunk of audio from the client."""
    session['wavefile'].writeframes(data)



@socketio.on('end-recording', namespace='/audio')
def end_recording():
    """Stop recording audio from the client."""
    session['wavefile'].close()
    upload_blob(bucket_name,current_app.config['FILEDIR'] + session['wavename'],session['wavename'])
    json_data = master("gs://hackpton-bucket/"+session['wavename'])
#     json_data = {'total_duration': 32.0, 'segments': {1: [{'sentence': ['I', 'want', 'to', 'do', 'is', 'yeah,', "I'm", 'going', 'to', 'speed', 'right', 'now', 'at', 'right', 'now.', "Nobody's", 'going', 'to', 'look', 'at', 'me.', 'Look', 'at', 'me', 'weird', 'upstairs'], 'start': 0.0, 'end': 11.0, 'duration': 11.0, 'sentiment': 1}, {'sentence': ['have', 'like', 'two', 'people', 'with', 'very', 'different', 'voices.'], 'start': 18.0, 'end': 32.0, 'duration': 14.0, 'sentiment': -2}], 2: [{'sentence': ['to', 'you.', 'Can', 'you'], 'start': 11.0, 'end': 18.0, 'duration': 7.0, 'sentiment': 0}]}}


#     json_data = {'total_duration': 33.0, 'segments': {1: [{'sentence': [], 'start': 0.0, 'end': 0.0, 'speaker': 1, 'duration': 0.0, 'sentiment': 5}, {'sentence': ['I', 'have', 'to', 'wait', 'before'], 'start': 0.0, 'end': 5.0, 'speaker': 2, 'duration': 5.0, 'sentiment': 2}, {'sentence': ['you', 'stop', 'drinking', 'coffee', 'because', 'you', 'had', 'some', 'issues', 'because', 'of', 'her.', 'So', 'sleepy', 'I', 'have', 'a', 'lot', 'of', 'coffee', 'is', 'required', 'to', 'say', 'something', 'else.', 'Okay,', 'so', 'I', 'can', 'be', 'angry', 'at', 'you', 'for', 'not', 'like'], 'start':5.0, 'end': 33.0, 'duration': 28.0, 'sentiment': 1}], 2: [{'sentence': [], 'start': 0.0, 'end': 0.0, 'speaker': 1,'duration': 0.0, 'sentiment': 5}, {'sentence': ['I', 'have', 'to', 'wait', 'before'], 'start': 0.0, 'end': 5.0, 'speaker': 2, 'duration': 5.0, 'sentiment': -1}, {'sentence': ['you', 'stop', 'drinking', 'coffee', 'because', 'you', 'had', 'some', 'issues', 'because', 'of', 'her.', 'So', 'sleepy', 'I', 'have', 'a', 'lot', 'of', 'coffee', 'is', 'required', 'to', 'say', 'something', 'else.', 'Okay,', 'so', 'I', 'can', 'be', 'angry', 'at', 'you', 'for', 'not', 'like'], 'start': 5.0, 'end': 33.0, 'duration': 28.0, 'sentiment': -2}]}}
#     print(json_data)

#     json_data = {1: [{'sentence': [], 'start': 0.0, 'end': 0.0, 'speaker': 1, 'duration': 0.0, 'sentiment': 5}, {'sentence': ['Then', 'I', 'can', 'then', 'I', 'can', 'really', 'work', 'on', 'that', 'because', 'I', 'have', 'trained', 'to', 'be', 'a', 'public', 'speaker.', 'I', 'have', 'asked', 'how', 'to', 'speak', 'persuasively', 'pic', 'of', 'the', 'pie', 'company.'], 'start': 32.0, 'end': 38.0, 'duration': 6.0, 'sentiment': 2}], 2: [{'sentence': [], 'start': 0.0, 'end': 0.0, 'speaker': 1, 'duration': 0.0, 'sentiment': 5}, {'sentence': ['Then', 'I', 'can', 'then', 'I', 'can', 'really', 'work', 'on', 'that', 'because', 'I', 'have', 'trained', 'to', 'be', 'a', 'public', 'speaker.', 'I', 'have', 'asked', 'how', 'to', 'speak', 'persuasively', 'pic', 'of', 'the', 'pie', 'company.'], 'start': 32.0, 'end': 38.0, 'duration': 6.0, 'sentiment': 2}]}


    emit('add-wavefile', url_for('static',
                            filename='_files/' + session['wavename']))
    session['wavefile'].close()

    emit('speech_data',json_data)


