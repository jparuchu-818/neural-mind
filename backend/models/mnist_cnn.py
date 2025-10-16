from torch import nn

class MnistCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1,32,3,1), nn.ReLU(),
            nn.Conv2d(32,64,3,1), nn.ReLU(),
            nn.MaxPool2d(2), nn.Dropout(0.25),
            nn.Flatten(),
            nn.Linear(9216,128), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(128,10)
        )
    def forward(self,x): return self.net(x)
