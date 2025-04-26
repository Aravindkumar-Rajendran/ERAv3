import gradio as gr
import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models import resnet50
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path configurations
MODEL_PATH = Path('src/model_10.pth')
CLASSES_PATH = Path('models/classes.txt')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Image preprocessing - using the same transforms as training
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def load_classes():
    with open(CLASSES_PATH) as f:
        return [line.strip() for line in f.readlines()]

def load_model():
    """
    Load the trained ResNet50 model
    """
    try:
        # Initialize model
        model = resnet50(weights=None)
        num_classes = len(load_classes())
        model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
        
        # Load checkpoint
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
        
        # Extract state dict from checkpoint
        if isinstance(checkpoint, dict):
            if "model" in checkpoint:
                state_dict = checkpoint["model"]
            elif "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            elif "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint
            
        # Clean state dict keys
        new_state_dict = {}
        for k, v in state_dict.items():
            name = k.replace("module.", "")
            if name.startswith("model."):
                name = name[6:]
            new_state_dict[name] = v
        
        # Load state dict and set to eval mode
        model.load_state_dict(new_state_dict, strict=False)
        model.to(DEVICE)
        model.eval()
        
        logger.info("Model loaded successfully")
        return model
    
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

# Global variables
CLASSES = load_classes()
MODEL = load_model()

def predict_image(image):
    """
    Predict class for input image with top-3 accuracy
    """
    try:
        if image is None:
            return "No image provided", "Please upload an image"
        
        # Convert to PIL Image if needed
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        # Preprocess image
        input_tensor = transform(image).unsqueeze(0).to(DEVICE)
        
        # Get prediction
        with torch.no_grad():
            output = MODEL(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
        # Get top-3 predictions
        top3_prob, top3_indices = torch.topk(probabilities, k=3)
        
        # Format predictions
        predictions = []
        for prob, idx in zip(top3_prob, top3_indices):
            class_name = CLASSES[idx]
            confidence = prob.item() * 100
            predictions.append(f"{class_name}: {confidence:.2f}%")
        
        # Join predictions with newlines
        predictions_text = "\n".join(predictions)
        
        # Get top prediction
        predicted_class = CLASSES[top3_indices[0]]
        
        # Log predictions
        logger.info(f"Predicted class: {predicted_class}")
        logger.info(f"Top 3 predictions:\n{predictions_text}")
        
        return predicted_class, predictions_text
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return "Error in prediction", str(e)

# Create Gradio interface
iface = gr.Interface(
    fn=predict_image,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=[
        gr.Textbox(label="Predicted Class"),
        gr.Textbox(label="Top 3 Predictions", lines=3)
    ],
    title="ResNet50 Image Classifier",
    description=(
        "Upload an image to classify.\n"
        "The model will predict the class and show confidence scores for the top 3 predictions."
    ),
    examples=[
        ["examples/example1.jpg"],
        ["examples/example2.jpg"]
    ] if Path("examples").exists() else None,
    theme=gr.themes.Base()
)

# Launch the app
if __name__ == "__main__":
    iface.launch() 