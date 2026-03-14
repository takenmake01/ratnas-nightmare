# written with AI
# ── configuration constants ────────────────────────

import os, torch, chess.pgn
from pathlib import Path

DATA_PATH   = Path("zlichess_db_standard_rated_2017-12.pgn")    # ← change if your data lives elsewhere
BATCH_SIZE  = 64
LEARNING_RATE=3e-4
EPOCHS      = 30
NUM_WORKERS = 4   # adjust for CPU/GPU