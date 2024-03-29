from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import torch.nn.functional as F
import torch
from torch import nn
from torch.nn import BCEWithLogitsLoss
from torchvision.transforms import Lambda
from transformers import Wav2Vec2PreTrainedModel, Wav2Vec2Model, Wav2Vec2Config
from transformers.utils import ModelOutput

@dataclass
class ClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None

class W2V_EmotionClassifierSevenEmos(nn.Module):

    def __init__(self, num_emotions = 7):
        super().__init__()
        self.linear1 = torch.nn.Linear(in_features=768, out_features=300)
        self.activation = torch.nn.LeakyReLU()
        self.activationT = nn.Tanh()
        self.dropouts = torch.nn.Dropout(0.2)
        self.linear2 = torch.nn.Linear(300, 100)
        self.linear3 = torch.nn.Linear(100, 4)
        self.linear4 = torch.nn.Linear(4, 4)
        self.linear5 = torch.nn.Linear(4, num_emotions)
        #pass dimension (along axis 0)
        self.softmax = torch.nn.Softmax(dim=0)

        self.initialize_weights()

    def forward(self, x, return_with_dims = False, soft_max = False, eval_mode = False):
        relu = F.relu
        tanh = torch.tanh
        softmax = F.softmax

        x = self.linear1(x)
        x = relu(x)
        x = self.dropouts(x) if eval_mode else x
        x = self.linear2(x)
        x = relu(x)
        x = self.linear3(x)
        y = tanh(x)
        y = self.linear4(y)
        y = relu(x)
        y = self.linear5(y)

        # y = tanh(y)

        y = softmax(y) if soft_max else y

        if return_with_dims:
            return y, x
        else:
            return y


    def initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight)
                nn.init.constant_(m.bias,0)

                if m.bias is not None:
                    nn.init.constant_(m.bias,0)



class Wav2Vec2ForSpeechClassification(Wav2Vec2PreTrainedModel):
    def __init__(self, model_name_or_path, pooling_mode, device, dataset_generator = False, from_full_dataset = False, num_emotions = 7):
        assert not (dataset_generator and from_full_dataset)
        self.from_full_dataset = from_full_dataset
        self.dataset_generator = dataset_generator
        config = Wav2Vec2Config(name_or_path=model_name_or_path)
        super().__init__(config)
        self.deviceE = device
        self.pooling_mode = pooling_mode

        if not from_full_dataset:
            self.wav2vec2 = Wav2Vec2Model(config).to(device)
        self.classifier = (W2V_EmotionClassifierSevenEmos(num_emotions=num_emotions)).to(device)

        #self.init_weights()

    def freeze_feature_extractor(self):
        self.wav2vec2.feature_extractor._freeze_parameters()

    def forward(
            self,
            input_values,
            return_with_dims=False, soft_max=False, eval_mode = False
    ):

        if self.from_full_dataset:
            hidden_states = input_values

        else:
            outputs = self.wav2vec2(
                input_values,
            )
            hidden_states = torch.mean(outputs[0], dim=1)

        if self.dataset_generator:
            return hidden_states

        logits = self.classifier(hidden_states, return_with_dims= return_with_dims, soft_max = soft_max, eval_mode=eval_mode)

        return logits


    def merged_strategy(
            self,
            hidden_states,
            mode="mean"
    ):
        if mode == "mean":
            outputs = torch.mean(hidden_states, dim=1)
        elif mode == "sum":
            outputs = torch.sum(hidden_states, dim=1)
        elif mode == "max":
            outputs = torch.max(hidden_states, dim=1)[0]
        else:
            raise Exception(
                "The pooling method hasn't been defined! Your pooling mode must be one of these ['mean', 'sum', 'max']")

        return outputs


