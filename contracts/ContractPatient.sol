// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Patient {
    struct MedicalRecord {
        string recordHash;
        mapping(address => bool) authorizedDoctors; // Map of doctors authorized for this record
    }

    mapping(address => mapping(string => MedicalRecord)) private records; // Patient -> RecordHash -> MedicalRecord

    event AccessGranted(address indexed patientAddress, address indexed doctorAddress, string recordHash);
    event AccessRevoked(address indexed patientAddress, address indexed doctorAddress, string recordHash);

    modifier onlyPatient(address _patientAddress, address _caller) {
        require(_patientAddress == _caller, "Only the patient can perform this action.");
        _;
    }

    // Authorize a doctor for a specific medical record
    function authorizeToMedicalFolder(
        address _patientAddress,
        string memory _recordHash,
        address _doctorAddress
    ) public onlyPatient(_patientAddress, msg.sender) {
        records[_patientAddress][_recordHash].recordHash = _recordHash;
        records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress] = true;
        emit AccessGranted(_patientAddress, _doctorAddress, _recordHash);
    }

    // Function to revoke a doctor's access to a specific medical record
    function revokeFromMedicalFolder(
        address _patientAddress,
        string memory _recordHash,
        address _doctorAddress
    ) public onlyPatient(_patientAddress, msg.sender) {
        require(
            records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress],
            "The doctor does not have access to this record."
        );
        records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress] = false;
        emit AccessRevoked(_patientAddress, _doctorAddress, _recordHash);
    }

    // Check if a doctor is authorized for a specific medical record
    function isDoctorAuthorized(
        address _patientAddress,
        string memory _recordHash,
        address _doctorAddress
    ) public view returns (bool) {
        return records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress];
    }
}
