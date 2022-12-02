import pickle
from navec import Navec

path = 'game/game_files/navec_hudlit_v1_12B_500K_300d_100q.tar'
navec = Navec.load(path)


import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = stopwords.words("russian")


with open('game/game_files/words4guess.pickle', 'rb') as handle:
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
