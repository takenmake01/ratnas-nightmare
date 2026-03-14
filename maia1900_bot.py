import chess
from chess_player import ChessPlayer
import subprocess
import time
import os
import shutil

class Maia1900Bot(ChessPlayer):
    """
    Chess bot that uses Maia-1900 (via lc0 binary + maia-1900.pb.gz network).
    Plays human-like chess at roughly 1900 Lichess level.
    
    Requirements (do once):
    1. Download lc0 binary for your platform:
       https://github.com/LeelaChessZero/lc0/releases (e.g. lc0-v0.30.0-windows-cpu-avx2.exe or lc0)
    2. Rename/copy it to 'lc0' / 'lc0.exe' in this directory (or add to PATH)
    3. Download Maia-1900 network:
       https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1900.pb.gz
       Place it in the same folder as this file (or adjust NETWORK_PATH below)
    """
    
    def __init__(self):
        self.engine = None
        self._start_engine()
    
    def _start_engine(self):
        """Launch lc0 with Maia-1900 net (only once)."""
        lc0_path = "./lc0"          # adjust if needed → "lc0.exe" on Windows
        network_path = "./maia-1900.pb.gz"  # or "./networks/maia-1900.pb.gz"
        
        if not os.path.isfile(lc0_path):
            raise FileNotFoundError(
                f"lc0 binary not found at {lc0_path}. "
                "Download from https://github.com/LeelaChessZero/lc0/releases "
                "and place it here (rename to lc0 or lc0.exe)."
            )
        
        if not os.path.isfile(network_path):
            raise FileNotFoundError(
                f"Maia-1900 network not found at {network_path}. "
                "Download from https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1900.pb.gz"
            )
        
        # Start lc0 process
        self.engine = subprocess.Popen(
            [
                lc0_path,
                "--weights=" + network_path,
                "--backend=cpu",               # change to cuda/opencl if you have GPU
                "--nncache_size=1000000",      # helps performance
                "--max-prefetch=8",
                "--threads=4",                 # adjust to your CPU cores
                "--move-time=5000",            # think ~5 seconds per move (adjust for strength/speed)
                "--logfile=maia1900.log"       # optional debug log
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for lc0 to initialize
        time.sleep(2)
        
        # Basic readiness check
        self._write("uci")
        response = self._read_until("uciok")
        if "uciok" not in response:
            raise RuntimeError("lc0 did not respond to UCI → check binary/network.")
    
    def _write(self, line):
        if self.engine:
            self.engine.stdin.write(line + "\n")
            self.engine.stdin.flush()
    
    def _read_line(self):
        if self.engine:
            return self.engine.stdout.readline().strip()
        return ""
    
    def _read_until(self, keyword):
        lines = []
        while True:
            line = self._read_line()
            lines.append(line)
            if keyword in line or not line:
                break
        return "\n".join(lines)
    
    def make_move(self, board: chess.Board):
        """
        Main method required by ChessPlayer.
        Returns the chosen move (chess.Move) or None.
        """
        if board.is_game_over():
            return None
        
        # Reset engine state
        self._write("ucinewgame")
        self._write(f"position fen {board.fen()}")
        
        # Ask for best move with fixed thinking time
        # (you can change wtime/btime for real time control if desired)
        self._write("go movetime 5000")   # 5 seconds thinking time — adjust this!
        
        # Read output until bestmove
        response = self._read_until("bestmove")
        
        # Parse bestmove line
        for line in response.split("\n"):
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2:
                    move_str = parts[1]
                    try:
                        move = chess.Move.from_uci(move_str)
                        if move in board.legal_moves:
                            return move
                    except:
                        pass
        
        # Fallback: if something fails, return a random legal move
        legal_moves = list(board.legal_moves)
        if legal_moves:
            return legal_moves[0]  # or random.choice(legal_moves)
        
        return None
    
    def __del__(self):
        """Cleanup engine process on object deletion."""
        if self.engine:
            try:
                self._write("quit")
                self.engine.terminate()
                self.engine.wait(timeout=3)
            except:
                pass
