from collections import Counter
from typing import List
from .card import Card

def hand_rank(hand: List[Card]) -> tuple:
    if not isinstance(hand, list) or len(hand) != 5:
        raise ValueError("Ręka musi być listą 5 obiektów Card.")

    values = sorted([card.value for card in hand], reverse=True)
    suits = [card.suit for card in hand]
    
    is_flush = len(set(suits)) == 1
    is_straight = (values[0] - values[4] == 4) and len(set(values)) == 5
    
    if values == [14, 5, 4, 3, 2]:
        is_straight = True
        values = [5, 4, 3, 2, 1] 

    if is_straight and is_flush:
        if values[0] == 14:
            return (9, )
        return (8, values[0])

    counts = Counter(values)
    rank_counts = sorted(counts.values(), reverse=True)
    major_kickers = sorted(counts.keys(), key=lambda k: (counts[k], k), reverse=True)

    if rank_counts[0] == 4:
        return (7, major_kickers[0], major_kickers[1])
        
    if rank_counts == [3, 2]:
        return (6, major_kickers[0], major_kickers[1])

    if is_flush:
        return (5, *values)

    if is_straight:
        return (4, values[0])

    if rank_counts[0] == 3:
        return (3, major_kickers[0], *[k for k in major_kickers if k != major_kickers[0]])

    if rank_counts == [2, 2, 1]:
        return (2, major_kickers[0], major_kickers[1], major_kickers[2])

    if rank_counts[0] == 2:
        pair_value = major_kickers[0]
        kickers = [k for k in major_kickers if k != pair_value]
        return (1, pair_value, *kickers)

    return (0, *values)