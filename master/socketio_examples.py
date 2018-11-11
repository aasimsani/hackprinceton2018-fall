import os
from flask import Flask, render_template
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['FILEDIR'] = 'static/_files/'
app.config['CHAT_URL'] = os.environ.get('CHAT_URL')
app.config['POLLS_VOTE_URL'] = os.environ.get('POLLS_VOTE_URL')
app.config['WHERE_PIN_URL'] = os.environ.get('WHERE_PIN_URL')
app.config['GOOGLE_MAPS_KEY'] = os.environ.get('GOOGLE_MAPS_KEY')
socketio = SocketIO(app, async_mode=True)

from audio import bp as audio_bp

app.register_blueprint(audio_bp, url_prefix='/audio')


@app.route('/')
def index():
    return render_template('index.html')


    

