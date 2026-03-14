# written with AI
import numpy as np, torch
from torch.utils.data import Dataset, DataLoader
import chess.pgn

# ------------------------------------------------------------------
def load_games_from_pgn(pgn_path: str):
    """Yield successive (board, move) pairs for every half‑move."""
    with open(pgn_path, 'r', encoding='utf-8') as f:
        game = chess.pgn.read_game(f)
        while game is not None:
            board = chess.Board()
            for i, move in enumerate(game.mainline()):          # SAN moves
                yield board.copy(), move                    # 1st: board; 2nd: Move
                board.push(move)                              # advance half‑move
            game = chess.pgn.read_game(f)


# ------------------------------------------------------------------
def board_to_tensor(board):
    """Return an (8,8,12) numpy array for a `chess.Board`."""
    PIECE_MAP = {
        chess.PAWN:0,   chess.PKNIGHT:1,  chess.PBISHOP:2,
        chess.PROOK:3,  chess.PQUEEN:4,   chess.PKING:5,
        # black pieces share the same indices
        chess.PBLACK:6, chess.Knight:7,   chess.Bishop:8,
        chess.Rook:9,   chess.Queen:10,  chess.King:11}
    arr = np.zeros((8,8,12), dtype=np.float32)
    for sq in board.piece_map():
        piece_type = board.piece_at(sq).piece_type
        rank, file = divmod(sq,64)
        arr[rank,file,PIECE_MAP[piece_type]] = 1.0
    return arr

# ------------------------------------------------------------------
def legal_move_to_int(move):
    """Encode a `chess.Move` as an integer in [0,4095]."""
    return move.from_square*64 + move.to_square


class ChessPolicyDataset(Dataset):
    """Dataset that turns PGN → (board_tensor , move_index) pairs."""
    def __init__(self, pgn_file: str, max_positions=None):
        self.samples = []
        for board, mv in load_games_from_pgn(pgn_file):
            X   = board_to_tensor(board)
            y   = legal_move_to_int(mv)
            self.samples.append((X, y))
            if max_positions and len(self.samples)>=max_positions:
                break

    def __len__(self): return len(self.samples)

    def __getitem__(self, idx):
        X,y  = self.samples[idx]
        # torch expects channel first: C×H×W
        tensor_X = torch.tensor(X).permute(2,0,1)
        return tensor_X, torch.tensor(y, dtype=torch.long)