

speech_file = "./test.wav"



with open(speech_file,'rb') as audio_file:

    content = audio_file.read()

def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""

    from google.cloud import speech_v1p1beta1 as speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=gcs_uri)

    from google.cloud import speech_v1p1beta1 as speech
    client = speech.SpeechClient()

    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        language_code='en-US',
        enable_speaker_diarization=True,
        enable_automatic_punctuation=True,
        diarization_speaker_count=2)


    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=900)
    # The transcript within each result is separate and sequential per result.
    # However, the words list within an alternative includes all the words
    # from all the results thus far. Thus, to get all the words with speaker
    # tags, you only have to take the words list from the last result:
    result = response.results[-1]

    words_info = result.alternatives[0].words

    return words_info
        

raw_transcript = transcribe_gcs("gs://hackpton-bucket/test-longer.flac")

speakers = {1:[],2:[]}

current_sentence = []

previous_tag = 1

for data in raw_transcript:

    if previous_tag == data.speaker_tag:
        current_sentence.append(data.word)
    else:
        speakers[data.speaker_tag].append(current_sentence)
        current_sentence = []
        current_sentence.append(data.word)
        previous_tag = data.speaker_tag


speakers[previous_tag].append(current_sentence)




"""Demonstrates how to make a simple call to the Natural Language API."""


from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


def print_result(annotations):
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))

    print('Overall Sentiment: score of {} with magnitude of {}'.format(
        score, magnitude))
    return 0


def analyze(content):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language.LanguageServiceClient()

    
    document = types.Document(
        content=content,
        type=enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document)

    # Print the results
    print_result(annotations)

    return (annotations)



speaker_sentiment = {1:[],2:[]}


for data in speakers[1]:

    analyze((' '.join(data)))


for data in speakers[2]:

    analyze(' '.join(data))