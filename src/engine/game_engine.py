import random
import uuid
from typing import List, Dict, Any
from datetime import datetime
from src.logic.player import Player
from src.logic.deck import Deck
from src.logic.hand_ranker import hand_rank
from src.utils.exceptions import InsufficientFundsError, InvalidActionError
from src.fileops.history_logger import HistoryLogger

class GameEngine:
    def __init__(self, players: List[Player], history_logger: HistoryLogger, small_blind: int = 25, big_blind: int = 50, game_id: str = None, dealer_pos: int = -1):
        self.players = players
        self.history_logger = history_logger
        self.deck = Deck()
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = 0
        self.game_id = game_id if game_id else str(uuid.uuid4())
        self.dealer_pos = dealer_pos
        self.round_counter = 0

    def get_session_data(self) -> Dict[str, Any]:
        player_data = [
            {"name": p.name, "stack": p.stack, "is_human": p.is_human}
            for p in self.players
        ]
        return {
            "game_id": self.game_id,
            "small_blind": self.small_blind,
            "big_blind": self.big_blind,
            "dealer_pos": self.dealer_pos,
            "players": player_data
        }

    def _post_blinds(self, hand_history: Dict[str, Any]):
        num_players = len(self.players)
        sb_player = self.players[(self.dealer_pos + 1) % num_players]
        bb_player = self.players[(self.dealer_pos + 2) % num_players]
        
        sb_amount = min(self.small_blind, sb_player.stack)
        sb_player.stack -= sb_amount
        sb_player.bet_in_round = sb_amount
        self.pot += sb_amount
        print(f"{sb_player.name} wnosi małą w ciemno: {sb_amount}.")
        hand_history['bets'].append({
            "stage": "blinds", "player_id": sb_player.id, "action": "BLIND", "amount": sb_amount
        })

        bb_amount = min(self.big_blind, bb_player.stack)
        bb_player.stack -= bb_amount
        bb_player.bet_in_round = bb_amount
        self.pot += bb_amount
        print(f"{bb_player.name} wnosi dużą w ciemno: {bb_amount}.")
        hand_history['bets'].append({
            "stage": "blinds", "player_id": bb_player.id, "action": "BLIND", "amount": bb_amount
        })
        hand_history['pot'] = self.pot
    
    def _betting_round(self, stage_name: str, hand_history: Dict[str, Any]):
        if stage_name == 'pre-exchange':
            current_bet = self.big_blind
            start_pos = (self.dealer_pos + 3) % len(self.players)
        else:
            current_bet = 0
            for p in self.players: p.bet_in_round = 0
            start_pos = (self.dealer_pos + 1) % len(self.players)
        
        last_raiser = None
        turn_pos = start_pos
        
        if len([p for p in self.players if p.is_active]) <= 1: return

        active_players_in_round = [p for p in self.players if p.is_active]
        player_to_act = len(active_players_in_round)
        
        while player_to_act > 0:
            player = self.players[turn_pos]
            
            if player.is_active and player.stack > 0:
                print(f"\nPula: {self.pot} | Aktualna stawka: {current_bet}")
                print(f"Tura: {player.name} (Stos: {player.stack})")
                if player.is_human: print(f"Twoje karty: {player.cards_to_str()}")
                
                action, amount = self.prompt_action(player, current_bet)
                hand_history['bets'].append({"stage": stage_name, "player_id": player.id, "action": action, "amount": amount})

                if action == 'fold': player.fold()
                elif action == 'call':
                    player.stack -= amount
                    self.pot += amount
                    player.bet_in_round += amount
                    print(f"{player.name} wyrównuje o {amount}.")
                elif action == 'raise':
                    player.stack -= amount
                    self.pot += amount
                    player.bet_in_round += amount
                    current_bet = player.bet_in_round
                    last_raiser = player
                    print(f"{player.name} przebija do {current_bet}.")
                    player_to_act = len([p for p in self.players if p.is_active])
                elif action == 'check':
                    print(f"{player.name} czeka.")

            turn_pos = (turn_pos + 1) % len(self.players)
            player_to_act -= 1

            if player_to_act <= 0 and last_raiser is not None:
                bets_equalized = all(p.bet_in_round == current_bet or not p.is_active for p in self.players)
                if not bets_equalized:
                    player_to_act = len([p for p in self.players if p.is_active and p.bet_in_round < current_bet])


    def _exchange_cards_phase(self, hand_history: Dict[str, Any]):
        print("\n--- Faza Wymiany Kart ---")
        hand_history['discards'] = {}
        for player in [p for p in self.players if p.is_active]:
            indices = []
            if player.is_human:
                while True:
                    try:
                        indices_str = input(f"Wybierz indeksy do wymiany (0-4) dla {player.name}: ")
                        indices = [] if not indices_str else [int(i) for i in indices_str.split()]
                        if len(indices) > 4: raise ValueError("Można wymienić maks. 4 karty.")
                        break
                    except (ValueError, IndexError) as e: print(f"Błąd: {e}")
            else:
                if hand_rank(player.hand)[0] < 1:
                    indices = random.sample(range(5), k=random.randint(1,4))

            old_cards_str = [str(player.hand[i]) for i in indices]
            hand_history['discards'][str(player.id)] = old_cards_str
            
            self._exchange_cards(player, indices)
            print(f"{player.name} wymienia {len(indices)} kart.")
        
        hand_history['final_hands'] = {
            str(p.id): [str(c) for c in p.hand] for p in self.players if p.is_active
        }

    def play_round(self):
        self.round_counter += 1
        hand_id = f"round_{self.round_counter}"
        print(f"\n" + "="*20 + f" Nowa Runda ({hand_id}) " + "="*20)

        hand_history = {
            "game_id": self.game_id, "hand_id": hand_id, "timestamp": datetime.now().isoformat(),
            "players": [{"id": p.id, "name": p.name, "initial_stack": p.stack} for p in self.players],
            "bets": [], "blinds": {"small": self.small_blind, "big": self.big_blind}
        }

        self.dealer_pos = (self.dealer_pos + 1) % len(self.players)
        self.pot = 0
        for p in self.players:
            p.is_active = True
            p.bet_in_round = 0
            p.hand.clear()
        
        self.deck = Deck()
        self.deck.shuffle()
        hand_history['deck'] = [str(c) for c in self.deck.cards]
        
        self._post_blinds(hand_history)
        
        self.deck.deal(self.players, 5)
        hand_history['initial_hands'] = {p.id: [str(c) for c in p.hand] for p in self.players}

        self._betting_round('pre-exchange', hand_history)
        
        if len([p for p in self.players if p.is_active]) > 1:
            self._exchange_cards_phase(hand_history)
        
        winner = self._showdown()
        if winner:
            print(f"\nZwycięzca: {winner.name}, otrzymuje {self.pot} żetonów.")
            winner.stack += self.pot
            hand_history['winner'] = {"player_id": winner.id, "pot_won": self.pot}
        else:
            print("Brak zwycięzcy w tej rundzie.")

        hand_history['final_player_state'] = [
            {"id": p.id, "name": p.name, "final_stack": p.stack} for p in self.players
        ]

        self.history_logger.save_hand_history(hand_history)
        print(f"Historia rozdania '{hand_id}' została zapisana.")
    
    def _showdown(self) -> Player:
        active_players = [p for p in self.players if p.is_active]
        if not active_players: return None
        if len(active_players) == 1: return active_players[0]
        print("\n--- Wyłożenie Kart (Showdown) ---")
        best_rank = (-1,)
        winner = None
        for player in active_players:
            rank = hand_rank(player.hand)
            print(f"{player.name} ma: {player.cards_to_str()} (Układ: {rank})")
            if rank > best_rank:
                best_rank = rank
                winner = player
        return winner

    def _exchange_cards(self, player: Player, indices: List[int]):
        for idx in sorted(indices, reverse=True):
            old_card = player.hand.pop(idx)
            self.deck.discard_to_bottom(old_card)
        for _ in indices:
            player.take_card(self.deck.draw())

    def prompt_action(self, player: Player, current_bet: int) -> tuple[str, int]:
        if player.is_human:
            return self._prompt_human_action(player, current_bet)
        else:
            return self._get_bot_action(player, current_bet)

    def _prompt_human_action(self, player: Player, current_bet: int) -> tuple[str, int]:
        to_call = current_bet - player.bet_in_round
        valid_actions = ['fold']
        if to_call == 0:
            valid_actions.append('check')
        else:
            valid_actions.append(f'call ({to_call})')
        if player.stack > to_call:
            valid_actions.append('raise')
        valid_actions_str = ', '.join(valid_actions)
        while True:
            action_str = input(f"Wybierz akcję [{valid_actions_str}]: ").lower().strip()
            if action_str == 'fold': return 'fold', 0
            if action_str == 'check' and to_call == 0: return 'check', 0
            if action_str == 'call' and to_call > 0:
                return 'call', min(to_call, player.stack)
            if action_str == 'raise' and player.stack > to_call:
                min_raise = current_bet + to_call if current_bet > 0 else self.big_blind
                max_raise = player.stack + player.bet_in_round
                try:
                    raise_amount = int(input(f"Wprowadź całkowitą kwotę zakładu (min {min_raise}, max {max_raise}): "))
                    if not (min_raise <= raise_amount <= max_raise):
                        raise InvalidActionError(f"Kwota musi być pomiędzy {min_raise} a {max_raise}.")
                    amount_to_add = raise_amount - player.bet_in_round
                    if amount_to_add > player.stack:
                        raise InsufficientFundsError("Niewystarczające środki.")
                    return 'raise', amount_to_add
                except ValueError:
                    print("Nieprawidłowa kwota. Proszę podać liczbę.")
                    continue
            print("Nieprawidłowa akcja. Wybierz jedną z dostępnych opcji.")

    def _get_bot_action(self, player: Player, current_bet: int) -> tuple[str, int]:
        to_call = current_bet - player.bet_in_round
        if to_call > 0:
            if random.random() < 0.8 and player.stack >= to_call:
                return 'call', min(to_call, player.stack)
            else:
                return 'fold', 0
        else:
            if random.random() < 0.7 or player.stack <= self.big_blind:
                return 'check', 0
            else:
                raise_amount = self.big_blind * 2 - player.bet_in_round
                if player.stack > raise_amount:
                     return 'raise', raise_amount
                else:
                     return 'check', 0