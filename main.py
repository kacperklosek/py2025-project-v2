import json
import os
from src.logic.player import Player
from src.engine.game_engine import GameEngine
from src.fileops.session_manager import SessionManager
from src.fileops.history_logger import HistoryLogger

def load_config() -> dict:
    default_config = {
        "small_blind": 25,
        "big_blind": 50,
        "initial_stack": 1000,
        "players": [
            {"name": "Gracz (Ty)", "is_human": True},
            {"name": "Bot Adam", "is_human": False},
            {"name": "Bot Ewa", "is_human": False},
        ]
    }
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            print("Wczytano konfigurację z pliku config.json.")
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ostrzeżenie: Nie udało się wczytać pliku config.json ({e}). Używam domyślnych ustawień.")
        return default_config

def replay_hand_from_history(filename: str):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku historii '{filename}'.")
        return
    except json.JSONDecodeError:
        print(f"Błąd: Plik historii '{filename}' jest uszkodzony.")
        return

    player_map = {p['id']: p['name'] for p in history['players']}
    print("\n" + "="*20)
    print(f"Odtwarzanie rozdania: {history['hand_id']}")
    print(f"ID Gry: {history['game_id']}")
    print(f"Data: {history['timestamp']}")
    print("="*20 + "\n")
    print("--- Stan początkowy ---")
    for p in history['players']:
        print(f"Gracz: {p['name']} (ID: {p['id']}), Stos: {p['initial_stack']}")
    print("-" * 20)
    print("\n--- Rozdane karty ---")
    for player_id_str, hand in history['initial_hands'].items():
        player_id = int(player_id_str)
        print(f"{player_map[player_id]}: {' '.join(hand)}")
    print("-" * 20)
    print("\n--- Przebieg rundy ---")
    for bet_info in history.get('bets', []):
        player_name = player_map[bet_info['player_id']]
        action = bet_info['action'].upper()
        amount = bet_info.get('amount', 0)
        if action == 'BLIND':
            print(f"[{bet_info['stage']}] {player_name} wnosi {amount} żetonów jako blind.")
        elif action in ['CALL', 'RAISE']:
            print(f"[{bet_info['stage']}] {player_name} wykonuje {action} za {amount} żetonów.")
        else:
            print(f"[{bet_info['stage']}] {player_name} wykonuje {action}.")
    if 'discards' in history and history['discards']:
        print("\n--- Wymiana kart ---")
        for player_id_str, discarded_cards in history['discards'].items():
            player_id = int(player_id_str)
            if discarded_cards:
                print(f"{player_map[player_id]} wymienia {len(discarded_cards)} karty: {' '.join(discarded_cards)}")
            else:
                print(f"{player_map[player_id]} nie wymienia kart.")
        print("-" * 20)
    print("\n--- Showdown (Wyłożenie kart) ---")
    if 'final_hands' in history:
        for player_id_str, hand in history['final_hands'].items():
            player_id = int(player_id_str)
            print(f"{player_map[player_id]}: {' '.join(hand)}")
    if 'winner' in history:
        winner_name = player_map[history['winner']['player_id']]
        pot_won = history['winner']['pot_won']
        print(f"\nZWYCIĘZCA: {winner_name}, wygrywa {pot_won} żetonów.")
    else:
        print("\nBrak jednoznacznego zwycięzcy w zapisie.")
    print("\n" + "="*20)
    print("Koniec odtwarzania.")
    print("="*20 + "\n")

def main():
    print("Witaj w Pokerze Pięciokartowym Dobieranym!")
    session_manager = SessionManager()
    history_logger = HistoryLogger()
    game = None
    while True:
        choice = input("Wybierz opcję: [N]owa gra, [W]czytaj grę, [O]dtwórz rozdanie, [Z]akończ: ").upper()
        if choice == 'N':
            print("Rozpoczynanie nowej gry...")
            config = load_config()
            
          
            print(f"DEBUG: Wczytano {len(config['players'])} graczy z konfiguracji.")

            player_specs = [
                {"name": p_data['name'], "stack": config['initial_stack'], "is_human": p_data['is_human']}
                for p_data in config['players']
            ]
            players = Player.create_players(player_specs)
            game = GameEngine(
                players=players,
                history_logger=history_logger,
                small_blind=config['small_blind'],
                big_blind=config['big_blind']
            )
            try:
                while True:
                    game.players = [p for p in game.players if p.stack > 0]
                    if len(game.players) < 2:
                        print("Zbyt mało graczy, aby kontynuować.")
                        break
                    game.play_round()
                    session_data = game.get_session_data()
                    session_manager.save_session(session_data)
                    print(f"Postęp gry został zapisany. ID Twojej gry to: {game.game_id}")
                    if input("Zagrać kolejną rundę? (t/n): ").lower() != 't':
                        break
            except KeyboardInterrupt:
                print("\nGra przerwana.")
            print("\nKoniec Gry.")
        elif choice == 'W':
            print("Wczytywanie sesji nie jest obecnie w pełni wspierane w tym trybie.")
        elif choice == 'O':
            print("\n--- Odtwarzanie Historii Rozdania ---")
            game_id_input = input("Podaj ID gry, z której chcesz odtworzyć rozdanie: ")
            hand_id_input = input("Podaj ID rozdania (np. round_1): ")
            filename = os.path.join('data', f"history_{game_id_input}_{hand_id_input}.json")
            replay_hand_from_history(filename)
        elif choice == 'Z':
            print("Do widzenia!")
            break
        else:
            print("Nieprawidłowy wybór.")

if __name__ == "__main__":
    main()