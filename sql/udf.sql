-- Schema for user defined functions
create schema UDF;

create or replace pynlp scalar script UDF.review_abs(review_id int, review_text varchar(200000)) emits (review_id int, sentence varchar(200000), aspect varchar(100), sentiment double) as

import sys
# This is hack to circumvent a problem with inter system operability of
# spacy
sys.argv = []

import spacy
import numpy as np

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from spacy.tokens import Doc
from spacy.matcher.phrasematcher import PhraseMatcher

nlp = spacy.load('en_core_web_md')
aspect_threshold = .9
sentiment_analyzer = SentimentIntensityAnalyzer()

aspect_terms = {
"aesthetics:sound": ["sound", "music"],
    "aesthetics:visual": ["graphic", "art", "theme", "visual"],
    "narrative:story": ["story", "plot", "narrative"],
    "narrative:dialog": ["dialog", "voice"],
    "game:general": ["game"],
    "gameplay:general": ["gameplay", "mechanics", "strategy"]
}

aspect_tokens = {k: list(nlp.pipe(v)) for k,v in aspect_terms.items()}

def get_similarities(token, token_list):
    """Get similarity of a token with all tokens in a token list."""
    return np.array([t.similarity(token) for t in token_list])


def get_aspects(token, aspect_tokens, threshold):
    """Get aspect for a token. Aspect is asigned if the similarity of the token
    with the aspect key words is greater than a threshold value."""

    similarities = {k: max(get_similarities(token, v))
                    for k,v in aspect_tokens.items()}
    return [k for k,v in similarities.items() if v > threshold]


def get_sentiment(text, sentiment_analyzer):
    """Get sentiment for a text using a sentiment analyser."""
    return sentiment_analyzer.polarity_scores(text)['compound']


def is_descriptive(span):
    """Return True if span contains an adjective or adverb."""
    return any([token.pos_ in ['ADV', 'ADJ'] for token in span])


def get_tree_span(token, doc):
    """Return a token's subtree span as Doc."""
    tree_span = doc[doc[token.i].left_edge.i: doc[token.i].right_edge.i + 1]
    if not isinstance(tree_span, Doc):
        tree_span = tree_span.as_doc()
    return tree_span


def cleanup_subtrees(subtrees, nlp_vocab):
    """Delete redundant Spans from a list of spans"""
    if len(subtrees) == 1:
        return subtrees
    sorted_subtrees = sorted(subtrees, key=lambda x: len(x))
    matcher = PhraseMatcher(nlp_vocab)
    for i, tree in enumerate(sorted_subtrees):
        matcher.add(f"pattern{i}", None, tree)
        _ = [sorted_subtrees.pop(i) for d in sorted_subtrees[i + 1:] if matcher(d)]
    return sorted_subtrees

def run(ctx):

    doc = nlp(ctx.review_text)
    for chunk in doc.noun_chunks:
        # If noun chunk contains a description (adjectives or adverbs), classify
        # noun chunk's aspect and get sentiment if the chunk refers to an aspect.
        aspect = get_aspects(chunk.root,
                             aspect_tokens,
                             threshold=aspect_threshold)
        if not aspect:
            continue

        if is_descriptive(chunk):
          sentiment = get_sentiment(chunk.text, sentiment_analyzer)
          aspect_text = chunk.text
          ctx.emit(ctx.review_id, aspect_text, str(aspect), sentiment)

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
            if not relevant_subtrees:
               continue
            # Delete duplicate subtrees. If a shorter subtree is contained in a
            # larger one, delete the former.
            relevant_subtrees = cleanup_subtrees(relevant_subtrees,
                                                 nlp.vocab)

            # consider all subtrees as information on aspects
            for tree in relevant_subtrees:
                sentiment = get_sentiment(tree.text, sentiment_analyzer)
                aspect_text = tree.text
                ctx.emit(ctx.review_id, aspect_text, str(aspect), sentiment)
/
