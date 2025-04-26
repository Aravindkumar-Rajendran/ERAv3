import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
from  torchvision import datasets
import matplotlib.pyplot as plt
from tqdm import tqdm

from model import CIFAR10_ConvNet


cifar_trainset = datasets.CIFAR10(root='./data', train=True, download=True)
data = cifar_trainset.data / 255

cifar_10_mean = data.mean(axis=(0, 1, 2)).tolist()
cifar_10_std = data.std(axis=(0, 1, 2)).tolist()
print(f"Mean : {cifar_10_mean}, Standard deviation: {cifar_10_std}")

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Hyper-parameters
num_epochs = 100
batch_size = 128
learning_rate = 0.001

# Albumentation transforms
transform_train = A.Compose([
    A.HorizontalFlip(),
    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=15, p=0.5),
    A.CoarseDropout(max_holes=1, max_height=16, max_width=16, min_holes=1, min_height=16, min_width=16,
                    fill_value=cifar_10_mean, mask_fill_value=None, p=0.5),
    A.Normalize(mean=cifar_10_mean, std=cifar_10_std),
    ToTensorV2(),
])


transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=cifar_10_mean, std=cifar_10_std),
])

train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=lambda img: transform_train(image=np.array(img))['image'])
test_dataset = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)

train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)


train_losses = []
test_losses = []
train_acc = []
test_acc = []

def train(model, device, train_loader, criterion, optimizer, epoch):
  model.train()
  pbar = tqdm(train_loader)
  correct = 0
  processed = 0
  for batch_idx, (data, target) in enumerate(pbar):
    # get samples
    data, target = data.to(device), target.to(device)
    optimizer.zero_grad()

    # Predict
    y_pred = model(data)

    # Calculate loss
    loss = criterion(y_pred, target)
    train_losses.append(loss)

    # Backpropagation
    loss.backward()
    optimizer.step()

    # Update pbar-tqdm
    pred = y_pred.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
    correct += pred.eq(target.view_as(pred)).sum().item()
    processed += len(data)

    pbar.set_description(desc= f'Loss={loss.item()} Batch_id={batch_idx} Accuracy={100*correct/processed:0.2f}')
    train_acc.append(100*correct/processed)

def test(model, device, test_loader, criterion):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    test_losses.append(test_loss)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

    test_acc.append(100. * correct / len(test_loader.dataset))



def main():
    model = CIFAR10_ConvNet().to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # step_lr
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

    lr_scheduler = torch.optim.lr_scheduler.OneCycleLR(
                                optimizer,
                                max_lr=0.1,
                                steps_per_epoch=len(train_loader),
                                epochs=num_epochs
                            )

    for epoch in range(1, num_epochs + 1):
        print("Epoch: ", epoch)
        print("Learning rate: ", optimizer.state_dict()['param_groups'][0]['lr'])
        train(model, device, train_loader, criterion, optimizer, epoch)
        test(model, device, test_loader, criterion)
        lr_scheduler.step()

    def plot_training_curve(train_losses, train_acc, test_losses, test_acc):
        t = [t_items.item() for t_items in train_losses]
        fig, axs = plt.subplots(2,2,figsize=(15,10))
        axs[0, 0].plot(t)
        axs[0, 0].set_title("Training Loss")
        axs[1, 0].plot(train_acc[4000:])
        axs[1, 0].set_title("Training Accuracy")
        axs[0, 1].plot(test_losses)
        axs[0, 1].set_title("Test Loss")
        axs[1, 1].plot(test_acc)
        axs[1, 1].set_title("Test Accuracy")

    plot_training_curve(train_losses, train_acc, test_losses, test_acc)

if __name__ == "__main__":
    main()

