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
    context = {}
    context['secret_word'] = secret_word

    if request.method == 'POST':
        input_word = request.POST.get('input_word')

        found = False
        for pair in similarity_matrix[secret_word]:
            if input_word in pair:
                if pair in user_guesses:
                    messages.warning(request, f'Слово {input_word} уже вводилось ранее')
                    found = True
                    break
                else:
                    context['pair_for_asked'] = pair
                    user_guesses.append(pair)
                    found = True

        if not found:
            messages.warning(request, 'Неизвестное слово')

    context['user_guesses'] = sorted(user_guesses, key=lambda x: x[1])

    return render(request, 'game/index.html', context)
