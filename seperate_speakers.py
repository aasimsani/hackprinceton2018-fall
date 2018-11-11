




def master(gcs_uri):

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
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
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


    raw_transcript = transcribe_gcs(gcs_uri)


    speakers = [] 

    current_sentence = []

    previous_tag = 1

    sentence_start = 0.00
    sentence_end = 0.00

    for data in raw_transcript:

        if previous_tag == data.speaker_tag:
            current_sentence.append(data.word)
            sentence_end = data.end_time.seconds + (data.end_time.nanos/100000000)
        else:

            speakers.append({"sentence":current_sentence,"start":sentence_start,"end":sentence_end,"speaker":previous_tag})
            sentence_start = data.start_time.seconds + (data.start_time.nanos/100000000)
            sentence_end = data.end_time.seconds + (data.end_time.nanos/100000000)
            current_sentence = []
            current_sentence.append(data.word)
            previous_tag = data.speaker_tag


    speakers.append({"sentence":current_sentence,"start":sentence_start,"end":sentence_end})

    last_tag = sentence_end



    """Demonstrates how to make a simple call to the Natural Language API."""


    from google.cloud import language
    from google.cloud.language import enums
    from google.cloud.language import types


    def print_result(annotations):
        score = annotations.document_sentiment.score
        magnitude = annotations.document_sentiment.magnitude

        for index, sentence in enumerate(annotations.sentences):
            sentence_sentiment = sentence.sentiment.score
            # print('Sentence {} has a sentiment score of {}'.format(
                # index, sentence_sentiment))

        # print('Overall Sentiment: score of {} with magnitude of {}'.format(
            # score, magnitude))
        return 0

    def parse_results(annotations):
        score = annotations.document_sentiment.score
        magnitude = annotations.document_sentiment.magnitude

        for index, sentence in enumerate(annotations.sentences):
            sentence_sentiment = sentence.sentiment.score

            return sentence_sentiment



    def analyze(content):
        """Run a sentiment analysis request on text within a passed filename."""
        client = language.LanguageServiceClient()


        document = types.Document(
            content=content,
            type=enums.Document.Type.PLAIN_TEXT)
        annotations = client.analyze_sentiment(document=document)

        # Print the results
        print_result(annotations)

        return parse_results(annotations)



    speaker_sentiment = {1:[],2:[]}


    for data in speakers:

        sentence = ' '.join(data['sentence'])

        raw_data = analyze(sentence)

        if isinstance(raw_data,type(None)):
            sentiment = None
            sentiment_enc = 5
        else:
            sentiment = float(raw_data)

            if sentiment > 0.3:
                sentiment_enc = 2
            elif sentiment <=0.3 and sentiment > -0.3:
                sentiment_enc = 0
            elif sentiment <= -0.3:
               sentiment_enc = -2
            else:
                sentiment_enc = 5

        print(sentiment)
        store = data['start'] 
        if data['end'] < data['start']:
            data['start'] = data['end']
            data['end'] = store

        data['duration'] = data['end'] - data['start']
        data['sentiment'] = sentiment_enc

        import copy
        data_other = copy.deepcopy(data)
        data_other['sentiment'] = 0
        speaker_sentiment[1].append(data)
        speaker_sentiment[2].append(data)


    print(speaker_sentiment)


    print("Completed action!")

    speaker_sentiment_data = {"total_duration":last_tag,"segments":speaker_sentiment}

    return speaker_sentiment_data 
# master("gs://hackpton-bucket/0a65a15c881849beb865947b54c865ac.wav")