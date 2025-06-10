class Card:
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    def __init__(self, rank: str, suit: str):
        if rank not in self.rank_values:
            raise ValueError(f"Nieprawidłowa ranga: {rank}")
        if suit not in self.unicode_dict:
            raise ValueError(f"Nieprawidłowy kolor: {suit}")
            
        self.rank = rank
        self.suit = suit
        self.value = self.rank_values[rank]

    def get_value(self) -> tuple[int, str]:
        return (self.value, self.suit)

    def __str__(self) -> str:
        return f"{self.rank}{self.unicode_dict[self.suit]}"
        
    def __repr__(self) -> str:
        return f"Card('{self.rank}', '{self.suit}')"