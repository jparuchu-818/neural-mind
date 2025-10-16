'use client';
import { useEffect, useState } from 'react';
import { ethers } from 'ethers';
import { CONTRACTS, RPC } from '../lib/contract';
type EventRow = { version: string; sender: string; hash: string; reward: string };
export default function Page() {
  const [rows, setRows] = useState<EventRow[]>([]);
  const [balance, setBalance] = useState<string>("0");
  const [address, setAddress] = useState(CONTRACTS.registry.address);
  useEffect(()=>{(async()=>{
    const provider = new ethers.JsonRpcProvider(RPC);
    const reg = new ethers.Contract(address, CONTRACTS.registry.abi, provider);
    const filter = reg.filters.ModelUpdated();
    const logs = await reg.queryFilter(filter, 0, 'latest');
    const parsed = logs.map((l:any)=>{ const {version, sender, updateHash, reward} = l.args; return {version: version.toString(), sender, hash: updateHash, reward: ethers.formatUnits(reward, 18)};});
    setRows(parsed.reverse());
    const token = new ethers.Contract(CONTRACTS.token.address, CONTRACTS.token.abi, provider);
    const accts = await provider.listAccounts();
    const bal = await token.balanceOf(accts[0].address); setBalance(ethers.formatUnits(bal,18));
  })().catch(console.error);},[address]);
  return (<main className="p-6 max-w-4xl mx-auto">
    <h1 className="text-2xl font-semibold">NeuralGrid — On‑Chain Model Updates</h1>
    <p className="text-sm mt-1">GRID balance (deployer): <b>{balance}</b></p>
    <div className="mt-3 text-sm"><label>ModelRegistry Address:&nbsp;</label>
    <input className="border px-2 py-1 w-full" value={address} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAddress(e.target.value)} /></div>
    <table className="mt-4 w-full border" style={{borderCollapse:'collapse'}}>
      <thead><tr style={{background:'#f3f4f6'}}><th className="p-2 text-left">Version</th><th className="p-2 text-left">Sender</th><th className="p-2 text-left">Hash</th><th className="p-2 text-left">Reward (GRID)</th></tr></thead>
      <tbody>{rows.map((r,i)=>(<tr key={i} style={{borderTop:'1px solid #e5e7eb'}}><td className="p-2">{r.version}</td><td className="p-2">{r.sender}</td><td className="p-2 font-mono break-all">{r.hash}</td><td className="p-2">{r.reward}</td></tr>))}
      {rows.length===0 && (<tr><td className="p-4" colSpan={4}>No events yet. Start training rounds.</td></tr>)}</tbody>
    </table></main>);
}
