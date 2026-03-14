import chess
import random
from chess_player import ChessPlayer

class RatnasNightmare(ChessPlayer):
    def make_move():
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        return random.choice(legal_moves)