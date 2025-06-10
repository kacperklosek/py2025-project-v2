import json
import os
from datetime import datetime

class SessionManager:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def save_session(self, session_data: dict) -> None:
        game_id = session_data.get("game_id", f"game_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        filepath = os.path.join(self.data_dir, f"session_{game_id}.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Błąd podczas zapisywania sesji: {e}")

    def load_session(self, game_id: str) -> dict:
        filepath = os.path.join(self.data_dir, f"session_{game_id}.json")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                print(f"Wczytywanie sesji z {filepath}...")
                return json.load(f)
        except FileNotFoundError:
            print(f"Błąd: Plik sesji nie został znaleziony w {filepath}")
            return {}
        except (IOError, json.JSONDecodeError) as e:
            print(f"Błąd podczas wczytywania sesji: {e}")
            return {}