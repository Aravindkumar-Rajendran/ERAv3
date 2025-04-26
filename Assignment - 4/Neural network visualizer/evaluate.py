import torch
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
from model import SimpleCNN

def evaluate_random_samples():
    # Load the trained model
    model = SimpleCNN()
    model.load_state_dict(torch.load('mnist_cnn.pth'))
    model.eval()
    
    # Prepare test dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('data', train=False, transform=transform)
    
    # Select 10 random samples
    indices = np.random.choice(len(test_dataset), 10, replace=False)
    
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.ravel()
    
    for idx, sample_idx in enumerate(indices):
        image, true_label = test_dataset[sample_idx]
        
        # Get prediction
        with torch.no_grad():
            output = model(image.unsqueeze(0))
            pred_label = output.argmax(dim=1, keepdim=True).item()
        
        # Display image
        axes[idx].imshow(image.squeeze(), cmap='gray')
        axes[idx].set_title(f'True: {true_label}\nPred: {pred_label}')
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig('static/evaluation_results.png')
    plt.close()

if __name__ == '__main__':
    evaluate_random_samples() 