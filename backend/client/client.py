import argparse
import flwr as fl, torch
from torch import nn, optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from backend.models.mnist_cnn import MnistCNN

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def get_data(partition:int,total:int):
    tfm = transforms.Compose([transforms.ToTensor()])
    train = datasets.MNIST("./data", train=True, download=True, transform=tfm)
    test = datasets.MNIST("./data", train=False, download=True, transform=tfm)
    n = len(train); part_size = n//total; start = partition*part_size; end = n if partition==total-1 else (partition+1)*part_size
    return DataLoader(Subset(train, list(range(start,end))), batch_size=64, shuffle=True), DataLoader(test, batch_size=128)

def train_one_epoch(model, loader, opt, loss_fn):
    model.train(); total=0; correct=0
    for x,y in loader:
        x,y = x.to(DEVICE), y.to(DEVICE); opt.zero_grad(); out = model(x); loss = loss_fn(out,y); loss.backward(); opt.step()
        pred = out.argmax(dim=1); total += y.size(0); correct += (pred==y).sum().item()
    return correct/total

def test(model, loader):
    model.eval(); correct=0; total=0
    with torch.no_grad():
        for x,y in loader:
            x,y = x.to(DEVICE), y.to(DEVICE); out = model(x); pred = out.argmax(dim=1)
            total += y.size(0); correct += (pred==y).sum().item()
    return correct/total

class Client(fl.client.NumPyClient):
    def __init__(self, partition:int, total:int):
        self.model = MnistCNN().to(DEVICE)
        self.train_loader, self.test_loader = get_data(partition,total)
        self.loss_fn = nn.CrossEntropyLoss()
        self.opt = optim.Adam(self.model.parameters(), lr=1e-3)
    def get_parameters(self,config): return [v.detach().cpu().numpy() for v in self.model.state_dict().values()]
    def set_parameters(self,parameters):
        keys = list(self.model.state_dict().keys())
        sd = {k: torch.tensor(p) for k,p in zip(keys, parameters)}
        self.model.load_state_dict(sd, strict=True)
    def fit(self,parameters,config):
        self.set_parameters(parameters); acc = train_one_epoch(self.model,self.train_loader,self.opt,self.loss_fn)
        return self.get_parameters({}), len(self.train_loader.dataset), {"train_acc": acc}
    def evaluate(self,parameters,config):
        self.set_parameters(parameters); acc = test(self.model,self.test_loader)
        return 0.0, len(self.test_loader.dataset), {"test_acc": acc}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--partition", type=int, default=0); ap.add_argument("--total", type=int, default=3); args = ap.parse_args()
    fl.client.start_numpy_client(server_address="localhost:8080", client=Client(args.partition,args.total))
