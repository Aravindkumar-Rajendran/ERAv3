import torch
import torch.nn as nn
import torch.nn.functional as F


class MNISTNet(nn.Module):
    def __init__(self):
        super(MNISTNet, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=1, out_channels=8, kernel_size=(3, 3), padding=0, bias=False)
        self.bnorm1 = nn.BatchNorm2d(8)
        # 28 -> 26 x 26 x 8 | RF - 3

        self.conv2 = nn.Conv2d(in_channels=8, out_channels=10, kernel_size=(3, 3), padding=0, bias=False)
        self.bnorm2 = nn.BatchNorm2d(10)
        # 26 -> 24 x 24 x 10 | RF - 5

        self.conv3 = nn.Conv2d(in_channels=10, out_channels=16, kernel_size=(3, 3), padding=0, bias=False)  
        self.bnorm3 = nn.BatchNorm2d(16)
        # 24 -> 22 x 22 x 16 | RF - 7

        self.pool1 = nn.MaxPool2d(2, 2)
        # 22 -> 11 x 11 x 16 | RF - 8

        self.noconv1 = nn.Conv2d(in_channels=16, out_channels=10, kernel_size=(1, 1), padding=0, bias=False)
        # 11 -> 11 x 11 x 10 | RF - 8

        self.conv4 = nn.Conv2d(in_channels=10, out_channels=10, kernel_size=(3, 3), padding=0, bias=False)
        self.bnorm4 = nn.BatchNorm2d(10)
        # 11 -> 9 x 9 x 10 | RF - 12

        self.conv5 = nn.Conv2d(in_channels=10, out_channels=10, kernel_size=(3, 3), padding=0, bias=False)
        self.bnorm5 = nn.BatchNorm2d(10)
        # 9 -> 7 x 7 x 10 | RF - 16

        self.conv6 = nn.Conv2d(in_channels=10, out_channels=12, kernel_size=(3, 3), padding=0, bias=False)
        self.bnorm6 = nn.BatchNorm2d(12)
        # 7 -> 5 x 5 x 12 | RF - 20

        self.conv7 = nn.Conv2d(in_channels=12, out_channels=16, kernel_size=(3, 3), padding=0, bias=False)
        self.bnorm7 = nn.BatchNorm2d(16)
        # 5 -> 3 x 3 x 16 | RF - 24

        # OUTPUT BLOCK
        self.gap = nn.AvgPool2d(kernel_size=3)
        # 3 x 3 x 16 -> 1 x 1 x 16 | RF - 28

        self.conv8 = nn.Conv2d(in_channels=16, out_channels=10, kernel_size=(1, 1), padding=0, bias=False)

        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.bnorm1(x)

        x = F.relu(self.conv2(x))
        x = self.bnorm2(x)

        x = F.relu(self.conv3(x))
        x = self.bnorm3(x)

        x = self.dropout(x)
        x = self.pool1(x)

        x = self.noconv1(x)

        x = F.relu(self.conv4(x))
        x = self.bnorm4(x)       

        x = F.relu(self.conv5(x))
        x = self.bnorm5(x)       

        x = F.relu(self.conv6(x))
        x = self.bnorm6(x)        

        x = F.relu(self.conv7(x))
        x = self.bnorm7(x)

        x = self.dropout(x)
        x = self.gap(x)
        x = self.conv8(x)
        x = x.view(-1, 10)
        return F.log_softmax(x, dim=-1)