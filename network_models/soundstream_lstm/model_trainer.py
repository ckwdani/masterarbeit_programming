import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from network_models.w2v_emotion_model.custom_collator import DataCollatorCTCWithPadding


class ModelTrainer():
    def __init__(
            self,
            model: nn.Module,
            data_collator: DataCollatorCTCWithPadding,
            train_dataset: Dataset,
            eval_dataset: Dataset,
            device: str,
            num_epochs: int,
            batch_size: int,
            lr=3e-4,
            save_model_every=1000,
            loss_fn=nn.CrossEntropyLoss(),
            need_reshape = True,
            model_path = "content/customModel"

    ):
        self.data_collator = data_collator
        self.model_path = model_path
        self.model = model
        self.train_dataset = train_dataset
        self.test_dataset = eval_dataset
        self.device = device
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.lr = lr
        self.save_model_every = save_model_every
        self.loss_fn = loss_fn
        self.need_reshape = need_reshape



    def colate_fn(self, batch):
        return self.data_collator.collate_fn(batch)


    def train(self):
        train_dataloader = DataLoader(self.train_dataset, shuffle=True, batch_size=self.batch_size, num_workers=2 ,collate_fn=self.colate_fn)
        test_dataloader = DataLoader(self.test_dataset, batch_size=self.batch_size, shuffle=False, num_workers=2)
        optimizer = torch.optim.SGD(self.model.parameters(), lr=self.lr, momentum=.9)


        for t in range(self.num_epochs):
            if(t % self.save_model_every == 0):
                torch.save(self.model.state_dict(), self.model_path + f"emo_reco_{t}.pth")
            print(f"Epoch {t + 1}\n-------------------------------")
            self.train_loop(train_dataloader, self.model, self.loss_fn, optimizer)
            self.test_loop(test_dataloader, self.model, self.loss_fn)





    def train_loop(self, dataloader, model, loss_fn, optimizer):
        size = len(dataloader.dataset)
        for batch, (X, y, z) in enumerate(dataloader):
            if(self.need_reshape):
                X = X.reshape(-1, 512 * 400).to("cuda")
            else:
                X = X.to(self.device)
            # Compute prediction and loss
            z = z.to("cuda")
            y = y.to("cuda")
            pred = model(X, attention_mask=y, labels=z)

            loss = loss_fn(pred, z)

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 100 == 0:
                loss, current = loss.item(), batch * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


    def test_loop(self, dataloader, model, loss_fn):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        test_loss, correct = 0, 0

        with torch.no_grad():
            for X, y in dataloader:
                if (self.need_reshape):
                    X = X.reshape(-1, 512 * 400).to("cuda")
                else:
                    X = X.to(self.device)
                y = y.to("cuda")
                pred = model(X)

                test_loss += loss_fn(pred, y.to("cuda")).item()
                y = torch.tensor([a.nonzero() for a in y]).to("cuda")
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        test_loss /= num_batches
        correct /= size
        print(f"Test Error: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")