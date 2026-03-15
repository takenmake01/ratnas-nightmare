# written with AI
import numpy as np, torch
# from concurrent.features import threadPoolExecutor
from torch.utils.data import Dataset, DataLoader
import chess.pgn

# ------------------------------------------------------------------
def load_games_from_pgn(pgn_path: str):
    """Yield successive (board, move) pairs for every half‑move."""
    print("Reading games...")
    counter = 0

    with open(pgn_path, 'r', encoding='utf-8') as f:
        game = chess.pgn.read_game(f)
        while game is not None:
            board = chess.Board()
            for i, move in enumerate(game.mainline()):          # SAN moves
                yield board.copy(), move.move                    # 1st: board; 2nd: Move
                board.push(move.move)                              # advance half‑move

            counter += 1
            print("Read games: " + str(counter))

            game = chess.pgn.read_game(f)

            # debug
            if (counter >= 2000):
                game = None



# ------------------------------------------------------------------
def board_to_tensor(board):
    """Return an (8,8,12) numpy array for a `chess.Board`."""
    PIECE_MAP = {
        chess.PAWN:0,   chess.KNIGHT:1,  chess.BISHOP:2,
        chess.ROOK:3,  chess.QUEEN:4,   chess.KING:5,
        # black pieces share the same indices
    }
    PIECE_COLOUR_MAP = {
        chess.WHITE:0, chess.BLACK:1
    }
    arr = np.zeros((8,8,12), dtype=np.float32)
    for sq in board.piece_map():
        piece_type = board.piece_at(sq).piece_type
        piece_colour = board.piece_at(sq).color
        rank = chess.square_rank(sq)
        file = chess.square_file(sq)
        arr[rank,file,PIECE_MAP[piece_type]+(6*PIECE_COLOUR_MAP[piece_colour])] = 1.0
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
        tensor_X = torch.tensor(X, device=torch.device("cuda")).permute(2,0,1)
        return tensor_X, torch.tensor(y, dtype=torch.long, device=torch.device("cuda"))