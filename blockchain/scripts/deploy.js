const fs = require("fs"); const path = require("path");
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const GridToken = await hre.ethers.getContractFactory("GridToken");
  const grid = await GridToken.deploy(); await grid.waitForDeployment(); const gridAddr = await grid.getAddress();
  console.log("GridToken deployed:", gridAddr);
  const ModelRegistry = await hre.ethers.getContractFactory("ModelRegistry");
  const registry = await ModelRegistry.deploy(gridAddr); await registry.waitForDeployment(); const regAddr = await registry.getAddress();
  console.log("ModelRegistry deployed:", regAddr);
  await (await grid.transferOwnership(regAddr)).wait(); console.log("Transferred GRID ownership to ModelRegistry.");
  const NodeRegistry = await hre.ethers.getContractFactory("NodeRegistry");
  const nodeReg = await NodeRegistry.deploy(); await nodeReg.waitForDeployment(); const nodeRegAddr = await nodeReg.getAddress();
  console.log("NodeRegistry deployed:", nodeRegAddr);
  const outDir = path.join(__dirname, "..", "deployments", "local"); fs.mkdirSync(outDir, { recursive: true });
  function writeOut(name, address) {
    const abiPath = path.join(__dirname, "..", "artifacts", "contracts", `${name}.sol`, `${name}.json`);
    const abiJson = JSON.parse(fs.readFileSync(abiPath, "utf8"));
    const out = { address, abi: abiJson.abi };
    fs.writeFileSync(path.join(outDir, `${name}.json`), JSON.stringify(out, null, 2));
    const backendOut = path.join(__dirname, "..", "..", "backend", "coordinator"); fs.mkdirSync(backendOut, { recursive: true });
    fs.writeFileSync(path.join(backendOut, `${name}.json`), JSON.stringify(out, null, 2));
  }
  writeOut("GridToken", gridAddr); writeOut("ModelRegistry", regAddr); writeOut("NodeRegistry", nodeRegAddr);
  console.log("Wrote ABI+address JSONs");
}
main().catch((e)=>{console.error(e); process.exit(1);});