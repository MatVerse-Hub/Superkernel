// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ProofOfSemanticEnforcement {
    mapping(string => uint256) public metrics;
    address public owner;

    event MetricRegistered(string indexed name, uint256 value);
    event TACEEvolution(uint256 timestamp, uint256 newOmega, int256 dOmegaDt);

    constructor() {
        owner = msg.sender;
    }

    function registerMetric(string memory name, uint256 value) public {
        require(msg.sender == owner, "owner only");
        metrics[name] = value;
        emit MetricRegistered(name, value);
    }

    function registerTACE(uint256 newOmega, int256 dOmegaDt) public {
        require(msg.sender == owner, "owner only");
        metrics["TACE_Evolution"] = newOmega;
        emit TACEEvolution(block.timestamp, newOmega, dOmegaDt);
    }
}
