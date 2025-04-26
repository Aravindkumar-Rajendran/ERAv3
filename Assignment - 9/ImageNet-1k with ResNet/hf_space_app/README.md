---
title: ResNet50 Image Classifier
emoji: 🔍
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
---

# ResNet50 Image Classifier

This is a Gradio web application that uses a trained ResNet50 model to classify images. The application provides real-time predictions with top-3 confidence scores for uploaded images.

## Live Demo

Visit the application at [[Resnet50 Classifier](https://huggingface.co/spaces/kishkath/Res-Imagenet)]

## Features

- Real-time image classification
- Top-3 predictions with confidence scores
- Support for various image formats
- User-friendly interface
- Detailed prediction logging
- Example images for testing

## Using the Application

### Quick Start
1. Visit the Hugging Face Space
2. Upload an image using one of these methods:
   - Click the "Upload Image" button
   - Drag and drop an image into the input area
   - Use the provided example images

### Input Requirements
- Supported formats: JPG, PNG, BMP
- Both color and grayscale images accepted
- Images are automatically:
  - Resized to 256 pixels
  - Center cropped to 224x224
  - Normalized using ImageNet statistics

### Output Format
The model returns:
1. **Predicted Class**: The most likely class
2. **Top 3 Predictions**: Three most likely classes with confidence scores

Example output:
```
Predicted Class: dog
Top 3 Predictions:
dog: 95.32%
cat: 3.45%
fox: 1.23%
```

## Technical Details

### Model Architecture
- Base model: ResNet50
- Input size: 224x224 pixels
- Output: Class probabilities through softmax
- Model format: PyTorch (.pth)

### Image Processing Pipeline
```python
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

### File Structure
```
.
├── app.py              # Main application file
├── requirements.txt    # Dependencies
├── README.md          # Documentation
├── src/
│   └── model_10.pth   # Trained model weights
├── models/
│   └── classes.txt    # Class labels
└── examples/          # Example images
    ├── example1.jpg
    └── example2.jpg
```

## Deployment Guide

### Prerequisites
1. Hugging Face account
2. Trained ResNet50 model (.pth format)
3. Class labels file (classes.txt)
4. Example images (optional)

### Deployment Steps
1. Create a new Space:
   - Go to huggingface.co/spaces
   - Click "Create new Space"
   - Select "Gradio" as the SDK
   - Use the provided space configuration from this README

2. Upload required files:
   - All files from the File Structure section
   - Ensure correct file paths in app.py

3. The Space will automatically build and deploy

### Space Configuration
```yaml
title: ResNet50 Image Classifier
emoji: 🔍
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
```

## Troubleshooting

### Common Issues
1. **Model Loading Errors**
   - Verify model path in app.py
   - Check model format and class count

2. **Image Upload Issues**
   - Verify supported formats
   - Check image file size

3. **Prediction Errors**
   - First prediction may be slower (model loading)
   - Check input image quality

### Performance Notes
- CPU inference by default
- GPU supported if available
- Batch processing not supported
- Real-time predictions

## Development

### Requirements
```
torch>=2.0.0
torchvision>=0.15.0
gradio>=4.19.2
Pillow>=9.0.0
numpy>=1.21.0
```

### Local Development
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run locally:
   ```bash
   python app.py
   ```

