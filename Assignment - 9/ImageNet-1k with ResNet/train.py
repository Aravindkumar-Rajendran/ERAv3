import warnings
warnings.filterwarnings('ignore')
import os
import time
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
from tqdm import tqdm

from src.config import Params, get_device
from src.data import get_dataloaders
from src.model import get_resnet50_model
from src.logger import TrainingLogger
from src.utils import show_image

# Initialize parameters and device
params = Params()
device = get_device()
print(f"Using {device} device")

# Data paths
training_folder_name = '/mnt/dataEBS/imagenet/ILSVRC/Data/CLS-LOC/train'
val_folder_name = '/mnt/dataEBS/imagenet/ILSVRC/Data/CLS-LOC/val'

# Get data loaders
train_loader, val_loader = get_dataloaders(params, training_folder_name, val_folder_name, n_gpu=1)

# Initialize model, loss, optimizer
model = get_resnet50_model().to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), 
                          lr=params.lr, 
                          momentum=params.momentum, 
                          weight_decay=params.weight_decay)

# Initialize logger
logger = TrainingLogger(params.name)

def train(dataloader, model, loss_fn, optimizer, epoch, writer):
    size = len(dataloader.dataset)
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    epoch_start_time = time.time()
    
    # Wrap the dataloader with tqdm
    for batch_idx, (X, y) in enumerate(tqdm(dataloader, desc=f'Epoch {epoch}', unit='batch', leave=True, total=len(dataloader))):
        X, y = X.to(device), y.to(device)
        batch_size = len(X)
        
        # Compute prediction and loss
        pred = model(X)
        loss = loss_fn(pred, y)
        
        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        # Calculate statistics
        running_loss += loss.item()
        _, predicted = pred.max(1)
        total += y.size(0)
        correct += predicted.eq(y).sum().item()
        
        current_loss = running_loss/(batch_idx+1)
        current_acc = 100.*correct/total
        
        # Update progress bar with current metrics
        tqdm.write(f'loss: {current_loss:.4f}, acc: {current_acc:.2f}%, processed: {(batch_idx + 1) * batch_size}/{size}')
        
        # Log to tensorboard and file logger every 100 batches
        if batch_idx % 100 == 0:
            step = epoch * size + batch_idx * batch_size
            writer.add_scalar('training/loss', current_loss, step)
            writer.add_scalar('training/accuracy', current_acc, step)
            
            # Log to file
            current_lr = optimizer.param_groups[0]['lr']
            logger.log_training_step(epoch, batch_idx, current_loss, 
                                  current_acc, current_lr, len(dataloader))
    
    epoch_time = time.time() - epoch_start_time
    
    # Log epoch metrics
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100. * correct / total
    writer.add_scalar('training/epoch_loss', epoch_loss, epoch)
    writer.add_scalar('training/epoch_accuracy', epoch_acc, epoch)
    
    # Log epoch summary
    logger.log_epoch_stats(epoch, epoch_loss, epoch_acc, epoch_time)
    
    return epoch_loss, epoch_acc

def test(dataloader, model, loss_fn, epoch, writer, train_dataloader, calc_acc5=False):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct, correct_top5 = 0, 0, 0
    
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
            if calc_acc5:
                _, pred_top5 = pred.topk(5, 1, largest=True, sorted=True)
                correct_top5 += pred_top5.eq(y.view(-1, 1).expand_as(pred_top5)).sum().item()
    
    test_loss /= num_batches
    correct /= size
    correct_top5 /= size
    
    # Log to tensorboard
    step = epoch * len(train_dataloader.dataset)
    if writer is not None:
        writer.add_scalar('test/loss', test_loss, step)
        writer.add_scalar('test/accuracy', 100*correct, step)
        if calc_acc5:
            writer.add_scalar('test/accuracy5', 100*correct_top5, step)
    
    # Log to file
    logger.log_validation_stats(
        epoch, 
        test_loss, 
        100*correct,
        100*correct_top5 if calc_acc5 else None
    )
    
    return test_loss, correct, correct_top5 if calc_acc5 else None

def main():
    # Setup tensorboard
    Path(os.path.join("checkpoints", params.name)).mkdir(parents=True, exist_ok=True)
    writer = SummaryWriter('runs/' + params.name)
    

    # # Initial validation
    # test(val_loader, model, loss_fn, epoch=0, writer=writer, 
    #      train_dataloader=train_loader, calc_acc5=True)
    
    print("starting the training...")
    # Training loop
    for epoch in range(params.num_epochs):
        
        train(train_loader, model, loss_fn, optimizer, epoch=epoch, writer=writer)
        
        # Save checkpoint
        checkpoint = {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "epoch": epoch,
            "params": params
        }
        checkpoint_path = os.path.join("checkpoints", params.name, f"model_{epoch}.pth")
        torch.save(checkpoint, checkpoint_path)
        logger.log_checkpoint(epoch, checkpoint_path)
        
        # Validation
        test(val_loader, model, loss_fn, epoch + 1, writer, 
             train_dataloader=train_loader, calc_acc5=True)

if __name__ == "__main__":
    main()
