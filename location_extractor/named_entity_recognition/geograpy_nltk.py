import nltk


def download_nltk():
    required_resources = [
        'maxent_ne_chunker',
        'words',
        'treebank',
        'maxent_treebank_pos_tagger',
        'punkt',
        'averaged_perceptron_tagger'
    ]
    for resource in required_resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.downloader.download(resource, quiet=True)
