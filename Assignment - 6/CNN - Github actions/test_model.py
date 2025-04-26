import torch
import pytest
from model import MNISTNet

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def test_parameter_count():
    model = MNISTNet()
    param_count = count_parameters(model)
    assert param_count < 20000, f"Model has {param_count} parameters, should be less than 20000"

def test_batch_normalization():
    model = MNISTNet()
    has_bn = any(isinstance(module, torch.nn.BatchNorm2d) for module in model.modules())
    assert has_bn, "Model should use Batch Normalization"

def test_dropout():
    model = MNISTNet()
    has_dropout = any(isinstance(module, torch.nn.Dropout2d) for module in model.modules())
    assert has_dropout, "Model should use Dropout"

def test_gap_or_fc():
    model = MNISTNet()
    has_gap = any(isinstance(module, torch.nn.AvgPool2d) for module in model.modules())
    has_fc = any(isinstance(module, torch.nn.Linear) for module in model.modules())
    assert has_gap or has_fc, "Model should use either Global Average Pooling or Fully Connected Layer" 