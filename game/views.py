from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
import pickle
from random import sample
from math import ceil
from pymorphy2 import MorphAnalyzer
from .utils import get_sorted_similarities
from .utils import stop_words
from .utils import words4guess
from .utils import all_words


morph = MorphAnalyzer()

secret_word = sample(words4guess, 1)[0]
user_guesses = []
similarities = get_sorted_similarities(secret_word)
is_victory = False


def reinitialize_game():
    global user_guesses
    global secret_word
    global similarities
    global is_victory

    secret_word = sample(words4guess, 1)[0]
    user_guesses = []
    similarities = get_sorted_similarities(secret_word)
    is_victory = False

    return


def get_indexes(user_guesses_):
    indexes = []

    for pair in user_guesses_:
        indexes.append(pair[1])

    return indexes


def index(request):

    global user_guesses
    global secret_word
    global similarities
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
                for pair in similarities:
                    if lemmatized in pair:
                        if pair in user_guesses:
                            messages.warning(request, f'Рейтинг слова {lemmatized} уже известен')
                            found = True
                            break
                        else:
                            if pair[1] == 1:
                                is_victory = True
                            context['pair_for_asked'] = pair
                            user_guesses.append(pair)
                            user_guesses = sorted(user_guesses, key=lambda x: x[1])
                            found = True

                if not found:
                    messages.warning(request, 'Неизвестное слово')

        elif 'show_answer_button' in request.POST:

            user_guesses.append(similarities[0])
            user_guesses = sorted(user_guesses, key=lambda x: x[1])
            is_victory = True

            context['secret_word'] = secret_word

        elif 'start_new_game_button' in request.POST:

            reinitialize_game()

        elif 'give_hint_button' in request.POST:

            if not user_guesses:
                messages.warning(request, 'Сделайте хотя бы одно предположение')

            elif user_guesses[0][1] == 1:
                messages.warning(request, 'Слово уже отгадано')

            elif user_guesses[0][1] == 2:
                for i in range(3, len(similarities)):
                    if i in get_indexes(user_guesses):
                        continue

                    placed = False
                    for pair in similarities:
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

                for pair in similarities:
                    if pair[1] == need_to_place:
                        user_guesses.append(pair)
                        user_guesses = sorted(user_guesses, key=lambda x: x[1])
                        break

        elif 'show_top_100_closest' in request.POST:

            top_100 = similarities[:100]
            local_context = {'top_100': top_100}

            return render(request, 'game/top_100.html', local_context)

        elif 'get_to_home_button' in request.POST:

            redirect('index')

    context['user_guesses'] = user_guesses
    context['is_victory'] = is_victory

    return render(request, 'game/index.html', context)
