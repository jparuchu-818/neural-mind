// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract NodeRegistry {
    event NodeRegistered(address indexed node, string did, bytes publicKey);
    event NodeRevoked(address indexed node);
    address public owner;
    mapping(address => bool) public allowed;
    mapping(address => string) public didOf;
    mapping(address => bytes) public pubkeyOf;
    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }
    constructor() { owner = msg.sender; }
    function registerNode(address node, string memory did, bytes memory pubkey) external onlyOwner {
        allowed[node] = true; didOf[node] = did; pubkeyOf[node] = pubkey; emit NodeRegistered(node, did, pubkey);
    }
    function revokeNode(address node) external onlyOwner { allowed[node] = false; emit NodeRevoked(node); }
    function isAllowed(address node) external view returns (bool) { return allowed[node]; }
}