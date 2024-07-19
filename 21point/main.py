from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Card deck and values
suits = ['♥️', '♦️', '♣️', '♠️']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


def create_deck():
    return [{'suit': suit, 'value': value} for suit in suits for value in values]


def draw_card(deck):
    card = random.choice(deck)
    deck.remove(card)
    return card


def calculate_score(hand):
    score = sum(card_values[card['value']] for card in hand)
    aces = sum(1 for card in hand if card['value'] == 'A')
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start')
def start():
    deck = create_deck()
    player_hand = [draw_card(deck), draw_card(deck)]
    dealer_hand = [draw_card(deck), draw_card(deck)]
    session['deck'] = deck
    session['player_hand'] = player_hand
    session['dealer_hand'] = dealer_hand
    session['player_score'] = calculate_score(player_hand)
    session['dealer_score'] = calculate_score(dealer_hand)
    return redirect(url_for('game'))


@app.route('/game')
def game():
    player_hand = session.get('player_hand', [])
    dealer_hand = session.get('dealer_hand', [])
    player_score = session.get('player_score', 0)
    dealer_score = session.get('dealer_score', 0)
    return render_template('game.html', player_hand=player_hand, dealer_hand=dealer_hand, player_score=player_score,
                           dealer_score=dealer_score)


@app.route('/hit')
def hit():
    deck = session.get('deck', [])
    player_hand = session.get('player_hand', [])
    player_hand.append(draw_card(deck))
    session['player_hand'] = player_hand
    session['player_score'] = calculate_score(player_hand)
    session['deck'] = deck

    if session['player_score'] > 21:
        return redirect(url_for('result'))

    return redirect(url_for('game'))


@app.route('/stand')
def stand():
    deck = session.get('deck', [])
    dealer_hand = session.get('dealer_hand', [])
    dealer_score = session.get('dealer_score', 0)

    while dealer_score < 17:
        dealer_hand.append(draw_card(deck))
        dealer_score = calculate_score(dealer_hand)

    session['dealer_hand'] = dealer_hand
    session['dealer_score'] = dealer_score
    session['deck'] = deck
    return redirect(url_for('result'))


@app.route('/result')
def result():
    player_score = session.get('player_score', 0)
    dealer_score = session.get('dealer_score', 0)
    return render_template('result.html', player_score=player_score, dealer_score=dealer_score)


if __name__ == '__main__':
    app.run(debug=True)