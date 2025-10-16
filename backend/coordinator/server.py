import json, os
from pathlib import Path
from typing import List
import flwr as fl, numpy as np, torch
from flwr.common import parameters_to_ndarrays
from web3 import Web3
from backend.models.mnist_cnn import MnistCNN
from backend.security.crypto import model_update_hash

ROOT = Path(__file__).resolve().parent
ART_REG = ROOT / "ModelRegistry.json"
assert ART_REG.exists(), "Deploy contracts first (ModelRegistry.json missing)"
REG = json.loads(ART_REG.read_text())

RPC_URL = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(RPC_URL)); assert w3.is_connected(), "Cannot connect RPC"
acct = w3.eth.accounts[0]
contract = w3.eth.contract(address=REG["address"], abi=REG["abi"])

class ChainLoggingFedAvg(fl.server.strategy.FedAvg):
    def aggregate_fit(self, rnd: int, results: List, failures):
        agg_parameters, metrics = super().aggregate_fit(rnd, results, failures)
        if agg_parameters is None: return None, {}
        nds = parameters_to_ndarrays(agg_parameters)
        model = MnistCNN()
        state = model.state_dict()
        new_state = {k: np.array(v) for k, v in zip(state.keys(), nds)}
        model.load_state_dict({k: torch.tensor(v) for k,v in new_state.items()})
        h = model_update_hash(model)
        tx = contract.functions.recordUpdate(h).transact({"from": acct})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        print(f"[Round {rnd}] Aggregated hash recorded on-chain: 0x{h.hex()} tx={receipt.transactionHash.hex()}")
        (ROOT.parent / "training_log.jsonl").open("a").write(json.dumps({"round": rnd, "hash": "0x"+h.hex(), "tx": receipt.transactionHash.hex()})+"\n")
        return agg_parameters, metrics

if __name__ == "__main__":
    print("Starting Flower server on 0.0.0.0:8080 ...")
    strategy = ChainLoggingFedAvg(min_fit_clients=3, min_available_clients=3, fraction_fit=1.0)
    fl.server.start_server(server_address="0.0.0.0:8080", config=fl.server.ServerConfig(num_rounds=3), strategy=strategy)
