from django.shortcuts import render
from django.contrib import messages
import pickle
from random import randrange


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


def index(request):

    global user_guesses
    global random_index
    global secret_word

    context = {}

    if request.method == 'POST':

        if 'check_word_button' in request.POST:

            input_word = request.POST.get('input_word')

            found = False
            for pair in similarity_matrix[secret_word]:
                if input_word in pair:
                    if pair in user_guesses:
                        messages.warning(request, f'Слово {input_word} уже вводилось ранее')
                        found = True
                        break
                    else:
                        if pair[1] == 1:
                            messages.warning(request, 'Вы отгадали слово. Можете продолжать эксперименты')
                        context['pair_for_asked'] = pair
                        user_guesses.append(pair)
                        found = True

            if not found:
                messages.warning(request, 'Неизвестное слово')

        elif 'show_answer_button' in request.POST:

            context['secret_word'] = secret_word

        elif 'start_new_game_button' in request.POST:

            user_guesses = []

            random_index = randrange(guess_words_length)
            secret_word = words4guess[random_index]

    context['user_guesses'] = sorted(user_guesses, key=lambda x: x[1])

    return render(request, 'game/index.html', context)
