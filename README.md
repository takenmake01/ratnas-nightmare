# TWU-Hackathon-2026
It is Backend software/code to host the chess bots made by participants and pit them against each other for one final winner.

## Creating Your Own Bot

### Quick Start
1. Open `bot_template.py` to see the template structure
2. Create a new Python file in this directory (e.g., `my_bot.py`)
3. Inherit from `ChessPlayer` and implement the `make_move()` method
4. Test your bot in `main.py`

### Basic Example
```python
import chess
from chess_player import ChessPlayer

class MyBot(ChessPlayer):
    def make_move(self, board):
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # Your strategy here!
        import random
        return random.choice(legal_moves)
```

### Using Your Bot
In `main.py`, import and wrap your bot:
```python
from my_bot import MyBot
from secure_bot import SecureBotWrapper

player1 = SecureBotWrapper(MyBot, "My Bot Name")
```

### Useful Board Methods
- `board.legal_moves` - all valid moves
- `board.is_capture(move)` - check if a move captures
- `board.piece_at(square)` - get piece at a square
- `board.turn` - whose turn (chess.WHITE or chess.BLACK)
- `board.is_check()` - is the king in check?
- `board.is_checkmate()` - is it checkmate?
