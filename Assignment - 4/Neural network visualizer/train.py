import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import json
import torch.nn.functional as F
from model import SimpleCNN
import os
from tqdm import tqdm

# Check for CUDA availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Data preparation
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('data', train=False, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64)

print(f"Training samples: {len(train_dataset)}")
print(f"Test samples: {len(test_dataset)}")

# Initialize model and optimizer
model = SimpleCNN().to(device)
optimizer = optim.Adam(model.parameters())

def train(epoch):
    model.train()
    train_loss = 0
    correct = 0
    total = 0
    pbar = tqdm(train_loader, desc=f'Epoch {epoch}')
    
    total_loss = 0
    num_batches = len(train_loader)
    batches_per_epoch = len(train_loader)
    
    for batch_idx, (data, target) in enumerate(pbar):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        total_loss += loss.item()
        
        # Calculate accuracy
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)
        current_accuracy = 100. * correct / total
        
        # Calculate current sub-epoch
        current_sub_epoch = epoch + (batch_idx / batches_per_epoch)
        
        # Update progress bar
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'accuracy': f'{current_accuracy:.2f}%'
        })
        
        # Save progress more frequently (every 0.1 epochs)
        if batch_idx % (batches_per_epoch // 10) == 0 or batch_idx == num_batches - 1:
            # Get test accuracy without progress bar
            test_loss, test_accuracy = test(show_progress=False)
            
            progress = {
                'epoch': current_sub_epoch,
                'batch': batch_idx,
                'loss': loss.item(),
                'avg_loss': train_loss / (batch_idx + 1),
                'accuracy': current_accuracy,
                'test_accuracy': test_accuracy
            }
            with open('static/training_progress.json', 'w') as f:
                json.dump(progress, f)
    
    # Final evaluation for the epoch
    epoch_avg_loss = total_loss / num_batches
    epoch_accuracy = 100. * correct / total
    
    # Final test with progress bar
    test_loss, test_accuracy = test(show_progress=True)
    
    with open('static/epoch_progress.json', 'a') as f:
        json.dump({
            'epoch': epoch,
            'avg_loss': epoch_avg_loss,
            'train_accuracy': epoch_accuracy,
            'test_accuracy': test_accuracy
        }, f)
        f.write('\n')
    
    return epoch_avg_loss, epoch_accuracy, test_accuracy

def test(show_progress=True):
    model.eval()
    test_loss = 0
    correct = 0
    
    # Use tqdm only if show_progress is True
    loader = tqdm(test_loader, desc='Testing') if show_progress else test_loader
    
    with torch.no_grad():
        for data, target in loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    return test_loss, accuracy

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    
    # Clear previous epoch progress
    with open('static/epoch_progress.json', 'w') as f:
        pass
    
    print("Starting training...")
    for epoch in range(0, 5):
        avg_loss, train_accuracy, test_accuracy = train(epoch)
        print(f'Epoch: {epoch}')
        print(f'Average training loss: {avg_loss:.4f}')
        print(f'Training accuracy: {train_accuracy:.2f}%')
        print(f'Test accuracy: {test_accuracy:.2f}%\n')
    
    # Save the model
    torch.save(model.state_dict(), 'mnist_cnn.pth')
    print("Training completed. Model saved as 'mnist_cnn.pth'") 