# MNIST Classification with CI/CD Pipeline

[![ML Pipeline](https://github.com/Aravindkumar-Rajendran/ERA-v3-session-5/actions/workflows/ml-pipeline.yml/badge.svg)](https://github.com/Aravindkumar-Rajendran/ERA-v3-session-5/actions/workflows/ml-pipeline.yml)

This project implements a simple Convolutional Neural Network (CNN) for MNIST digit classification with a complete CI/CD pipeline using GitHub Actions. The model architecture includes two convolutional layers followed by fully connected layers, optimized to have less than 25000 parameters while maintaining > 95% accuracy.

## Project Structure 
```
├── model.py # CNN model architecture
├── train.py # Training script
├── test_model.py # Testing and validation scripts
├── augmentation.py # Data augmentation script
├── requirements.txt # Project dependencies
├── README.md # Project documentation
├── samples/ # Directory for augmented samples
├── .github/
│ └── workflows/
│ └── ml-pipeline.yml # GitHub Actions workflow
└── .gitignore
```

## Requirements

- Python 3.8 or higher
- PyTorch
- torchvision
- pytest

## Local Setup

1. Clone the repository:
```
git clone https://github.com/Aravindkumar-Rajendran/ERA-v3-session-5.git
cd ERA-v3-session-5
```

2. Create and activate a virtual environment:

On Windows
```
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux
```
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

## Running Locally

1. Train the model:
```
python train.py
```
This will:
- Download the MNIST dataset (if not already present)
- Train the model for one epoch
- Save the model with a timestamp (format: `mnist_model_YYYYMMDD_HHMMSS.pth`)

2. Run tests:
```
pytest test_model.py -v
```
This will verify:
- Model architecture 
    - input/output dimensions
    - Parameter count (< 25000)
- Model accuracy (> 95%)
- Model robustness: Accuracy on augmented data (> 90%)
- Prediction confidence: High confidence for correct predictions (> 0.8)
- Model stability: Predictions remain stable under small input perturbations

## CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically:
1. Sets up a Python environment
2. Installs dependencies
3. Trains the model
4. Runs all tests
5. Saves the trained model as an artifact

The pipeline runs automatically on every push to the repository.

## Model Architecture

The CNN architecture consists of:
- Input layer: 28x28 grayscale images
- Conv1: 8 filters (3x3)
- Conv2: 16 filters (3x3)
- Max Pooling layers
- Two Fully Connected layers
- Output: 10 classes (digits 0-9)

Total parameters: ~52,138

## Deployment

Models are automatically saved with timestamps for versioning:
- Format: `mnist_model_YYYYMMDD_HHMMSS.pth`
- Location: Project root directory
- Artifacts: Available in GitHub Actions after successful runs

## Contributing

1. Fork the repository
2. Create your feature branch:
```
git checkout -b feature/your-feature
```
3. Commit your changes:
```
git commit -m 'Add some feature'
```
4. Push to the branch:
```
git push origin feature/your-feature
```
5. Create a Pull Request


  
## Notes

- The model is optimized for CPU training
- Training is limited to one epoch for quick testing
- Accuracy requirements might need adjustment based on your specific needs
- Model artifacts are automatically saved in GitHub Actions