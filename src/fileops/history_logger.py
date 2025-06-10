import json
import os
from datetime import datetime

class HistoryLogger:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def save_hand_history(self, history_data: dict) -> None:
        game_id = history_data.get("game_id", "unknown_game")
        hand_id = history_data.get("hand_id", "unknown_hand")
        
        filename = f"history_{game_id}_{hand_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Błąd podczas zapisywania historii rozdania: {e}")