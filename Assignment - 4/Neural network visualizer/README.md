# MNIST CNN Training with Real-time Visualization

This project implements a Convolutional Neural Network (CNN) for MNIST digit classification with real-time training visualization using a Flask web server.

## Requirements 

```
pip install torch torchvision flask matplotlib
```

## Project Structure

- `model.py`: Contains the CNN architecture
- `train.py`: Training script with CUDA support
- `server.py`: Flask server for real-time visualization
- `templates/index.html`: Web interface for monitoring training
- `evaluate.py`: Script to evaluate model on random test samples

## How to Run

1. Start the Flask server:
```
python server.py
```

2. In a new terminal, start the training:
```
python train.py
```
  
3. Open your browser and navigate to `http://localhost:5000` to see the training progress and test the model.

  
4. After training completes, evaluate the model:

```
python evaluate.py
```

The training progress will be displayed in real-time on the web interface, showing the loss curve and current training statistics. After training, the evaluation results will be saved as 'evaluation_results.png' in the static folder.

## Features

- Real-time training visualization
- CUDA support for faster training
- Interactive loss curve plotting
- Evaluation on random test samples
- Simple web interface for monitoring

## Model Architecture

The CNN consists of:
- 2 convolutional layers
- 2 max pooling layers
- 2 fully connected layers
- Dropout for regularization