from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import os, random, queue
from operator import itemgetter
import json
import copy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

### Global variables ###
player_count = 0
player_number = 0
player_ready_count = 0

# Suspected card
who_accusation = None
what_accusation = None
where_accusation = None

# Actual final cards
actual_who = None
actual_what = None
actual_where = None

# Player info
cwd = os.getcwd()
player_list = []
card_list = []
player_selections = []
name_availability = [True, True, True, True, True, True]
player_list.append([cwd + "\\images\\players\\big_demon",     "H1",  1, "Miss Scarlet", "Red Demon"])
player_list.append([cwd + "\\images\\players\\big_zombie",    "H2",  2, "Prof. Plum", "Big Zombie"])
player_list.append([cwd + "\\images\\players\\green_girl",    "H4",  3, "Col. Mustard", "Female Elf"])
player_list.append([cwd + "\\images\\players\\green_guy",     "H7",  4, "Mrs. Peacock", "Male Elf"])
player_list.append([cwd + "\\images\\players\\knight_orange", "H10", 5, "Mr. Green", "Male Knight"])
player_list.append([cwd + "\\images\\players\\knight_pink",   "H11", 6, "Mrs. White", "Female Knight"])

# Player Order queue
player_order = queue.Queue(maxsize=6)
suspect_order = queue.Queue(maxsize=6)
current_player = 1

class PlayerSelection:
    def __init__(self, player_number):
        self.player_number = player_number
        self.player_name = None
        self.character_name = None
        self.character_file = None


def init_player_cards(total_player_count):
    global player_count, actual_who, actual_what, actual_where
    cards_list = []
    who_cards = [
        'Miss Scarlet',
        'Prof. Plum',
        'Col. Mustard',
        'Mrs. Peacock',
        'Mr. Green',
        'Mrs. White'
    ]

    what_cards = [
        'Candlestick',
        'Knife',
        'Lead Pipe',
        'Revolver',
        'Rope',
        'Wrench'
    ]

    where_cards = [
        'Ballroom',
        'Billiard Room',
        'Conservatory',
        'Dining Room',
        'Hall',
        'Kitchen',
        'Library',
        'Study'
    ]
    location = random.randint(0, len(who_cards) - 1)
    actual_who = who_cards[location]
    who_cards.pop(location)
    location = random.randint(0, len(who_cards) - 1)
    actual_what = what_cards[location]
    what_cards.pop(location)
    location = random.randint(0, len(who_cards) - 1)
    actual_where = where_cards[location]
    where_cards.pop(location)
    cards_option_list = who_cards + what_cards + where_cards
    count = 0
    print(actual_who, " ", actual_what, " ", actual_where)

    for count in range(0, total_player_count):
        cards_list.append(
                {
                    "who": [],
                    "what": [],
                    "where": []
                })
    while True:
        location = random.randint(0, len(cards_option_list) - 1)
        card = cards_option_list[location]
        cards_option_list.pop(location)
        if card in who_cards:
            cards_list[count]["who"].append(card)
        if card in what_cards:
            cards_list[count]["what"].append(card)
        if card in where_cards:
            cards_list[count]["where"].append(card)
        count = count + 1
        if not cards_option_list:
            break
        if count == total_player_count:
            count = 0

    return cards_list


def change_player():
    global current_player, player_order
    next_player = player_order.get()
    while current_player == next_player:
        player_order.put(next_player)
        next_player = player_order.get()
    current_player = next_player
    player_order.put(current_player)
    print("New current player: ", current_player)
    print("New Player order: ", list(player_order.queue))


def remove_player(player_number):
    global player_selections
    delete_index = 0
    for i in range(0, len(player_selections)):
        if player_selections[i].player_number == player_number:
            delete_index = i
        if player_selections[i].player_number > player_number:
            player_selections[i].player_number = player_selections[i].player_number - 1

    del player_selections[delete_index]


