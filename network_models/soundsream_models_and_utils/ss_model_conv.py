import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from network_models.soundsream_models_and_utils.ss_base_model import SSBaseModel

kernelSize = 5


class SSConvModel3Sec(SSBaseModel):

    def __init__(self, xSize, ySize, num_emotions=7, eval_mode = False):
        enda = int((((xSize - np.floor(kernelSize / 2) * 2) / 2) - (np.floor(kernelSize / 2) * 2)) // 2)
        endb = int((((ySize - np.floor(kernelSize / 2) * 2) / 2) - (np.floor(kernelSize / 2) * 2)) // 2)

        super().__init__(num_emotions=num_emotions)

        self.conv1 = nn.Conv2d(1, 6, kernelSize)
        self.conv2 = nn.Conv2d(6, 16, kernelSize)

        self.linear1 = torch.nn.Linear(16 * endb * enda, 300)
        self.linear2 = torch.nn.Linear(300, 300)

        self.dropouts = torch.nn.Dropout(0.2 if not eval_mode else 0)



    def forward(self, x, return_with_dims=False, soft_max = False, eval_mode = False):
        relu = F.relu
        tanh = F.tanh
        softmax = F.softmax
        pool2d = F.max_pool2d

        x = pool2d(relu(self.conv1(x)), (2, 2))
        x = self.dropouts(x) if not eval_mode else x
        x = pool2d(relu(self.conv2(x)), (2, 2))
        x = torch.flatten(x, 1)

        x = self.linear1(x)
        x = relu(x)
        x = self.dropouts(x) if not eval_mode else x
        x = self.linear2(x)
        x = relu(x)
        return super().forward(x, return_with_dims=return_with_dims, soft_max=soft_max)


class SmallConvModel(SSBaseModel):
    kernelSize = 3
    def __init__(self, xSize, ySize, num_emotions=7, eval_mode = False):
        enda = int((((xSize - np.floor(self.kernelSize / 2) * 2) / 2) - (np.floor(self.kernelSize / 2) * 2)) // 2)
        endb = int((((ySize - np.floor(self.kernelSize / 2) * 2) / 2) - (np.floor(self.kernelSize / 2) * 2)) // 2)

        super().__init__(num_emotions=num_emotions)

        self.conv1 = nn.Conv2d(1, 6, self.kernelSize)
        self.conv2 = nn.Conv2d(6, 16, self.kernelSize)

        self.linear1 = torch.nn.Linear(16 * endb * enda, 300)
        self.linear2 = torch.nn.Linear(300, 300)

        self.dropouts = torch.nn.Dropout(0.2 if not eval_mode else 0)



    def forward(self, x, return_with_dims=False, soft_max = False, eval_mode = False):
        relu = F.relu
        tanh = F.tanh
        softmax = F.softmax
        pool2d = F.max_pool2d
       # x = torch.unsqueeze(x, dim=1)
        x = pool2d(relu(self.conv1(x)), (2, 2))
        x = self.dropouts(x) if not eval_mode else x
        x = pool2d(relu(self.conv2(x)), (2, 2))
        x = torch.flatten(x, 1)

        x = self.linear1(x)
        x = relu(x)
        x = self.dropouts(x) if not eval_mode else x
        x = self.linear2(x)
        x = relu(x)
        return super().forward(x, return_with_dims=return_with_dims, soft_max=soft_max)
