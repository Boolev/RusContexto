import pickle
from navec import Navec
import json

path = 'game/game_files/navec_hudlit_v1_12B_500K_300d_100q.tar'
navec = Navec.load(path)

from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()

import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = stopwords.words("russian")

with open('game/game_files/words_4_guess.pickle', 'rb') as handle:
    words4guess = pickle.load(handle)

with open('game/game_files/cleaned_all_words.pickle', 'rb') as handle:
    all_words = pickle.load(handle)

all_words = [word for word in all_words if word not in stop_words]


def get_sorted_similarities(main_word):

    global all_words

    similarity_values = []

    for word in all_words:
        similarity = navec.sim(word, main_word)
        similarity_values.append(similarity)

    zipped_sorted = sorted(list(zip(all_words, similarity_values)), key=lambda x: x[1], reverse=True)

    result = [[zipped_sorted[i][0], i + 1] for i in range(len(zipped_sorted))]

    return result


def array_to_json(array_obj):
    return json.dumps(array_obj)


def json_to_array(json_str):
    return json.loads(json_str)


def get_indexes(guesses):

    indexes = []

    for pair in guesses:
        indexes.append(pair[1])

    return indexes
