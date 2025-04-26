import torch
import torch.nn as nn
import torch.nn.functional as F

class MNISTNet(nn.Module):
    def __init__(self):
        super(MNISTNet, self).__init__()

        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 16, 3, padding=0)
        self.bnorm1 = nn.BatchNorm2d(16)
        # 28 -> 26 x 26 x 8 | RF - 3

        self.conv2 = nn.Conv2d(16, 32, 3, padding=0)
        self.bnorm2 = nn.BatchNorm2d(32)
        # 26 -> 24 x 24 x 16 | RF - 5

        self.noconv1 = nn.Conv2d(32, 16, 1)
        # 24 -> 24 x 24 x 16 | RF - 5

        self.pool1 = nn.MaxPool2d(2, 2)
        # 24 -> 12 x 12 x 16 | RF - 6

        self.conv3 = nn.Conv2d(16, 16, 3, padding=0)
        self.bnorm3 = nn.BatchNorm2d(16)
        # 12 -> 10 x 10 x 16 | RF - 10

        self.conv4 = nn.Conv2d(16, 16, 3, padding=0)
        self.bnorm4 = nn.BatchNorm2d(16)
        # 10 -> 8 x 8 x 16 | RF - 14

        self.conv5 = nn.Conv2d(16, 16, 3, padding=0)
        self.bnorm5 = nn.BatchNorm2d(16)
        # 8 -> 6 x 6 x 16 | RF - 1

        self.conv6 = nn.Conv2d(16, 16, 3, padding=0)
        self.bnorm6 = nn.BatchNorm2d(16)
        # 6 -> 4 x 4 x 32 | RF - 22

        self.drop = nn.Dropout2d(0.1)

        self.gap = nn.AvgPool2d(4)
        # 4 x 4 x 32 -> 1 x 1 x 32 | RF - 28

        self.noconv2 = nn.Conv2d(16, 10, 1)
        # 1 x 1 x 32 -> 1 x 1 x 10 | RF - 28


    def forward(self, x):
        # Convolutional layers with ReLU and pooling
        x = F.relu(self.conv1(x))
        x = self.bnorm1(x)
        x = self.drop(x)

        x = F.relu(self.conv2(x))
        x = self.bnorm2(x)
        x = self.drop(x)

        x = self.noconv1(x)

        x = self.pool1(x)

        x = F.relu(self.conv3(x))
        x = self.bnorm3(x)
        x = self.drop(x)

        x = F.relu(self.conv4(x))
        x = self.bnorm4(x)
        x = self.drop(x)

        x = F.relu(self.conv5(x))
        x = self.bnorm5(x)
        x = self.drop(x)

        x = F.relu(self.conv6(x))
        x = self.bnorm6(x)
        x = self.drop(x)

        x = self.gap(x)

        x = self.noconv2(x)

        x = x.view(-1, 10)

        # Log softmax for the output
        return F.log_softmax(x, dim=1)