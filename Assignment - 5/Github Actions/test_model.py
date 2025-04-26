import torch
from torchvision import datasets, transforms
from model import MNISTNet
import pytest
import glob
import os
import numpy as np
from augmentation import get_augmented_transforms
import torch.nn.functional as F

def get_latest_model():
    model_files = glob.glob('mnist_model_*.pth')
    return max(model_files, key=os.path.getctime)

def test_model_architecture():
    model = MNISTNet()
    
    # Test input shape
    test_input = torch.randn(1, 1, 28, 28)
    output = model(test_input)
    assert output.shape == (1, 10), "Output shape is incorrect"
    
    # Test parameter count
    total_params = sum(p.numel() for p in model.parameters())
    assert total_params < 25000, f"Model has {total_params} parameters, should be < 25000"

def test_model_accuracy():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MNISTNet().to(device)
    
    # Load the latest trained model
    model_path = get_latest_model()
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    # Prepare test data
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000)
    
    # Evaluate
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            _, predicted = torch.max(outputs.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    
    accuracy = 100 * correct / total
    print(f"Model accuracy is {accuracy}%")
    assert accuracy > 95, f"Model accuracy is {accuracy}%, should be > 95%"

def test_model_robustness():
    """Test model performance on augmented data"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MNISTNet().to(device)
    
    model_path = get_latest_model()
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    # Test with augmented data
    transform = get_augmented_transforms()
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000)
    
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            _, predicted = torch.max(outputs.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    
    augmented_accuracy = 100 * correct / total
    assert augmented_accuracy > 90, f"Model accuracy on augmented data is {augmented_accuracy}%, should be > 90%"

def test_prediction_confidence():
    """Test if model predictions are confident (high probability for correct class)"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MNISTNet().to(device)
    
    model_path = get_latest_model()
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=100)
    
    model.eval()
    confidences = []
    
    with torch.no_grad():
        for data, target in list(test_loader)[:1]:  # Test only first batch
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, dim=1)
            confidences.extend(confidence.cpu().numpy())
    
    avg_confidence = np.mean(confidences)
    assert avg_confidence > 0.8, f"Average prediction confidence is {avg_confidence}, should be > 0.8"

def test_model_stability():
    """Test if model predictions are stable under small input perturbations"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MNISTNet().to(device)
    
    model_path = get_latest_model()
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    # Create a sample input
    x = torch.randn(1, 1, 28, 28).to(device)
    
    # Add small random noise
    noise_level = 0.1
    x_noisy = x + noise_level * torch.randn_like(x)
    
    model.eval()
    with torch.no_grad():
        pred1 = model(x)
        pred2 = model(x_noisy)
    
    # Compare predictions
    diff = torch.norm(pred1 - pred2)
    assert diff < 1.0, f"Model predictions vary too much under small perturbations: {diff}"

if __name__ == "__main__":
    pytest.main([__file__]) 