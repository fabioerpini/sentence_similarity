import numpy as np
#from sklearn.feature_extraction.text import TfidfVectorizer

# from sentence_similarity import sentence_similarity
#from sklearn.decomposition import TruncatedSVD
#from sklearn.pipeline import make_pipeline
#from sklearn.preprocessing import Normalizer

import gensim.downloader as api

from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

#from onnxt5 import GenerativeT5
#from onnxt5.api import get_encoder_decoder_tokenizer


# measures:
# entailment: LLM x NLI, STS;
# concept mover distance?
# sentence: cosine x T5, sBERT, LSA (embeddings trained on another corpus)
# word: wmd, cosine x fasttext, word2vec, glove

'''
def T5_generative_model():
    # t5 = transformers.T5ForConditionalGeneration.from_pretrained('t5-11b', use_cdn=False)
    # return t5
    model_name = 't5-base'
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer
    # decoder_sess, encoder_sess, tokenizer = get_encoder_decoder_tokenizer()
    # generative_t5 = GenerativeT5(encoder_sess, decoder_sess, tokenizer, onnx=True)
    # prompt = 'translate English to French: I was a victim of a series of accidents.'
    # 
    # output_text, output_logits = generative_t5(prompt, max_length=100, temperature=0.)
'''

def load_sentence_transformers(model_name):
    return SentenceTransformer(f'sentence-transformers/{model_name}')


def T5_model():
    return load_sentence_transformers('sentence-t5-base')

'''
def RoBERTa_model():
    return load_sentence_transformers('stsb-roberta-base')


def LSA_model():
    corpus = api.load('text8')  # download the corpus and return it opened as an iterable

    lsa = make_pipeline(TfidfVectorizer(
        max_df=0.5,
        min_df=5,
        stop_words=None,  # keep things like not, etc.
    ), TruncatedSVD(n_components=100), Normalizer(copy=False))
    return lsa.fit(map(lambda x: ' '.join(x), corpus))


def fasttext_model():
    # https://github.com/piskvorky/gensim-data
    model = api.load("fasttext-wiki-news-subwords-300")
    model.fill_norms()
    return model


def w2v_model():
    model = api.load("word2vec-google-news-300")
    model.fill_norms()
    return model


def glove_model():
    model = api.load("glove-wiki-gigaword-300")
    model.fill_norms()
    return model


def embed_sentences(sentences, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    # Compute embeddings
    embeddings = model.encode(sentences, convert_to_tensor=True)
    return embeddings
'''

def cosine_similarity_from_embeddings(embeddings):
    return util.cos_sim(embeddings, embeddings)


def print_similarities(cosine_scores, sentences):
    # Find the pairs with the highest cosine similarity scores
    pairs = []
    for i in range(len(cosine_scores) - 1):
        for j in range(i + 1, len(cosine_scores)):
            pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})

    # Sort scores in decreasing order
    pairs = sorted(pairs, key=lambda x: x['score'], reverse=True)

    for pair in pairs[0:10]:
        i, j = pair['index']
        print("{} \t\t {} \t\t Score: {:.4f}".format(sentences[i], sentences[j], pair['score']))


def preprocess(text):
    return ''.join(c.lower() if c.isalpha() else ' ' for c in text)


def tokenize(text):
    return text.split()


def embed_from_words(list_of_embeddings):
    return np.mean(list_of_embeddings, axis=0)













