import model from "../../backend/coordinator/ModelRegistry.json"; import grid from "../../backend/coordinator/GridToken.json";
export const CONTRACTS = { registry: { address: model.address as `0x${string}`, abi: model.abi }, token: { address: grid.address as `0x${string}`, abi: grid.abi } };
export const RPC = process.env.NEXT_PUBLIC_RPC || "http://127.0.0.1:8545";
