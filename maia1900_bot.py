import chess
from chess_player import ChessPlayer
import subprocess
import time
import os
import sys
import shutil
import threading


class Maia1900Bot(ChessPlayer):
    """
    Maia-1900 via Nix-packaged lc0 (nixpkgs#lc0).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._engine = None
        self._started = False
        self.lc0_path = self._find_lc0()

    def _find_lc0(self):
        candidates = [
            shutil.which("lc0"),
            "/run/current-system/sw/bin/lc0",
        ]
        for cand in [c for c in candidates if c]:
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                print(f"[Maia-1900] Found lc0 at: {cand}", file=sys.stderr)
                return cand

        raise FileNotFoundError(
            "[Maia-1900] Could not find 'lc0' executable.\n"
            "Make sure you run with: nix shell nixpkgs#lc0 --command python main.py\n"
            "or have lc0 in your PATH."
        )

    def _drain_stderr(self):
        for line in self._engine.stderr:
            print(f"[lc0 stderr] {line.rstrip()}", file=sys.stderr)

    def _ensure_engine(self):
        if self._started:
            return True

        weights = os.path.abspath("./maia-1900.pb.gz")

        if not os.path.isfile(weights):
            print(f"[Maia-1900] Missing weights file: {weights}", file=sys.stderr)
            return False

        try:
            cmd = [
                "stdbuf", "-oL",
                self.lc0_path,
                f"--weights={weights}",
                "--threads=1",
            ]

            print(f"[Maia-1900] Launching lc0: {' '.join(cmd)}", file=sys.stderr)

            self._engine = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env=os.environ.copy(),
                cwd=os.getcwd()
            )

            threading.Thread(target=self._drain_stderr, daemon=True).start()

            time.sleep(1.0)

            if self._engine.poll() is not None:
                raise RuntimeError(f"lc0 exited immediately with code {self._engine.returncode}")

            self._write("uci")
            resp = self._read_until("uciok", max_lines=2000, timeout=60.0)

            print(f"[Maia-1900] Init response:\n{resp}\n", file=sys.stderr)

            if "uciok" not in resp.lower():
                raise RuntimeError("Did not receive 'uciok' from lc0")

            self._write("isready")
            self._read_until("readyok", max_lines=50, timeout=10.0)

            self._started = True
            print("[Maia-1900] Engine initialized successfully!", file=sys.stderr)
            return True

        except Exception as e:
            print(f"[Maia-1900] Engine startup failed: {str(e)}", file=sys.stderr)
            self._kill_engine()
            return False

    def _write(self, text):
        if self._engine and self._engine.poll() is None:
            try:
                self._engine.stdin.write(text + "\n")
                self._engine.stdin.flush()
            except:
                pass

    def _read_line(self):
        if self._engine and self._engine.poll() is None:
            try:
                return self._engine.stdout.readline().rstrip()
            except:
                pass
        return ""

    def _read_until(self, keyword, max_lines=2000, timeout=60.0):
        lines = []
        deadline = time.time() + timeout
        for _ in range(max_lines):
            if time.time() > deadline:
                print(f"[Maia-1900] _read_until timed out waiting for '{keyword}'", file=sys.stderr)
                break
            line = self._read_line()
            if line:
                lines.append(line)
            if keyword.lower() in line.lower():
                break
        return "\n".join(lines)

    def _kill_engine(self):
        if self._engine:
            try:
                self._write("quit")
                self._engine.terminate()
                self._engine.wait(4.0)
            except:
                pass
            self._engine = None
        self._started = False

    def make_move(self, board: chess.Board):
        if board.is_game_over():
            return None

        if not self._ensure_engine():
            print("[Maia-1900] Engine not available → random fallback move", file=sys.stderr)
            moves = list(board.legal_moves)
            return moves[0] if moves else None

        try:
            self._write("ucinewgame")
            self._write("isready")
            self._read_until("readyok", max_lines=50, timeout=10.0)

            self._write(f"position fen {board.fen()}")
            self._write("isready")
            self._read_until("readyok", max_lines=50, timeout=10.0)

            self._write("go movetime 1500")

            output = self._read_until("bestmove", max_lines=500, timeout=10.0)
            print(f"[Maia-1900] go output:\n{output}", file=sys.stderr)

            for line in output.splitlines():
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) > 1 and parts[1] != "(none)":
                        try:
                            move = chess.Move.from_uci(parts[1])
                            if move in board.legal_moves:
                                return move
                        except ValueError:
                            pass

        except Exception as e:
            print(f"[Maia-1900] Error during make_move: {str(e)}", file=sys.stderr)

        moves = list(board.legal_moves)
        return moves[0] if moves else None
