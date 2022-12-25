from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
import pickle
from random import choice
from math import ceil
from .models import Room
from .utils import morph
from .utils import get_sorted_similarities
from .utils import stop_words
from .utils import words4guess
from .utils import all_words
from .utils import array_to_json, json_to_array
from .utils import get_indexes


def render_room(request, room_id):

    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise Http404("Такой комнаты не существует")

    context = {'room': room}
    similarities = json_to_array(room.similarities)
    users_guesses = json_to_array(room.all_guesses)

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
                        if pair in users_guesses:
                            messages.warning(request, f'Рейтинг слова "{lemmatized}" уже известен')
                            found = True
                            break
                        else:
                            if pair[1] == 1:
                                room.is_victory = True
                                room.is_revealed = True
                            context['pair_for_asked'] = pair
                            users_guesses.append(pair)
                            users_guesses = sorted(users_guesses, key=lambda x: x[1])

                            room.guess_counter += 1
                            found = True

                if not found:
                    messages.warning(request, 'Неизвестное слово')

        elif 'show_answer_button' in request.POST:

            if room.is_revealed:
                messages.warning(request, 'Секретное слово уже известно')
            else:
                users_guesses.append(similarities[0])
                users_guesses = sorted(users_guesses, key=lambda x: x[1])
                room.is_revealed = True

        elif 'start_new_game_button' in request.POST:

            new_secret_word = choice(words4guess)
            new_similarities = get_sorted_similarities(new_secret_word)

            room.secret_word = new_secret_word
            room.all_guesses = array_to_json([])
            room.similarities = array_to_json(new_similarities)
            room.guess_counter = 0
            room.hint_counter = 0
            room.is_victory = False
            room.is_revealed = False

            room.save()

            return render(request, 'game/room.html', context)

        elif 'give_hint_button' in request.POST:

            if not users_guesses:
                messages.warning(request, 'Сделайте хотя бы одно предположение')

            elif users_guesses[0][1] == 1:
                messages.warning(request, 'Секретное слово уже известно')

            elif users_guesses[0][1] == 2:
                for i in range(3, len(similarities)):
                    if i in get_indexes(users_guesses):
                        continue

                    placed = False
                    for pair in similarities:
                        if pair[1] == i:
                            users_guesses.append(pair)
                            users_guesses = sorted(users_guesses, key=lambda x: x[1])
                            placed = True
                            room.hint_counter += 1
                            break

                    if placed:
                        break
            else:
                top_guess = get_indexes(users_guesses)[0]
                need_to_place = ceil(top_guess / 2)

                for pair in similarities:
                    if pair[1] == need_to_place:
                        users_guesses.append(pair)
                        users_guesses = sorted(users_guesses, key=lambda x: x[1])
                        room.hint_counter += 1
                        break

        elif 'show_top_100_closest' in request.POST:

            top_100 = similarities[:100]
            local_context = {'top_100': top_100}

            return render(request, 'game/top_100.html', local_context)

        elif 'get_to_home_button' in request.POST:

            redirect('index')

    context['all_guesses'] = users_guesses
    room.all_guesses = array_to_json(users_guesses)
    room.save()

    return render(request, 'game/room.html', context)


def index(request):

    team_rooms = Room.objects.filter(created_for_teams=True)
    context = {'team_rooms': team_rooms}

    if request.method == 'POST':

        room_count = len(Room.objects.all())

        if 'quick_start_button' in request.POST:

            if room_count >= 10:
                messages.warning(request, 'Достигнут лимит количества комнат')
                return render(request, 'game/index.html', context)

            secret_word = choice(words4guess)
            all_guesses = array_to_json([])

            similarities_ = get_sorted_similarities(secret_word)
            similarities = array_to_json(similarities_)

            new_room = Room(
                secret_word=secret_word,
                all_guesses=all_guesses,
                similarities=similarities,
            )
            new_room.save()

            return redirect('/game/room/' + str(new_room.pk) + '/')

        elif 'multiplayer_game_button' in request.POST:

            if room_count >= 10:
                messages.warning(request, 'Достигнут лимит количества комнат')
                return render(request, 'game/index.html', context)

            return redirect('/game/room_registration/')

        elif 'join_room' in request.POST:

            room_pk = request.POST.get('room_pk')
            return redirect('/game/room/' + room_pk + '/')

    return render(request, 'game/index.html', context)


def room_registration(request):

    if request.method == 'POST':

        if 'back_to_index' in request.POST:
            return redirect('index')

        elif 'create_room' in request.POST:

            room_name = request.POST.get('room_name')
            secret_word = choice(words4guess)
            all_guesses = array_to_json([])

            similarities_ = get_sorted_similarities(secret_word)
            similarities = array_to_json(similarities_)

            new_room = Room(
                name=room_name,
                secret_word=secret_word,
                all_guesses=all_guesses,
                similarities=similarities,
                created_for_teams=True,
            )
            new_room.save()

            return redirect('/game/room/' + str(new_room.pk) + '/')

    return render(request, 'game/room_registration.html', {})
