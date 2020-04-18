def test_extract_from_tweet(ner_extractor):
    text = '''
    Perfect just Perfect! It's a perfect storm for Nairobi on a
    Friday evening! horrible traffic here is your cue to become worse @Ma3Route
    '''

    places = ner_extractor.find_entities(text=text)

    assert places
    assert 'Nairobi' in places


def test_extract_from_tweet_with_link(ner_extractor):
    text3 = '''
    Risks of Cycling in Nairobi:
    http://www.globalsiteplans.com/environmental-design/engineering-environmental
    -design/the-risky-affair-of-cycling-in-nairobi-kenya/ ...
    via @ConstantCap @KideroEvans @county_nairobi @NrbCity_Traffic
    '''
    places = ner_extractor.find_entities(text=text3)

    assert places
    assert 'Nairobi' in places


def test_extract_from_tweet_with_mention(ner_extractor):
    text4 = '''
    @DurbanSharks [Africa Renewal]It is early morning in Nairobi,
    the Kenyan capital. The traffic jam along Ngong
    '''
    places = ner_extractor.find_entities(text=text4)

    assert places
    assert 'Nairobi' in places
    assert 'Ngong' in places


def test_extract_from_text(ner_extractor):
    text = ' There is a city called São Paulo in Brazil.'
    places = ner_extractor.find_entities(text=text)

    assert len(places) == 2
    assert 'São Paulo' in places
    assert 'Brazil' in places
