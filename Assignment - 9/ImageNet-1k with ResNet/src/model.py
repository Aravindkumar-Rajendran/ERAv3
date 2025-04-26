import torch.nn as nn
from torchvision import models

def get_resnet50_model():
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 1000)
    return model 