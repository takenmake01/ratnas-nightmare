import chess
import settings
from game_recorder import GameRecord


class GameReplayer:
    """Replays a previously saved game move by move"""
    
    def __init__(self, record: GameRecord):
        self.record = record
        self.board = chess.Board()
        self.current_move_index = 0
        self.white_time = settings.GAME_TIME_LIMIT
        self.black_time = settings.GAME_TIME_LIMIT
        self.is_playing = False
        self.playback_speed = 1.0  # 1.0 = normal speed, 0.5 = half speed, 2.0 = double
        self.move_display_time = 0  # Time to display current move
        self.time_per_move = 1.0  # Seconds to display each move
    
    def get_current_move(self):
        """Get the current move in UCI format"""
        if self.current_move_index < len(self.record.moves):
            return self.record.moves[self.current_move_index]
        return None
    
    def get_current_board(self):
        """Get the board state at current move"""
        return self.board.copy()
    
    def has_moves_remaining(self):
        """Check if there are more moves to replay"""
        return self.current_move_index < len(self.record.moves)
    
    def advance_move(self):
        """Advance to the next move"""
        if not self.has_moves_remaining():
            self.is_playing = False
            return False
        
        move_uci = self.record.moves[self.current_move_index]
        move = chess.Move.from_uci(move_uci)
        
        if move in self.board.legal_moves:
            self.board.push(move)
            times = self.record.times[self.current_move_index]
            self.white_time, self.black_time = times
            self.current_move_index += 1
            self.move_display_time = 0
            return True
        else:
            # Invalid move in record
            print(f"Warning: Invalid move in replay: {move_uci}")
            self.is_playing = False
            return False
    
    def rewind_move(self):
        """Go back one move"""
        if self.current_move_index > 0:
            self.board.pop()
            self.current_move_index -= 1
            
            if self.current_move_index < len(self.record.times):
                times = self.record.times[self.current_move_index]
                self.white_time, self.black_time = times
            self.move_display_time = 0
            return True
        return False
    
    def jump_to_move(self, move_index):
        """Jump to a specific move number"""
        if move_index < 0 or move_index > len(self.record.moves):
            return False
        
        # Reset and replay to target move
        self.board.reset()
        self.current_move_index = 0
        self.white_time = settings.GAME_TIME_LIMIT
        self.black_time = settings.GAME_TIME_LIMIT
        
        for i in range(move_index):
            self.advance_move()
        
        return True
    
    def toggle_playback(self):
        """Toggle between playing and paused"""
        self.is_playing = not self.is_playing
    
    def stop(self):
        """Stop playback and reset to beginning"""
        self.is_playing = False
        self.board.reset()
        self.current_move_index = 0
        self.white_time = settings.GAME_TIME_LIMIT
        self.black_time = settings.GAME_TIME_LIMIT
        self.move_display_time = 0
    
    def get_move_notation(self, move_index):
        """Get the notation for a move"""
        if move_index >= len(self.record.moves):
            return None
        
        # Reconstruct board state up to that move
        board_copy = chess.Board()
        for i in range(move_index):
            move = chess.Move.from_uci(self.record.moves[i])
            board_copy.push(move)
        
        move = chess.Move.from_uci(self.record.moves[move_index])
        return board_copy.san(move)
    
    def update(self, dt):
        """Update playback (call from main game loop)"""
        if not self.is_playing or not self.has_moves_remaining():
            return
        
        self.move_display_time += dt * self.playback_speed
        
        if self.move_display_time >= self.time_per_move:
            self.advance_move()
    
    def get_game_info(self):
        """Get info about the recorded game"""
        return {
            "white": self.record.white_player_name,
            "black": self.record.black_player_name,
            "result": self.record.result,
            "reason": self.record.game_over_reason,
            "total_moves": len(self.record.moves),
            "current_move": self.current_move_index,
            "timestamp": self.record.timestamp,
        }
