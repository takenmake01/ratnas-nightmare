import json
import os
from datetime import datetime
import chess

class GameRecord:
    """Represents a saved game with all necessary data for replay"""
    def __init__(self, white_player_name, black_player_name):
        self.white_player_name = white_player_name
        self.black_player_name = black_player_name
        self.moves = []  # List of move UCI strings
        self.times = []  # List of (white_time, black_time) tuples after each move
        self.timestamp = datetime.now().isoformat()
        self.result = None  # Final game result
        self.game_over_reason = ""

    def add_move(self, move_uci, white_time, black_time):
        """Record a move with the time state after the move"""
        self.moves.append(move_uci)
        self.times.append((white_time, black_time))

    def set_result(self, result, reason=""):
        """Set the final game result"""
        self.result = result
        self.game_over_reason = reason

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "white_player": self.white_player_name,
            "black_player": self.black_player_name,
            "timestamp": self.timestamp,
            "moves": self.moves,
            "times": self.times,
            "result": self.result,
            "game_over_reason": self.game_over_reason,
        }

    @classmethod
    def from_dict(cls, data):
        """Create GameRecord from dictionary"""
        record = cls(data["white_player"], data["black_player"])
        record.moves = data["moves"]
        record.times = data["times"]
        record.timestamp = data["timestamp"]
        record.result = data["result"]
        record.game_over_reason = data["game_over_reason"]
        return record


class GameRecorder:
    """Saves and loads game recordings"""
    
    SAVES_DIR = "game_saves"
    
    def __init__(self):
        if not os.path.exists(self.SAVES_DIR):
            os.makedirs(self.SAVES_DIR)
    
    def save_game(self, record: GameRecord) -> str:
        """
        Save a game record to file.
        Returns the filename of the saved game.
        """
        timestamp = record.timestamp.replace(":", "-").replace(".", "-")
        filename = f"{record.white_player_name}_vs_{record.black_player_name}_{timestamp}.json"
        filepath = os.path.join(self.SAVES_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(record.to_dict(), f, indent=2)
        
        return filename
    
    def load_game(self, filename: str) -> GameRecord:
        """Load a game record from file"""
        filepath = os.path.join(self.SAVES_DIR, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Game save not found: {filename}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return GameRecord.from_dict(data)
    
    def list_saved_games(self) -> list:
        """List all saved game files"""
        if not os.path.exists(self.SAVES_DIR):
            return []
        
        files = [f for f in os.listdir(self.SAVES_DIR) if f.endswith('.json')]
        return sorted(files, reverse=True)  # Most recent first
    
    def delete_game(self, filename: str) -> bool:
        """Delete a saved game"""
        filepath = os.path.join(self.SAVES_DIR, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
