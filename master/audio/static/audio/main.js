/* Audio recording and streaming demo by Miguel Grinberg.

   Adapted from https://webaudiodemos.appspot.com/AudioRecorder
   Copyright 2013 Chris Wilson

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext();
var audioInput = null,
    realAudioInput = null,
    inputPoint = null,
    recording = false;
var rafID = null;
var analyserContext = null;
var canvasWidth, canvasHeight;
var socketio = io.connect(location.origin + '/audio', {transports: ['websocket']});

socketio.on('speech_data', function(json) {
    // add new recording to page

    document.getElementById("center-this").innerHTML = ''
    
    audio = document.createElement('p');
    console.log(JSON.stringify(json,null,2));

    var totalDuration = json['total_duration'];

    var toRender = "";

    h = document.createElement('h1');

    h.innerHTML = 'Speaker A <br/>';
    document.getElementById('speaker-a').appendChild(h);
    for (var data in json['segments'][1]) {
        var duration = json['segments'][1][data]["duration"];
        var percent = Math.round((duration/totalDuration) * 100);
            percent = Math.round(percent/1.20);
        var toRender = "";
        var sentiment = json['segments'][1][data]['sentiment'];
        var emotionScalar = "";

        if (sentiment == -2) {
            emotionScalar = "most-negative";
        } else if (sentiment == -1) {
            emotionScalar = "less-negative";
        } else if (sentiment == 0) {
            emotionScalar = "neutral";
        } else if (sentiment == 1) {
            emotionScalar = "less-positive";
        } else if (sentiment == 2) {
            emotionScalar = "most-positive";
        } else {
            emotionScalar = "empty";
        }
        
        toRender = '<div class="progress-bar progress-bar-' + emotionScalar + '" role="progressbar" style="width:' + percent + '%">';
        tr = document.createElement('div')
        tr.innerHTML = toRender;
        document.getElementById('speaker-a').appendChild(tr);

    }

  
    h = document.createElement('h1');

    h.innerHTML = 'Speaker B';
    document.getElementById('speaker-b').appendChild(h);

    for (var data in json['segments'][2]) {
        var duration = json['segments'][2][data]["duration"];
        var percent = Math.round((duration /totalDuration) * 100);
            percent = Math.round(percent/1.40);
        var toRender = "";
        var sentiment = json['segments'][2][data]['sentiment'];
        var emotionScalar = "";

        if (sentiment == -2) {
            emotionScalar = "most-negative";
        } else if (sentiment == -1) {
            emotionScalar = "less-negative";
        } else if (sentiment == 0) {
            emotionScalar = "neutral";
        } else if (sentiment == 1) {
            emotionScalar = "less-positive";
        } else if (sentiment == 2) {
            emotionScalar = "most-positive";
        } else {
            emotionScalar = "empty";
        }
        
        toRender = '<div class="progress-bar progress-bar-' + emotionScalar + '" role="progressbar" style="width:' + percent + '%">';
        tr = document.createElement('div')
        tr.innerHTML = toRender;
        document.getElementById('speaker-b').appendChild(tr);
    }
  


});

socketio.on('add-wavefile', function(url) {
    // add new recording to page
    audio = document.createElement('p');
    // audio.innerHTML = '<audio src="' + url + '" controls>';
    document.getElementById('wavefiles').appendChild(audio);
});

function toggleRecording( e ) {
    if (e.classList.contains('recording')) {
        // stop recording
        document.getElementById("record").src = "/audio/static/audio/start.png"
        document.getElementById("center-this").innerHTML = '<img src="/audio/static/audio/loader.gif" id="loader" />'
        e.classList.remove('recording');
        recording = false;
        socketio.emit('end-recording');
    } else {
        // start recording
        document.getElementById("record").src = "/audio/static/audio/stop.png"
        e.classList.add('recording');
        recording = true;
        socketio.emit('start-recording', {numChannels: 1, bps: 16, fps: parseInt(audioContext.sampleRate)});
    }
}

function convertToMono( input ) {
    var splitter = audioContext.createChannelSplitter(2);
    var merger = audioContext.createChannelMerger(2);

    input.connect( splitter );
    splitter.connect( merger, 0, 0 );
    splitter.connect( merger, 0, 1 );
    return merger;
}

function cancelAnalyserUpdates() {
    window.cancelAnimationFrame( rafID );
    rafID = null;
}

function updateAnalysers(time) {
    if (!analyserContext) {
        var canvas = document.getElementById('analyser');
        canvasWidth = canvas.width;
        canvasHeight = canvas.height;
        analyserContext = canvas.getContext('2d');
    }

    // analyzer draw code here
    {
        var SPACING = 3;
        var BAR_WIDTH = 1;
        var numBars = Math.round(canvasWidth / SPACING);
        var freqByteData = new Uint8Array(analyserNode.frequencyBinCount);

        analyserNode.getByteFrequencyData(freqByteData); 

        analyserContext.clearRect(0, 0, canvasWidth, canvasHeight);
        analyserContext.fillStyle = '#F6D565';
        analyserContext.lineCap = 'round';
        var multiplier = analyserNode.frequencyBinCount / numBars;

        // Draw rectangle for each frequency bin.
        for (var i = 0; i < numBars; ++i) {
            var magnitude = 0;
            var offset = Math.floor( i * multiplier );
            // gotta sum/average the block, or we miss narrow-bandwidth spikes
            for (var j = 0; j< multiplier; j++)
                magnitude += freqByteData[offset + j];
            magnitude = magnitude / multiplier;
            var magnitude2 = freqByteData[i * multiplier];
            analyserContext.fillStyle = "hsl( " + Math.round((i*360)/numBars) + ", 100%, 50%)";
            analyserContext.fillRect(i * SPACING, canvasHeight, BAR_WIDTH, -magnitude);
        }
    }
    
    rafID = window.requestAnimationFrame( updateAnalysers );
}

function toggleMono() {
    if (audioInput != realAudioInput) {
        audioInput.disconnect();
        realAudioInput.disconnect();
        audioInput = realAudioInput;
    } else {
        realAudioInput.disconnect();
        audioInput = convertToMono( realAudioInput );
    }

    audioInput.connect(inputPoint);
}

function gotStream(stream) {
    inputPoint = audioContext.createGain();

    // Create an AudioNode from the stream.
    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;

    audioInput = convertToMono( audioInput );
    audioInput.connect(inputPoint);

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect( analyserNode );

    scriptNode = (audioContext.createScriptProcessor || audioContext.createJavaScriptNode).call(audioContext, 1024, 1, 1);
    scriptNode.onaudioprocess = function (audioEvent) {
        if (recording) {
            input = audioEvent.inputBuffer.getChannelData(0);

            // convert float audio data to 16-bit PCM
            var buffer = new ArrayBuffer(input.length * 2)
            var output = new DataView(buffer);
            for (var i = 0, offset = 0; i < input.length; i++, offset += 2) {
                var s = Math.max(-1, Math.min(1, input[i]));
                output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            }
            socketio.emit('write-audio', buffer);
        }
    }
    inputPoint.connect(scriptNode);
    scriptNode.connect(audioContext.destination);

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect( zeroGain );
    zeroGain.connect( audioContext.destination );
    updateAnalysers();
}

function initAudio() {
    if (!navigator.getUserMedia)
        navigator.getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
    if (!navigator.cancelAnimationFrame)
        navigator.cancelAnimationFrame = navigator.webkitCancelAnimationFrame || navigator.mozCancelAnimationFrame;
    if (!navigator.requestAnimationFrame)
        navigator.requestAnimationFrame = navigator.webkitRequestAnimationFrame || navigator.mozRequestAnimationFrame;

    navigator.getUserMedia({audio: true}, gotStream, function(e) {
        alert('Error getting audio');
        console.log(e);
    });
}

window.addEventListener('load', initAudio );
