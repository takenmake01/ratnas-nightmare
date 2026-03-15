# written with AI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader
import torch.nn as nn
from tqdm.auto import tqdm

# local imports – make sure the package root is on PYTHONPATH
from training.config   import *
from training.dataset  import ChessPolicyDataset
from model    import ChessNet

# ------------------------------------------------------------------
def train_one_epoch(net, loader, device, lr=LEARNING_RATE):
    net.train()
    optimizer = optim.AdamW(net.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    for X_batch, y_batch in tqdm(loader):
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        logits = net(X_batch)            # (B,4096)
        loss   = criterion(logits, y_batch)
        loss.backward()
        optimizer.step()


# ------------------------------------------------------------------
if __name__ == "__main__":
    device  = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = ChessPolicyDataset(DATA_PATH)                 # ← read PGN
    loader   = DataLoader(dataset,
                           batch_size=BATCH_SIZE,
                           num_workers=0, # IterableDataset with multiple workers is tricky
                           pin_memory=False)

    net      = ChessNet().to(device)
    writer   = SummaryWriter("runs/epoch_log")            # optional tensorboard

    for epoch in range(EPOCHS):
        print(f"=== Epoch {epoch+1}/{EPOCHS} ===")
        train_one_epoch(net, loader, device)
        # with torch.no_grad():
        #     writer.add_scalar("loss", nn.L1Loss(), global_step=epoch)

    torch.save(net, "../ratnasNightmare.pth")
