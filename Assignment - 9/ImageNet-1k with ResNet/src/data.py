import torch
import torchvision
import torchvision.transforms as transforms
import albumentations as A
from PIL import Image
import numpy as np

class AlbumentationsWrapper(object):
    def __init__(self, albumentation):
        self.albumentation = albumentation

    def __call__(self, img):
        img = np.array(img)
        augmented = self.albumentation(image=img)
        return Image.fromarray(augmented['image'])

def get_transforms():
    train_transformation = transforms.Compose([
        transforms.RandomResizedCrop(224, interpolation=transforms.InterpolationMode.BILINEAR, antialias=True),
        transforms.RandomHorizontalFlip(0.5),
        transforms.RandomRotation(10),
        AlbumentationsWrapper(A.CoarseDropout(max_holes=1, max_height=24, max_width=24, 
                                            min_holes=1, min_height=8, min_width=8, 
                                            fill_value=1, mask_fill_value=None, 
                                            always_apply=False, p=0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])

    val_transformation = transforms.Compose([
        transforms.Resize(size=256, antialias=True),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    return train_transformation, val_transformation

def get_dataloaders(params, training_folder_name, val_folder_name, n_gpu):
    train_transformation, val_transformation = get_transforms()
    
    train_dataset = torchvision.datasets.ImageFolder(
        root=training_folder_name,
        transform=train_transformation
    )
    
    train_sampler = torch.utils.data.RandomSampler(train_dataset)
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=params.batch_size * n_gpu,  # Scale batch size by number of GPUs
        shuffle=True,
        num_workers=params.num_workers,
        pin_memory=True
    )

    val_dataset = torchvision.datasets.ImageFolder(
        root=val_folder_name,
        transform=val_transformation
    )

    val_loader = torch.utils.data.DataLoader(
        val_dataset,
        batch_size=64,
        num_workers=params.num_workers,
        shuffle=False,
        pin_memory=True
    )
    
    return train_loader, val_loader