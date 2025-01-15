// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractPatient.sol";

contract Doctor {
    struct DoctorData {
        address doctorAddress;
        string name;
        bool isRegistered;
    }

    mapping(address => DoctorData) public doctors; // List of registered doctors
    Patient public patientContract; // Reference to the Patient contract

    // Events
    event DoctorRegistered(address indexed doctorAddress, string name);
    event RecordUpdated(
        address indexed patientAddress,
        string recordHash,
        address updatedBy,
        uint256 timestamp
    );

    // Modifier: checks if the caller is a registered doctor
    modifier onlyRegisteredDoctor() {
        require(doctors[msg.sender].isRegistered, "You must be a registered doctor.");
        _;
    }

    // Constructor: initializes the Patient contract
    constructor(address _patientContract) {
        require(_patientContract != address(0), "Invalid Patient contract address.");
        patientContract = Patient(_patientContract);
    }

    // Function to register a doctor
    function registerDoctor(address _doctorAddress, string memory _name) public {
        require(_doctorAddress != address(0), "Invalid doctor address.");
        require(!doctors[_doctorAddress].isRegistered, "Doctor already registered.");

        doctors[_doctorAddress] = DoctorData({
            doctorAddress: _doctorAddress,
            name: _name,
            isRegistered: true
        });

        emit DoctorRegistered(_doctorAddress, _name);
    }

    // Function to add a medical record to a patient
    function addRecordForPatient(address _patientAddress, string memory _recordHash)
    public
    onlyRegisteredDoctor
{
    require(_patientAddress != address(0), "Invalid patient address.");
    require(bytes(_recordHash).length > 0, "Invalid medical record hash.");

    // Check if the doctor is authorized for this patient
    require(
        patientContract.isDoctorAuthorized(_patientAddress, _recordHash, msg.sender), 
        "Unauthorized access for this patient."
    );

    // Call the addMedicalRecord function with a single argument (the record hash)
    // patientContract.addMedicalRecord(_recordHash);

    // Emit an event to signal the addition of the medical record
    emit RecordUpdated(_patientAddress, _recordHash, msg.sender, block.timestamp);
}

}
