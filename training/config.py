# written with AI
# ── configuration constants ────────────────────────

import os, torch, chess.pgn
from pathlib import Path

DATA_PATH   = Path("training/lichess_db_standard_rated_2013-01.pgn")    # ← change if your data lives elsewhere
BATCH_SIZE  = 64
LEARNING_RATE=3e-4
EPOCHS      = 1
NUM_WORKERS = 128   # adjust for CPU/GPU