import random
from typing import List
from .card import Card
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .player import Player

class Deck:
    def __init__(self):
        ranks = list(Card.rank_values.keys())
        suits = list(Card.unicode_dict.keys())
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.discards = []

    def __str__(self) -> str:
        return f"Talia z {len(self.cards)} kartami."

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, players: List['Player'], num_cards: int):
        for _ in range(num_cards):
            for player in players:
                if self.cards:
                    player.take_card(self.cards.pop(0))

    def draw(self) -> Card:
        if not self.cards:
            raise ValueError("Nie można dobrać karty z pustej talii.")
        return self.cards.pop(0)

    def discard_to_bottom(self, card: Card) -> None:
        self.discards.append(card)