def update_player_list():
    global player_selections, player_list
    for i in range(0, len(player_selections)):
        for j in range(0, len(player_list)):
            if player_selections[i].player_name == player_list[j][3]:
                old_number = player_list[j][2]
                player_list[j][0] = player_selections[i].character_file
                player_list[j][4] = player_selections[i].character_name
                for k in range(0, len(player_list)):
                    if player_list[k][2] == player_selections[i].player_number:
                        player_list[k][2] = old_number
                        break
                player_list[j][2] = player_selections[i].player_number

    # Sort the list by the player number
    player_list = sorted(player_list, key=itemgetter(2))


@socketio.on('my message')
def handle_message(message):
    global player_ready_count, player_number, card_list, player_order, current_player, suspect_order, player_list
    global player_selections
    global who_accusation, what_accusation, where_accusation
    global actual_who, actual_what, actual_where
    print('received message type: ' + message['message_type'])

    # Update the player ready values
    if message['message_type'] == "player_ready":
        player_ready_count = player_ready_count + 1
        print("Current player count: ", player_count)
        print("Current start count:  ", player_ready_count)

        # Broadcast the current waiting queue to all
        emit('my message',
             {'message_type': "player_count",
              "player_count": player_count,
              "player_ready_count": player_ready_count},
             broadcast=True
             )
        # Check if all the players are ready
        if player_ready_count == player_count:
            for i in range(0, player_count):
                player_order.put(i + 1)
            emit('my message',
                 {'message_type': "game_start"},
                 broadcast=True
                 )

    # Broadcast message to start the game
    if message['message_type'] == "game_start":
        # Send the game info to the particular player
        update_player_list()
        emit('my message',
             {'message_type': "game_info",
              'player_list': player_list,
              'card_list': card_list[message['player_number'] - 1]
              }
             )

    # Respond to a request to update the players name
    elif message['message_type'] == "update_player_name":
        name_found = False
        for i in range(0, len(player_selections)):
            # Check if the name was already selected
            if player_selections[i].player_name == message['player_name']:
                name_found = True
                emit('my message',
                     {'message_type': "name_already_chosen"}
                     )
                break

        # Update the selection list and confirm with player that selection is fine
        if not name_found:
            for i in range(0, len(player_selections)):
                if player_selections[i].player_number == message['player_number']:
                    player_selections[i].player_name = message['player_name']
                    emit('my message',
                         {'message_type': "player_name_updated"}
                         )
                    break

    # Respond to a request to update the players name
    elif message['message_type'] == "update_player_character":
        # Update the selection list with the new character
        for i in range(0, len(player_selections)):
            if player_selections[i].player_number == message['player_number']:
                player_selections[i].character_name = message['character_name']
                player_selections[i].character_file = message['character_file']
                emit('my message',
                     {'message_type': "player_character_updated"}
                     )
                break

    # Respond to a request to remove the players name
    elif message['message_type'] == "remove_player_name":
        for i in range(0, len(player_selections)):
            if player_selections[i].player_number == message["player_number"]:
                player_selections[i].player_name = None
                emit('my message',
                     {'message_type': "player_name_removed"}
                     )
                break

    # Respond to a request to get the player number
    elif message['message_type'] == "request_number":
        player_number = player_number + 1
        print("Player Number: ", str(player_number))
        player_selections.append(PlayerSelection(player_number))
        emit('my message', {'message_type':  "player_number",
                            'player_number': player_number})

    # Respond to a request to return a player number
    elif message['message_type'] == "return_number":
        player_number = player_number - 1
        remove_player(message["player_number"])
        print("Player Number: ", str(player_number))
        emit('my message', {'message_type': "update_player_number",
                            'player_number': message["player_number"]},
             broadcast=True
             )

    # Emit the direction the player should move
    elif message['message_type'] == "move_player":
        if message["player_number"] == current_player:
            emit('my message',
                 {'message_type': "move_player",
                  "player_number": message["player_number"],
                  "direction": message["direction"],
                  "new_room": message["new_room"]},
                 broadcast=True
                 )
            change_player()
        else:
            emit('my message',
                 {'message_type': "out_of_turn"}
                 )

    # Send the current player
    elif message['message_type'] == "get_current_player":
        emit('my message',
             {'message_type': "current_player",
              "player_number": current_player}
             )

    # Handle player pass message
    elif message['message_type'] == "player_pass":
        if message["player_number"] == current_player:
            change_player()
            emit('my message',
                 {'message_type': "current_player",
                  "player_number": current_player},
                 broadcast=True
                 )
        else:
            emit('my message',
                 {'message_type': "out_of_turn"}
                 )

    # Handle an accusation
    elif message['message_type'] == "accuse":
        if message["current_player"] == current_player:
            if message["who_accusation"] == actual_who and message["what_accusation"] == actual_what and message["where_accusation"] == actual_where:
                emit('my message',
                     {'message_type': "player_wins",
                      'player_number': message["current_player"],
                      "who_accusation": message["who_accusation"],
                      "what_accusation": message["what_accusation"],
                      "where_accusation": message["where_accusation"]
                      }
                     )
            else:
                emit('my message',
                     {'message_type': "player_losses",
                      'player_number': message["current_player"],
                      "who_accusation": message["who_accusation"],
                      "what_accusation": message["what_accusation"],
                      "where_accusation": message["where_accusation"]
                      },
                     broadcast=True
                     )
        else:
            emit('my message',
                 {'message_type': "out_of_turn"}
                 )

    # Start the player suspect loop
    elif message['message_type'] == "start_suspect_loop":
        if message["current_player"] == current_player:
            queue_size = player_order.qsize()
            suspect_order = queue.Queue(maxsize=6)
            for i in range(0, queue_size):
                cur_val = player_order.get()
                if not cur_val == current_player:
                    suspect_order.put(cur_val)
                player_order.put(cur_val)

            # Delete the first option
            cur_suspect = suspect_order.get()
            if cur_suspect == current_player:
                cur_suspect = suspect_order.get()
            print("Suspect order: ", list(suspect_order.queue))
            who_accusation = message["who_accusation"]
            what_accusation = message["what_accusation"]
            where_accusation = message["where_accusation"]
            emit('my message',
                 {'message_type': "init_suspect_loop",
                  "current_responder": cur_suspect,
                  "inquisition_player": current_player,
                  "who_accusation": who_accusation,
                  "what_accusation": what_accusation,
                  "where_accusation": where_accusation},
                 broadcast=True
                 )
        else:
            emit('my message',
                 {'message_type': "out_of_turn"}
                 )

    # Respond to a responder passing
    elif message['message_type'] == "responder_pass":
        if not suspect_order.empty():
            cur_res = suspect_order.get()
            print("Not empty: ", cur_res)
            emit('my message',
                 {'message_type': "next_responder",
                  "current_responder": cur_res,
                  "inquisition_player": current_player,
                  "who_accusation": who_accusation,
                  "what_accusation": what_accusation,
                  "where_accusation": where_accusation},
                 broadcast=True
                 )
        else:
            print("empty")
            emit('my message',
                 {'message_type': "suspect_loop_done"},
                 broadcast=True
                 )
            print("Emitted")
            change_player()

    # Respond to a responder giving card
    elif message['message_type'] == "responder_give":
        emit('my message',
             {'message_type': "card_given",
              "current_responder": message["responder_number"],
              "inquisition_player": current_player,
              "card_given": message["card_given"]},
             broadcast=True
             )
        change_player()

@socketio.on('connect', namespace='/')
def test_connect():
    global player_count, player_ready_count
    print("client connected")
    player_count = player_count + 1
    emit('my message',
         {'message_type': "player_count",
          "player_count": player_count,
          "player_ready_count": player_ready_count},
         broadcast=True
         )

@socketio.on('disconnect', namespace='/c')
def test_disconnect():
    global player_count
    print('Client disconnected')
    player_count = player_count - 1


if __name__ == '__main__':
    card_list = init_player_cards(5)
    socketio.run(app)