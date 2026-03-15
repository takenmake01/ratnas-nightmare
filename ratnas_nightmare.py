import torch, chess
import random
from chess_player import ChessPlayer
from model import ChessNet
from training.dataset import board_to_tensor

class RatnasNightmare(ChessPlayer):
    def __init__(self, name):
        super().__init__(name)

        # torch.serialization.add_safe_globals([ChessNet])

        # AI
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # self.net = ChessNet().to(self.device)
        # self.net.load_state_dict(torch.load("ratnasNightmare.pth", weights_only=False, map_location=self.device))
        self.net = torch.load("ratnasNightmare.pth", weights_only=False, map_location=self.device)

    # AI
    def predict_best_move(self, board):
        self.net.eval()

        with torch.no_grad():                   # no grads needed
            # 1. Convert the board to (8,8,12) → (B=1,C=12,H=8,W=8)
            x = torch.tensor(board_to_tensor(board)).permute(2,0,1).unsqueeze(0).to(self.device)

            # 2. Forward through the network – shape: (B,4096)
            logits   = self.net(x)                                   # forward pass

            # 3. Softmax → prob‑distribution over all legal half‑moves
            probs    = torch.nn.functional.softmax(logits, dim=1)[0]

            # 4. Pick top‑k indices – these are just flat numbers in [0,4095]
            top_idx   = torch.topk(probs, 3).indices.cpu().numpy()

        # 5. Decode index → `chess.Move` (from_square * 64 + to_square)
        moves = [chess.Move(i//64, i%64) for i in top_idx]
        return moves

    def make_move(self, board):
        legal_moves = list(board.legal_moves)

        if not legal_moves:
                return None

        for move in self.predict_best_move(board):
            if move in legal_moves:
                print("Legal NN move")
                return move
            
        else:
            print("[WARNING] All NN suggested moves illegal, falling back to random selection")
            
            return random.choice(legal_moves)