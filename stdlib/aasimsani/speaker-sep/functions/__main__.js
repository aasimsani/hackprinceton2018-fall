/**
* A simple "hello world" function
*/
const fs = require('fs');


// Imports the Google Cloud client library
const speech = require('@google-cloud/speech').v1p1beta1;

// Creates a client
const client = new speech.SpeechClient();

/**
 * TODO(developer): Uncomment the following lines before running the sample.
 */
// const fileName = 'Local path to audio file, e.g. /path/to/audio.raw';

const config = {
  encoding: `LINEAR16`,
  sampleRateHertz: 8000,
  languageCode: `en-US`,
  enableSpeakerDiarization: true,
  diarizationSpeakerCount: 2,
  model: `phone_call`,
};

const audio = {
  content: fs.readFileSync(fileName).toString('base64'),
};

const request = {
  config: config,
  audio: audio,
};

client
  .recognize(request)
  .then(data => {
    const response = data[0];
    const transcription = response.results
      .map(result => result.alternatives[0].transcript)
      .join('\n');
    console.log(`Transcription: ${transcription}`);
    console.log(`Speaker Diarization:`);
    const result = response.results[response.results.length - 1];
    const wordsInfo = result.alternatives[0].words;
    // Note: The transcript within each result is separate and sequential per result.
    // However, the words list within an alternative includes all the words
    // from all the results thus far. Thus, to get all the words with speaker
    // tags, you only have to take the words list from the last result:
    wordsInfo.forEach(a =>
      console.log(` word: ${a.word}, speakerTag: ${a.speakerTag}`)
    );
  })
  .catch(err => {
    console.error('ERROR:', err);
  });
  
  
module.exports = async (name = 'world') => {
  return `Hello ${name}, I built this API with Code on Standard Library!`;
};