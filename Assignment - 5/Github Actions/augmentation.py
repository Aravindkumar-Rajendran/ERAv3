import torch
from torchvision import transforms
import matplotlib.pyplot as plt
from torchvision.datasets import MNIST
import os
import random

def get_augmented_transforms():
    return transforms.Compose([
        transforms.RandomRotation(15),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

def save_augmented_samples():
    # Create samples directory if it doesn't exist
    if not os.path.exists('samples'):
        os.makedirs('samples')
    
    # Original transform
    basic_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Load dataset
    original_dataset = MNIST('./data', train=True, download=True, transform=basic_transform)
    augmented_dataset = MNIST('./data', train=True, download=True, transform=get_augmented_transforms())
    
    # Plot and save samples
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    
    for i, d in zip(range(5), random.sample(range(len(original_dataset)), 5)):
        # Get same image with different transforms
        img_orig, label = original_dataset[d]
        img_aug, _ = augmented_dataset[d]
        
        # Convert to numpy and denormalize
        img_orig = img_orig[0].numpy()
        img_aug = img_aug[0].numpy()
        
        # Plot
        axes[0][i].imshow(img_orig, cmap='gray')
        axes[0][i].set_title(f'Original {label}')
        axes[0][i].axis('off')
        
        axes[1][i].imshow(img_aug, cmap='gray')
        axes[1][i].set_title(f'Augmented {label}')
        axes[1][i].axis('off')
    
    plt.tight_layout()
    plt.savefig('samples/augmented_samples.png')
    plt.close()

if __name__ == "__main__":
    save_augmented_samples() 