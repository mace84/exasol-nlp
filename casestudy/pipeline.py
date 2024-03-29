"""
Implement NLP Pipeline for aspect based sentiment analysis of computer game
reviews.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import spacy
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher

df = pd.read_csv('./data/steam.csv',
                 names=['game_id', 'review', 'sentiment', 'helpful'])

#%%
df.shape[0]
# ~ 6.5 mio reviews


#%%
len(pd.unique(df.game_id))
# ~ 10k games

#%%
df.sentiment.value_counts()/df.shape[0]
# Most reviews are positive (83%)

#%% Distribution of number of users finding the review helpful
df.helpful.value_counts()/df.shape[0]
# Most review are not considered to be helpful (15%)


#%% review
df['review_length'] = df.review.apply(lambda x: len(str(x)))
plt.hist(df['review_length'], 100)
plt.show()

#%% Aspect based sentiment analysis
# Each review is a document
# Parse tree determines noun chunks from document
# For each noun chunk, check whether it refers to an aspect.
#    If chunk contains descriptive words:
#      get sentiment for noun chunk
#    Else:
#      search for noun chunk in all subtrees of the document
#      get sentiment fo all subtrees that contain noun chunk and have descriptives
#
# Aspects are determined by semantic matching of noun chunk roots to aspect key
# words

nlp = spacy.load('en_core_web_md')

sentiment_analyzer = SentimentIntensityAnalyzer()

sim_thresh = .9
aspect_terms = {
    "aesthetics:sound": ["sound", "music"],
    "aesthetics:visual": ["graphic", "art", "theme", "visual"],
    "narrative:story": ["story", "plot", "narrative"],
    "narrative:dialog": ["dialog", "voice"],
    "game:general": ["game"],
    "gameplay:general": ["gameplay", "mechanics", "strategy"]
}

aspect_tokens = {k: list(nlp.pipe(v)) for k,v in aspect_terms.items()}

#%% Helper functions


def get_similarities(token, token_list):
    """Get similarity of a token with all tokens in a token list."""
    try:
        if token.has_vector:
            similarities = [t.similarity(token) for t in token_list]
        else:
            similarities = []
    except:
        similarities = []
    return np.array(similarities)


def get_aspects(token, aspect_tokens, threshold):
    """Get aspect for a token. Aspect is asigned if the similarity of the token
    with the aspect key words is greater than a threshold value."""

    similarities = {k: max(get_similarities(token, v))
                    for k, v in aspect_tokens.items()}
    similarities = [k for k, v in similarities.items() if v and v > threshold]
    return similarities


def get_sentiment(text, sentiment_analyzer):
    """Get sentiment for a text using a sentiment analyser."""
    try:
        sentiment = sentiment_analyzer.polarity_scores(text)['compound']
    except:
        return None
    else:
        return sentiment


def is_descriptive(span):
    """Return True if span contains an adjective or adverb."""
    return any([token.pos_ in ['ADV', 'ADJ'] for token in span])


def get_tree_span(token, doc):
    """Return a token's subtree span as Doc."""
    tree_span = Span(doc, doc[token.i].left_edge.i, doc[token.i].right_edge.i + 1)
    return tree_span


def cleanup_subtrees(subtrees, nlp_vocab):
    """Delete redundant Spans from a list of spans"""
    if len(subtrees) == 1:
        return subtrees
    sorted_subtrees = sorted(subtrees, key=lambda x: len(x))
    sorted_tree_docs = [nlp(span.text) for span in sorted_subtrees]
    matcher = PhraseMatcher(nlp_vocab)
    for i, tree in enumerate(sorted_tree_docs):
        matcher.add(f"pattern{i}", None, tree)
        _ = [sorted_tree_docs.pop(i) for d in sorted_tree_docs[i + 1:] if matcher(d)]
    return sorted_tree_docs

#%% NLP Loop

nlp = spacy.load('en_core_web_md')

reviews = df.sample(n=10000, random_state=4711)

reviews['review_id'] = list(range(1, reviews.shape[0] + 1))

skip_ear = ' Early Access Review'
aspect_threshold = .9
sentences = []
aspects = []
sentiments = []
review_ids = []

review_data = [(str(txt), str(id)) for txt, id in reviews[['review', 'review_id']].values]


for doc, review_id in nlp.pipe(review_data, as_tuples=True):

    try:
        # Skip Early Access Reviews
        if doc.text == skip_ear:
            continue

        if not doc.text:
            continue

        for chunk in doc.noun_chunks:
            # If noun chunk contains a description (adjectives or adverbs), classify
            # noun chunk's aspect and get sentiment if the chunk refers to an aspect.
            aspect = get_aspects(chunk.root,
                                 aspect_tokens,
                                 threshold=aspect_threshold)
            if not aspect:
                continue

            if is_descriptive(chunk):
                aspects.append(aspect)
                sentiments.append(get_sentiment(chunk.text, sentiment_analyzer))
                sentences.append(chunk.text)
                review_ids.append(review_id)

            # Else: lookup noun chunk in subtrees of tokens. Filter subtrees and keep
            # only those that contain a description (adjectives or adverbs)
            else:
                relevant_subtrees = []
                for token in doc:
                    subtree_contains_chunk = all([t in token.subtree for t in chunk])
                    if not subtree_contains_chunk:
                        continue
                    if not is_descriptive(token.subtree):
                        continue
                    tree_span = get_tree_span(token, doc)
                    relevant_subtrees.append(tree_span)

                # Delete duplicate subtrees. If a shorter subtree is contained in a
                # larger one, delete the former.
                relevant_subtrees = cleanup_subtrees(relevant_subtrees, nlp.vocab)

                # consider all subtrees as information on aspects
                for tree in relevant_subtrees:
                    aspects.append(aspect)
                    sentiments.append(get_sentiment(tree.text, sentiment_analyzer))
                    sentences.append(tree.text)
                    review_ids.append(review_id)
    except:
        continue


aspect_data = pd.DataFrame({'review_id': review_ids,
                            'snippet': sentences,
                            'aspect': aspects,
                            'sentiment': sentiments})