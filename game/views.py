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


def index(request):
    context = {}

    random_index = randrange(guess_words_length)
    secret_word = words4guess[random_index]

    context['secret_word'] = secret_word

    if request.method == 'POST':
        input_word = request.POST.get('input_word')

        found = False
        for pair in similarity_matrix[secret_word]:
            if input_word in pair:
                context['pair_for_asked'] = pair
                found = True

        if not found:
            messages.warning(request, 'Неизвестное слово')

        top_5 = similarity_matrix[secret_word][:5]
        context['top_5'] = top_5
        
    return render(request, 'game/index.html', context)