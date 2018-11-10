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

    print(json_data)


    emit('add-wavefile', url_for('static',
                            filename='_files/' + session['wavename']))
    session['wavefile'].close()

    emit('speech_data',[{}])


