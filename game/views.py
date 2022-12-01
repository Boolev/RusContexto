from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
import pickle
from random import randrange
from math import ceil
from pymorphy2 import MorphAnalyzer

import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
stop_words = stopwords.words("russian")


morph = MorphAnalyzer()

with open('game/game_files/cleaned_all_words.pickle', 'rb') as handle:
    all_words = pickle.load(handle)

with open('game/game_files/similarity_matrix.pickle', 'rb') as handle:
    similarity_matrix = pickle.load(handle)

with open('game/game_files/words4guess.pickle', 'rb') as handle:
    words4guess = pickle.load(handle)  

guess_words_length = len(words4guess)

user_guesses = []

random_index = randrange(guess_words_length)
secret_word = words4guess[random_index]

is_victory = False


def get_indexes(user_guesses_):
    indexes = []

    for pair in user_guesses_:
        indexes.append(pair[1])

    return indexes


def index(request):

    global user_guesses
    global random_index
    global secret_word
    global is_victory

    context = {}

    if request.method == 'POST':

        if 'check_word_button' in request.POST:

            input_word = request.POST.get('input_word')

            if input_word in stop_words:
                messages.warning(request, 'В этом слове мало смысла')

            else:
                lemmatized = morph.parse(input_word)[0].normal_form

                found = False
                for pair in similarity_matrix[secret_word]:
                    if lemmatized in pair:
                        if pair in user_guesses:
                            messages.warning(request, f'Рейтинг слова {lemmatized} уже известен')
                            found = True
                            break
                        else:
                            if pair[1] == 1:
                                messages.warning(request, 'Вы отгадали слово. Можете продолжать эксперименты')
                                is_victory = True
                            context['pair_for_asked'] = pair
                            user_guesses.append(pair)
                            user_guesses = sorted(user_guesses, key=lambda x: x[1])
                            found = True

                if not found:
                    messages.warning(request, 'Неизвестное слово')

        elif 'show_answer_button' in request.POST:

            user_guesses.append(similarity_matrix[secret_word][0])
            user_guesses = sorted(user_guesses, key=lambda x: x[1])
            context['secret_word'] = secret_word

        elif 'start_new_game_button' in request.POST:

            user_guesses = []
            is_victory = False

            random_index = randrange(guess_words_length)
            secret_word = words4guess[random_index]

        elif 'give_hint_button' in request.POST:

            if not user_guesses:
                messages.warning(request, 'Сделайте хотя бы одно предположение')

            elif user_guesses[0][1] == 1:
                messages.warning(request, 'Слово уже отгадано')

            elif get_indexes(user_guesses)[0] == 2:
                for i in range(3, 50000):
                    if i in get_indexes(user_guesses):
                        continue

                    placed = False
                    for pair in similarity_matrix[secret_word]:
                        if pair[1] == i:
                            user_guesses.append(pair)
                            user_guesses = sorted(user_guesses, key=lambda x: x[1])
                            placed = True
                            break

                    if placed:
                        break
            else:
                top_guess = get_indexes(user_guesses)[0]
                need_to_place = ceil(top_guess / 2)

                for pair in similarity_matrix[secret_word]:
                    if pair[1] == need_to_place:
                        user_guesses.append(pair)
                        user_guesses = sorted(user_guesses, key=lambda x: x[1])
                        break

        elif 'show_top_100_closest' in request.POST:

            top_100 = similarity_matrix[secret_word][:100]
            local_context = {'top_100': top_100}

            return render(request, 'game/top_100.html', local_context)

        elif 'get_to_home_button' in request.POST:

            redirect('index')

    context['user_guesses'] = user_guesses
    context['is_victory'] = is_victory

    return render(request, 'game/index.html', context)
