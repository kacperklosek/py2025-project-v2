import random

def deck():
    
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    cards = [f"{rank}{suit}" for suit in suits for rank in ranks]
    random.shuffle(cards)
    return cards

def deal(deck, n):
    return [deck.pop() for _ in range(n)]

if __name__ == "__main__":
    d = deck()
    hand = deal(d, 5)
    print("Twoja ręka:", hand)
    print("Pozostało kart w talii:", len(d))
