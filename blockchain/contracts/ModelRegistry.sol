// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
interface IGridToken { function mint(address to, uint256 amount) external; }
contract ModelRegistry {
    event ModelUpdated(uint256 indexed version, address indexed sender, bytes32 updateHash, uint256 reward);
    uint256 public version;
    mapping(uint256 => bytes32) public versionHash;
    mapping(address => uint256) public contributions;
    IGridToken public token;
    constructor(address tokenAddr) { token = IGridToken(tokenAddr); }
    function recordUpdate(bytes32 updateHash) external {
        version += 1;
        versionHash[version] = updateHash;
        contributions[msg.sender] += 1;
        uint256 reward = 1e18;
        if (address(token) != address(0)) { token.mint(msg.sender, reward); }
        emit ModelUpdated(version, msg.sender, updateHash, reward);
    }
}