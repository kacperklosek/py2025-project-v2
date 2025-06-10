from typing import List, Tuple
from .card import Card

class Player:
    def __init__(self, id: int, name: str, stack: int, is_human: bool = False):
        self.id = id
        self._stack = stack
        self.name = name
        self.hand: List[Card] = []
        self.is_human = is_human
        self.is_active = True
        self.bet_in_round = 0

    @property
    def stack(self) -> int:
        return self._stack

    @stack.setter
    def stack(self, value: int) -> None:
        if value < 0:
            raise ValueError("Stos nie może być ujemny.")
        self._stack = value

    def take_card(self, card: Card) -> None:
        self.hand.append(card)

    def change_card(self, new_card: Card, idx: int) -> Card:
        if not 0 <= idx < len(self.hand):
            raise IndexError("Indeks karty jest poza zakresem.")
        
        old_card = self.hand[idx]
        self.hand[idx] = new_card
        return old_card

    def get_player_hand(self) -> Tuple[Card, ...]:
        return tuple(self.hand)

    def cards_to_str(self) -> str:
        return ' '.join(str(card) for card in self.hand)

    def fold(self):
        self.is_active = False
        print(f"{self.name} pasuje.")

    @classmethod
    def create_players(cls, player_specs: List[dict]) -> List['Player']:
        return [cls(id=i, **spec) for i, spec in enumerate(player_specs)]