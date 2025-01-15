import json
from web3 import Web3
import customtkinter as ctk


class PatientInterface:
    def __init__(self, contract_address, abi_path, provider_url):
        """Initialize the interface and connect to the contract."""
        self.web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

        if not self.web3.isConnected():
            raise Exception("Failed to connect to the Web3 provider.")

        with open(abi_path, 'r') as file:
            self.contract_abi = json.load(file)

        self.contract = self.web3.eth.contract(address=Web3.to_checksum_address(contract_address),
                                               abi=self.contract_abi)
        self.account = None  # Connected wallet address

        # Initialize the CustomTkinter interface
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Patient Management")
        self.build_interface()

    def connect_wallet(self, address, private_key):
        """Connect an Ethereum wallet to sign transactions."""
        self.account = address
        self.web3.eth.default_account = address
        self.private_key = private_key

    def build_interface(self):
        """Create the user interface."""
        self.label_title = ctk.CTkLabel(self.root, text="Blockchain Patient Management", font=("Arial", 20))
        self.label_title.pack(pady=10)

        # Patient registration fields
        self.entry_patient_address = ctk.CTkEntry(self.root, placeholder_text="Patient address")
        self.entry_patient_address.pack(pady=5)

        self.entry_patient_name = ctk.CTkEntry(self.root, placeholder_text="Patient name")
        self.entry_patient_name.pack(pady=5)

        self.btn_register_patient = ctk.CTkButton(self.root, text="Register Patient",
                                                  command=self.register_patient)
        self.btn_register_patient.pack(pady=10)

        # Doctor access management
        self.entry_doctor_address = ctk.CTkEntry(self.root, placeholder_text="Doctor address")
        self.entry_doctor_address.pack(pady=5)

        self.btn_grant_access = ctk.CTkButton(self.root, text="Grant Access", command=self.grant_access)
        self.btn_grant_access.pack(pady=5)

        self.btn_revoke_access = ctk.CTkButton(self.root, text="Revoke Access", command=self.revoke_access)
        self.btn_revoke_access.pack(pady=5)

        # Add medical record
        self.entry_record_hash = ctk.CTkEntry(self.root, placeholder_text="Medical record hash")
        self.entry_record_hash.pack(pady=5)

        self.btn_add_record = ctk.CTkButton(self.root, text="Add Medical Record",
                                            command=self.add_medical_record)
        self.btn_add_record.pack(pady=10)

        # View records
        self.btn_view_records = ctk.CTkButton(self.root, text="View Records", command=self.view_records)
        self.btn_view_records.pack(pady=10)

    def register_patient(self):
        """Register a new patient in the contract."""
        patient_address = self.entry_patient_address.get()
        patient_name = self.entry_patient_name.get()

        try:
            tx = self.contract.functions.registerPatient(patient_address, patient_name).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Patient successfully registered. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Error registering patient:", e)

    def grant_access(self):
        """Grant access to a doctor."""
        doctor_address = self.entry_doctor_address.get()
        try:
            tx = self.contract.functions.grantAccess(doctor_address).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Access successfully granted. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Error granting access:", e)

    def revoke_access(self):
        """Revoke access from a doctor."""
        doctor_address = self.entry_doctor_address.get()
        try:
            tx = self.contract.functions.revokeAccess(doctor_address).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Access successfully revoked. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Error revoking access:", e)

    def add_medical_record(self):
        """Add a medical record to the connected patient."""
        record_hash = self.entry_record_hash.get()
        try:
            tx = self.contract.functions.addMedicalRecord(record_hash).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Medical record successfully added. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Error adding medical record:", e)

    def view_records(self):
        """Display the patient's medical records."""
        try:
            records = self.contract.functions.getRecords(self.account).call()
            print("Medical records:", records)
        except Exception as e:
            print("Error retrieving records:", e)

    def run(self):
        self.root.mainloop()
