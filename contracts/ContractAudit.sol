// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractPatient.sol";
import "./ContractDoctor.sol";

contract Manager {
    address public admin;

    // References to the Patient and Doctor contracts
    Patient public patientContract;
    Doctor public doctorContract;

    // Structure to record actions performed
    struct AuditLog {
        address actor;
        string action;
        uint timestamp;
    }

    // Mapping to keep track of actions performed on each medical record
    mapping(address => AuditLog[]) public patientAuditLogs;
    mapping(address => AuditLog[]) public doctorAuditLogs;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only the admin can perform this action.");
        _;
    }

    constructor(address _patientContract, address _doctorContract) {
        admin = msg.sender;
        patientContract = Patient(_patientContract);
        doctorContract = Doctor(_doctorContract);
    }

    function registerPatient(address _patientAddress, string memory _name) public onlyAdmin {
        patientContract.registerPatient(_patientAddress, _name);
        
        // Record the action in the audit
        patientAuditLogs[_patientAddress].push(AuditLog({
            actor: msg.sender,
            action: "Patient registration",
            timestamp: block.timestamp
        }));
    }

    function registerDoctor(address _doctorAddress, string memory _name) public onlyAdmin {
        doctorContract.registerDoctor(_doctorAddress, _name);

        // Record the action in the audit
        doctorAuditLogs[_doctorAddress].push(AuditLog({
            actor: msg.sender,
            action: "Doctor registration",
            timestamp: block.timestamp
        }));
    }

    // Function to get the action history of a patient
    function getPatientAuditLogs(address _patientAddress) public view returns (AuditLog[] memory) {
        return patientAuditLogs[_patientAddress];
    }

    // Function to get the action history of a doctor
    function getDoctorAuditLogs(address _doctorAddress) public view returns (AuditLog[] memory) {
        return doctorAuditLogs[_doctorAddress];
    }
}
