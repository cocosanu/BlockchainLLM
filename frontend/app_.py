import customtkinter
from PIL import Image
from click import command
from netaddr.strategy.ipv4 import width
from web3 import Web3
import csv
import os
import ipfshttpclient
import json
import requests
from dotenv import load_dotenv
import zipfile


# Blockchain setup
GANACHE_URL = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
load_dotenv()
print(web3.eth.accounts[5])

def upload_to_pinata(medical_data):
    # Retrieve the JWT token from the environment
    PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

    # URL of the Pinata API to add data to IPFS
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    # Define the headers with the Bearer authorization token
    headers = {'Authorization': f'Bearer {PINATA_JWT_TOKEN}'}

    json_data = {"data":medical_data} # Convert to JSON to check validity
    print(f"Sending data to Pinata: {json_data}")

    # Make a POST request to send the JSON data to Pinata
    response = requests.post(url, json=json_data, headers=headers)

    # Check the response from the Pinata API
    if response.status_code == 200:
        # Extract the IPFS hash from the response
        ipfs_hash = response.json()['IpfsHash']
        print(f"The data has been successfully uploaded to IPFS. Hash: {ipfs_hash}")
        return ipfs_hash
    else:
        print(f"Error uploading to Pinata: {response.status_code}, {response.text}")
        return None


def upload_directory_to_pinata(directory_path):
    # Retrieve the JWT token from the environment
    PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

    # URL of the Pinata API to add data to IPFS
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    # Define the headers with the Bearer authorization token
    headers = {'Authorization': f'Bearer {PINATA_JWT_TOKEN}'}

    # Create a zip file from the directory
    zip_file_path = f"{directory_path}.zip"
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory_path))

    print(f"Directory compressed to: {zip_file_path}")

    # Open the zip file to send it to Pinata
    with open(zip_file_path, 'rb') as file:
        files = {'file': file}

        # Make a POST request to send the zip file to Pinata
        response = requests.post(url, files=files, headers=headers)

    # Check the response from the Pinata API
    if response.status_code == 200:
        # Extract the IPFS hash from the response
        ipfs_hash = response.json()['IpfsHash']
        print(f"The data has been successfully uploaded to IPFS. Hash: {ipfs_hash}")
        return ipfs_hash
    else:
        print(f"Error uploading to Pinata: {response.status_code}, {response.text}")
        return None


if web3.is_connected():
    print("Connected to the blockchain")
else:
    print("Connection failed")

def load_user_profiles(csv_file_path):
    user_profiles = {}

    try:
        with open(csv_file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Extract fields from the CSV
                address = row["Address"]
                role = row["Role"]
                specialization = row["Specialization"]
                name = row["Name"]

                # Convert "N/A" or empty specialization to None
                specialization = specialization if specialization != "N/A" else None

                # Populate the dictionary
                user_profiles[address] = {"role": role, "specialization": specialization, "name":name}

    except FileNotFoundError:
        print(f"File '{csv_file_path}' not found. Starting with an empty dictionary.")

    return user_profiles

# Example usage
csv_file_path = 'user_accounts.csv'
user_profiles = load_user_profiles(csv_file_path)

# Print the dictionary to verify
print(user_profiles)



class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, msg,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x100")
        self.title("Notification")
        self.label = customtkinter.CTkLabel(self, text=msg)
        self.label.pack(padx=20, pady=20)



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Med-Chain")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.selected_files = []
        self.frame1 = customtkinter.CTkFrame(master=self, width=200, height=1200)
        self.frame1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.frame2 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        self.frame2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.create_interface()

        doctor_contract_address = "0x24dA47fc46A1dAD599679Aa368D20e2284413b63"
        doctor_abi = [
        {
            "inputs": [
                {"internalType": "address", "name": "_patientContract", "type": "address"}
            ],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "address", "name": "doctorAddress", "type": "address"},
                {"indexed": False, "internalType": "string", "name": "name", "type": "string"}
            ],
            "name": "DoctorRegistered",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "address", "name": "patientAddress", "type": "address"},
                {"indexed": False, "internalType": "string", "name": "recordHash", "type": "string"},
                {"indexed": False, "internalType": "address", "name": "updatedBy", "type": "address"}
            ],
            "name": "RecordUpdated",
            "type": "event"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "_patientAddress", "type": "address"},
                {"internalType": "string", "name": "_recordHash", "type": "string"}
            ],
            "name": "addRecordForPatient",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
        self.doctor_contract = web3.eth.contract(address=doctor_contract_address,abi=doctor_abi)

        patient_contract_address = "0xf8e81D47203A594245E36C48e151709F0C19fBe8"
        patient_abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "patientAddress",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "doctorAddress",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "recordHash",
                "type": "string"
            }
        ],
        "name": "AccessGranted",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "patientAddress",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "doctorAddress",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "recordHash",
                "type": "string"
            }
        ],
        "name": "AccessRevoked",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_patientAddress",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "_recordHash",
                "type": "string"
            },
            {
                "internalType": "address",
                "name": "_doctorAddress",
                "type": "address"
            }
        ],
        "name": "authorizeToMedicalFolder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_patientAddress",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "_recordHash",
                "type": "string"
            },
            {
                "internalType": "address",
                "name": "_doctorAddress",
                "type": "address"
            }
        ],
        "name": "isDoctorAuthorized",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_patientAddress",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "_recordHash",
                "type": "string"
            },
            {
                "internalType": "address",
                "name": "_doctorAddress",
                "type": "address"
            }
        ],
        "name": "revokeFromMedicalFolder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
        self.patient_contract = web3.eth.contract(address=patient_contract_address, abi=patient_abi)

        #web3.eth.default_account = web3.eth.accounts[0]  # Default account
    def create_medical_record(self, patient_address, medical_data):
        try:
            # 1. Verify if the patient's address is valid
            if not web3.is_address(patient_address):
                self.show_message("Invalid patient address!")
                return

            # 2. Upload the medical data to IPFS
            #client = ipfshttpclient.connect()  # Connect to IPFS
            #ipfs_response = client.add_json(medical_data)  # Add the medical data (in JSON)
            #ipfs_hash = ipfs_response["Hash"]
            #client.close()
            ipfs_response = upload_to_pinata(medical_data)  # Add the medical data (in JSON)
            ipfs_hash = ipfs_response["Hash"]

            # 3. Record the hash in the blockchain via the smart contract
            doctor_address = web3.eth.default_account  # Ethereum address of the connected doctor
            doctor_contract = web3.eth.contract(
                address=self.doctor_contract_address,
                abi=self.doctor_abi
            )

            # Call the method to create a medical record
            tx = doctor_contract.functions.createMedicalRecord(
                patient_address,
                ipfs_hash
            ).transact({'from': doctor_address})
            web3.eth.wait_for_transaction_receipt(tx)

            self.show_message("Medical record created successfully!")

        except Exception as e:
            self.show_message(f"Error creating medical record: {str(e)}")

    def create_interface(self):
        # Frame 1: Image Display
        my_image = customtkinter.CTkImage(light_image=Image.open("./assets/bg1.png"), size=(500, 800))
        image_label = customtkinter.CTkLabel(self.frame1, image=my_image, text="")
        image_label.pack()

        # Frame 2: Tabs for Sign In and Sign Up
        tabview_log = customtkinter.CTkTabview(master=self.frame2, width=460, height=600)
        tabview_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tabview_log.add("Sign In")
        tabview_log.add("Sign Up")
        tabview_log.set("Sign In")

        # Sign In Tab
        self.create_sign_in_tab(tabview_log)

        # Sign Up Tab
        self.create_sign_up_tab(tabview_log)

        ########msg balance#########
        label_msg = customtkinter.CTkLabel(master=self.frame2, text="The login process is empowered by Metamask,")
        label_msg.grid(row=1, column=0, padx=10, pady=2, sticky="nsew")
        label_msg_ = customtkinter.CTkLabel(master=self.frame2,
                                            text="please verify that your wallet contain some ETH balance.",
                                            text_color="#029CFF")
        label_msg_.grid(row=2, column=0, padx=10, pady=0, sticky="nsew")

    def create_sign_in_tab(self, tabview):
        logo_w = customtkinter.CTkImage(light_image=Image.open("./assets/logooo.png"), size=(100, 80))
        logo_label = customtkinter.CTkLabel(tabview.tab("Sign In"), image=logo_w, text="")
        logo_label.pack(pady=50)

        label_up = customtkinter.CTkLabel(master=tabview.tab("Sign In"), text="Welcome to Med-Chain!", fg_color="transparent", text_color="#FFFFFF", font=("arial", 30))
        label_up.pack(pady=20)

        label_adr = customtkinter.CTkLabel(master=tabview.tab("Sign In"), text="Account Address *", fg_color="transparent", justify="left")
        label_adr.pack(padx=20, pady=(100, 5), anchor="w")
        self.entry_signin_address = customtkinter.CTkEntry(master=tabview.tab("Sign In"), placeholder_text="Ex: 0x123456...", width=400)
        self.entry_signin_address.pack(padx=20, pady=(0, 10), anchor="w")

        signin_btn = customtkinter.CTkButton(master=tabview.tab("Sign In"), corner_radius=20, width=300, text="Sign in!", command=self.sign_in)
        signin_btn.pack(padx=30, pady=20)

    def create_sign_up_tab(self, tabview):
        logo_w = customtkinter.CTkImage(light_image=Image.open("./assets/logooo.png"), size=(100, 80))
        logo_label = customtkinter.CTkLabel(tabview.tab("Sign Up"), image=logo_w, text="")
        logo_label.pack()

        label_up = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Welcome to Med-Chain!", fg_color="transparent", text_color="#FFFFFF", font=("arial", 30))
        label_up.pack(pady=20)

        # Full Name
        label_name = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Full Name *", fg_color="transparent", justify="left")
        label_name.pack(padx=20, pady=(10, 5), anchor="w")
        self.entry_signup_name = customtkinter.CTkEntry(master=tabview.tab("Sign Up"), placeholder_text="Ex: John Doe", width=400)
        self.entry_signup_name.pack(padx=20, pady=(0, 10), anchor="w")

        # Ethereum Address
        label_adr = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Account Address *", fg_color="transparent", justify="left")
        label_adr.pack(padx=20, pady=(10, 5), anchor="w")
        self.entry_signup_address = customtkinter.CTkEntry(master=tabview.tab("Sign Up"), placeholder_text="Ex: 0x123456...", width=400)
        self.entry_signup_address.pack(padx=20, pady=(0, 10), anchor="w")

        # Profile Role
        label_profil = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Patient/Doctor *", fg_color="transparent", justify="left")
        label_profil.pack(padx=20, pady=(10, 5), anchor="w")
        self.optionmenu_role = customtkinter.CTkOptionMenu(master=tabview.tab("Sign Up"), width=400, values=["Patient", "Doctor"])
        self.optionmenu_role.pack(padx=20, pady=(0, 10), anchor="w")

        # Specialization (if Doctor)
        label_spe = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Specialization", fg_color="transparent", justify="left")
        label_spe.pack(padx=20, pady=(10, 5), anchor="w")
        self.entry_signup_specialization = customtkinter.CTkEntry(master=tabview.tab("Sign Up"), placeholder_text="Ex: Cardiologist", width=400)
        self.entry_signup_specialization.pack(padx=20, pady=(0, 10), anchor="w")
        self.entry_signup_specialization.configure(state="disabled")

        # Role-dependent behavior
        def update_specialization_state(choice):
            if choice == "Patient":
                self.entry_signup_specialization.configure(state="disabled")
                self.entry_signup_specialization.delete(0, "end")
            else:
                self.entry_signup_specialization.configure(state="normal")

        self.optionmenu_role.configure(command=update_specialization_state)

        # Sign Up Button
        signup_btn = customtkinter.CTkButton(master=tabview.tab("Sign Up"), corner_radius=20, text="Create Account!", command=self.sign_up)
        signup_btn.pack(padx=30, pady=20)

    def sign_in(self):
        def check_balance(address):
            balance = web3.eth.get_balance(address)
            return web3.from_wei(balance, "ether")
        self.address = self.entry_signin_address.get()
        if web3.is_address(self.address):
            balance = check_balance(self.address)
            print(balance)
            if balance < 0.01:  # Requires a minimum of 0.01 ETH
                self.show_message("Insufficient ETH balance for authentication!")
                return

        if web3.is_address(self.address):
            profile = user_profiles.get(self.address)
            if profile:
                self.show_profile_interface(profile)
            else:
                self.show_message("Address not registered!")
        else:
            self.show_message("Invalid Ethereum address!")

    def sign_up(self):
        name = self.entry_signup_name.get()
        address = self.entry_signup_address.get()
        role = self.optionmenu_role.get()
        specialization = self.entry_signup_specialization.get() if role == "Doctor" else None

        if web3.is_address(address):
            user_profiles[address] = {"name": name, "role": role, "specialization": specialization}
            self.save_to_csv(name, address, role, specialization)
            self.show_message(f"Account created for {role}!")
        else:
            self.show_message("Invalid Ethereum address!")

    def save_to_csv(self, name, address, role, specialization):
        # Define the CSV file path
        file_path = 'user_accounts.csv'

        # Check if the file already exists to write headers only once
        file_exists = os.path.exists(file_path)

        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write header if the file does not exist
            if not file_exists:
                writer.writerow(["Name", "Address", "Role", "Specialization"])

            # Write the user data row
            writer.writerow([name, address, role, specialization if specialization else "N/A"])

    def show_profile_interface(self, profile):
        role = profile["role"]
        print(profile)
        name = profile["name"]
        specialization = profile.get("specialization", "N/A")
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        #self.geometry(f"{screen_width}x{screen_height}")
        #self.resizable(True, True)
        self.frame1.destroy()
        self.frame2.destroy()

        self.frame1 = customtkinter.CTkFrame(master=self, width=200, height=1200)
        #self.frame1.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.frame1.pack(fill="x", padx=10, pady=5)

        self.frame2 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        #self.frame2.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.frame2.pack(side="left",padx=10, fill="y", pady=5)

        self.frame3 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        #self.frame3.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.frame3.pack(side="right",padx=10, fill="both", expand=True, pady=5)


        frame_lab1 = customtkinter.CTkFrame(master=self.frame1,width=200)
        frame_lab1.pack(side="left",padx=10,pady=10)

        frame_lab2 = customtkinter.CTkFrame(master=self.frame1,width=500)
        frame_lab2.pack(side="left",padx=10,pady=10)

        label = customtkinter.CTkLabel(master=frame_lab1, text=f"Welcome, {role} {name}!", font=("Arial", 30),width=500)
        label.pack(pady=20,padx=20,side="top",fill="x")

        # Add a label to display the balance
        self.balance_label = customtkinter.CTkLabel(master=frame_lab2,width=500,height=45, text="Loading balance...", font=("Arial", 20))
        self.balance_label.pack(pady=20,padx=20,side="top",fill="x")

        # Sign out
        button_signout = customtkinter.CTkButton(master=frame_lab2,width=450,text="sign out",fg_color="red",command=self.signout)
        button_signout.pack(side="left",fill="x",padx=10,pady=5)

        # Start updating the balance as soon as the interface is loaded
        self.update_balance_label()
        if role == "Doctor":
            specialization_label = customtkinter.CTkLabel(master=frame_lab1, text=f"Specialization: {specialization}")
            specialization_label.pack(pady=10,padx=20, side="bottom",fill="x")

            frame_btn = customtkinter.CTkFrame(self.frame3,width=500)
            frame_btn.pack(padx=20,pady=5,side="top")

            # Create buttons for Create and Update Medical Folder
            create_btn = customtkinter.CTkButton(
                frame_btn,fg_color='#29453C',text_color='#45C976',
                text="Create Medical Folder",
                command=self.open_create_medical_folder_window
            )
            create_btn.pack(pady=10,padx=30,side="left")

            update_btn = customtkinter.CTkButton(
                frame_btn,fg_color='#2D3A54',text_color='#5994E2',
                text="Update Medical Folder",
                command=self.open_update_window
            )
            update_btn.pack(pady=10,padx=30,side="left")

            self.scrollable_frame = customtkinter.CTkScrollableFrame(self.frame3, height=400, width=500)
            self.scrollable_frame.pack(padx=20, pady=5,side="top")

            self.update_btn = customtkinter.CTkButton(self.frame3,text="Update list", command=self.get_medical_files_from_pinata)
            self.update_btn.pack(padx=20, pady=5,side="top")
            #self.get_medical_files_from_pinata()

            # List to display events
            self.textbox = customtkinter.CTkTextbox(self.frame2, height=200, width=400)
            self.textbox.pack(padx=20, pady=10, fill="both", expand=True)

            self.start_button = customtkinter.CTkButton(self.frame2, text="Get Transactions",
                                                        command=self.start_retrieving_transactions)
            self.start_button.pack(pady=10)

        else:
            specialization_label = customtkinter.CTkLabel(master=frame_lab1, text="Hope you feel better soon!")
            specialization_label.pack(pady=10, padx=20, side="bottom", fill="x")

            frame_btn = customtkinter.CTkFrame(self.frame3, width=500)
            frame_btn.pack(padx=20, pady=5, side="top")

            self.update_btn = customtkinter.CTkButton(frame_btn, text="Update list",
                                                      command=self.get_medical_files_from_pinata_patient)
            self.update_btn.pack(padx=10, pady=5, side="left")

            # Create buttons for Authorize and Revoke access to Medical Folder
            authorize_btn = customtkinter.CTkButton(
                frame_btn, fg_color='#29453C', text_color='#45C976',
                text="Authorize doctor",
                command=self.authorize_medical_folder_window
            )
            authorize_btn.pack(pady=5, padx=10, side="left")

            revoke_btn = customtkinter.CTkButton(
                frame_btn, fg_color='#4C3039', text_color='#E86B6C',
                text="Revoke doctor",
                command=self.revoke_medical_folder_window
            )
            revoke_btn.pack(pady=5, padx=10, side="left")

            self.scrollable_frame = customtkinter.CTkScrollableFrame(self.frame3, height=400, width=500)
            self.scrollable_frame.pack(padx=20, pady=5, side="top")

            # List to display events
            self.textbox = customtkinter.CTkTextbox(self.frame2, height=200, width=400)
            self.textbox.pack(padx=20, pady=10, fill="both", expand=True)

            self.start_button = customtkinter.CTkButton(self.frame2, text="Get Transactions",
                                                        command=self.start_retrieving_transactions)
            self.start_button.pack(pady=10)

    def get_transactions(self, address, start_block=0, end_block=None):
        """Retrieve transactions associated with an address in the blockchain."""
        if end_block is None:
            end_block = web3.eth.block_number  # Get the latest block

        address = self.address

        transactions = []

        for block_number in range(start_block, end_block + 1):
            self.update_textbox(f"Retrieving block {block_number}...\n")
            try:
                block = web3.eth.get_block(block_number, full_transactions=True)
                for tx in block['transactions']:
                    # Check if the address is the sender or recipient
                    if tx['from'] == address or tx['to'] == address:
                        transactions.append(tx)
                        message = (
                            f"From: {tx['from']}, To: {tx['to']}, Amount: {web3.from_wei(tx['value'], 'ether')} ETH, "
                            f"Block: {tx['blockNumber']}\n")
                        self.update_textbox(message)
            except Exception as e:
                self.update_textbox(f"Error retrieving block {block_number}: {str(e)}\n")

        return transactions

    def update_textbox(self, message):
        """Update the TextBox with new information."""
        self.textbox.insert('end', message)  # Insert text at the end
        self.textbox.yview('end')  # Automatically scroll to the end

    def start_retrieving_transactions(self):
        import threading
        """Start the process of retrieving transactions in a separate thread."""
        start_block = 0  # You can customize the starting block
        end_block = web3.eth.block_number
        self.textbox.insert('end', "Starting transaction retrieval...\n")

        # Start the thread
        threading.Thread(
            target=self.get_transactions,
            args=(web3.eth.accounts[0], start_block, end_block),
            daemon=True
        ).start()

    def get_medical_files_from_pinata_patient(self):
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')
        url = "https://api.pinata.cloud/data/pinList"
        headers = {
            'Authorization': f'Bearer {PINATA_JWT_TOKEN}',
        }

        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            files_data = response.json()
            files = files_data.get('rows', [])
            print("files in pinata: ", files_data)

            # Add files to the Scrollable Frame
            self.display_files_in_scrollable_frame_patient(files)
        else:
            print("Error retrieving files from Pinata.")

    def display_files_in_scrollable_frame_patient(self, files):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for file in files:
            file_name = file.get("metadata", {}).get("name", "Unknown file name")
            file_url = f"https://gateway.pinata.cloud/ipfs/{file['ipfs_pin_hash']}"
            file_cid = file.get('ipfs_pin_hash', "No CID available")
            json_MF = self.download_zip_from_ipfs(file_cid)
            print(json_MF)
            if "address" in json_MF.keys() and json_MF["address"] == self.address:

                frame = customtkinter.CTkFrame(self.scrollable_frame)
                frame.pack(side="top", pady=10)

                # Add a label for each file in the Scrollable Frame
                #label = customtkinter.CTkLabel(frame, text=file_cid, anchor="w", width=400)
                #label.pack(padx=10, pady=5,side='left')

                entry = customtkinter.CTkEntry(frame, width=300)
                entry.insert(0, file_cid)
                entry.pack(padx=5, pady=5, side='left')

                # Add a button to open the file URL
                button = customtkinter.CTkButton(frame, text="Download Folder", command=lambda url=file_url: self.open_file(url))
                button.pack(pady=5, padx=5, side='left')
            else:
                pass

    def get_medical_files_from_pinata(self):
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')
        url = "https://api.pinata.cloud/data/pinList"
        headers = {
            'Authorization': f'Bearer {PINATA_JWT_TOKEN}',
        }

        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            files_data = response.json()
            files = files_data.get('rows', [])
            print("files in pinata: ", files_data)

            # Add files to the Scrollable Frame
            self.display_files_in_scrollable_frame(files)
        else:
            print("Error retrieving files from Pinata.")

    def display_files_in_scrollable_frame(self, files):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for file in files:
            file_name = file.get("metadata", {}).get("name", "Unknown file name")
            file_url = f"https://gateway.pinata.cloud/ipfs/{file['ipfs_pin_hash']}"
            file_cid = file.get('ipfs_pin_hash', "No CID available")
            json_MF = self.download_zip_from_ipfs(file_cid)
            if "address_doctor" in json_MF.keys() and json_MF["address_doctor"] == self.address:

                # Add a label for each file in the Scrollable Frame
                label = customtkinter.CTkLabel(self.scrollable_frame, text=file_name, anchor="w", width=400)
                label.pack(padx=10, pady=5)

                # Add a button to open the file URL
                button = customtkinter.CTkButton(self.scrollable_frame, text="Download Folder", command=lambda url=file_url: self.open_file(url))
                button.pack(pady=5)
            else:
                pass

    def open_file(self, url):
        import webbrowser
        webbrowser.open(url)
        print(f"Opening file: {url}")

    def signout(self):
        self.frame1.destroy()
        self.frame2.destroy()
        self.frame3.destroy()
        self.frame1 = customtkinter.CTkFrame(master=self, width=200, height=1200)
        self.frame1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.frame2 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        self.frame2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.create_interface()

    def get_balance(self):
        balance_wei = web3.eth.get_balance(self.address)  # Balance in Wei
        balance_ether = web3.from_wei(balance_wei, 'ether')  # Convert to Ether
        return balance_ether

    # Function to update the label with the balance
    def update_balance_label(self):
        balance = self.get_balance()  # Get the current balance
        self.balance_label.configure(text=f"Balance: {balance} ETH".format())

        # Update the interface every 10 seconds
        self.frame1.after(10000, self.update_balance_label)

    def revoke_medical_folder_window(self):
        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Revoke Doctor")
        self.create_window.geometry("500x400")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window, height=300, width=500)
        scrollable_frame.pack(padx=20, pady=5)
        # Medical Information Section
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Revoke Doctor",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_CID = customtkinter.CTkLabel(scrollable_frame, text="CID folder")
        label_CID.pack(pady=5)
        entry_CID = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_CID.pack(pady=5)

        label_doc_address = customtkinter.CTkLabel(scrollable_frame, text="Revoked doctor address")
        label_doc_address.pack(pady=5)
        entry_doc_address = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_doc_address.pack(pady=5)

        label_ppk = customtkinter.CTkLabel(scrollable_frame, text="Your private key")
        label_ppk.pack(pady=5)
        entry_ppk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_ppk.pack(pady=5)

        # Submit button
        submit_button = customtkinter.CTkButton(
            self.create_window, width=400, fg_color="red",
            text="Revoke doctor",
            command=lambda: self.revoke_to_medical_folder(
                cid=entry_CID.get(),
                patient_private_key=entry_ppk.get(), address_patient=self.address,
                new_doctor_address=entry_doc_address.get(),
            )
        )
        submit_button.pack(pady=5)

    def revoke_to_medical_folder(self, cid, patient_private_key, address_patient, new_doctor_address):
        # Build the transaction
        transaction = self.patient_contract.functions.revokeFromMedicalFolder(
            address_patient, cid, new_doctor_address
        ).build_transaction({
            'from': address_patient,
            'nonce': web3.eth.get_transaction_count(address_patient),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        })

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key=patient_private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction sent successfully. Hash: {web3.to_hex(tx_hash)}")

        self.create_window.destroy()
        return web3.to_hex(tx_hash)

    def authorize_medical_folder_window(self):
        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Authorize Doctor")
        self.create_window.geometry("500x400")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window, height=300, width=500)
        scrollable_frame.pack(padx=20, pady=5)
        # Medical Information Section
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Authorize Doctor",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_CID = customtkinter.CTkLabel(scrollable_frame, text="CID folder")
        label_CID.pack(pady=5)
        entry_CID = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_CID.pack(pady=5)

        label_doc_address = customtkinter.CTkLabel(scrollable_frame, text="New Authorized doctor address")
        label_doc_address.pack(pady=5)
        entry_doc_address = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_doc_address.pack(pady=5)

        label_ppk = customtkinter.CTkLabel(scrollable_frame, text="Your private key")
        label_ppk.pack(pady=5)
        entry_ppk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_ppk.pack(pady=5)

        # Submit button
        submit_button = customtkinter.CTkButton(
            self.create_window, width=400, fg_color="#64B5A0",
            text="Authorize doctor",
            command=lambda: self.authorize_to_medical_folder(
                cid=entry_CID.get(),
                patient_private_key=entry_ppk.get(), address_patient=self.address,
                new_doctor_address=entry_doc_address.get(),
            )
        )
        submit_button.pack(pady=5)

    def authorize_to_medical_folder(self, cid, patient_private_key, address_patient, new_doctor_address):
        # Build the transaction
        transaction = self.patient_contract.functions.authorizeToMedicalFolder(
            address_patient, cid, new_doctor_address
        ).build_transaction({
            'from': address_patient,
            'nonce': web3.eth.get_transaction_count(address_patient),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        })

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key=patient_private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction sent successfully. Hash: {web3.to_hex(tx_hash)}")

        self.create_window.destroy()
        return web3.to_hex(tx_hash)

    def open_create_medical_folder_window(self):
        """Opens a new window to create a medical folder"""

        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Create Medical Folder")
        self.create_window.geometry("500x600")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window,height=500,width=500)
        scrollable_frame.pack(padx=20,pady=5)

        # Medical Information Section
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Medical Informations",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_address = customtkinter.CTkLabel(scrollable_frame, text="Patient address")
        label_address.pack(pady=5)
        entry_address = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_address.pack(pady=5)

        label_pk = customtkinter.CTkLabel(scrollable_frame, text="Your private key")
        label_pk.pack(pady=5)
        entry_pk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_pk.pack(pady=5)

        label_name = customtkinter.CTkLabel(scrollable_frame, text="Patient name")
        label_name.pack(pady=5)
        entry_name = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_name.pack(pady=5)

        label_doctor = customtkinter.CTkLabel(scrollable_frame, text="Current doctor's name")
        label_doctor.pack(pady=5)
        entry_doctor = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_doctor.pack(pady=5)

        label_phone_number = customtkinter.CTkLabel(scrollable_frame, text="Patient's phone number")
        label_phone_number.pack(pady=5)
        entry_phone_number = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_phone_number.pack(pady=5)

        # Section Medical History
        label_blood_group = customtkinter.CTkLabel(scrollable_frame, text="Blood group")
        label_blood_group.pack(pady=5)
        entry_blood_group = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_blood_group.pack(pady=5)
        
        label_history = customtkinter.CTkLabel(scrollable_frame, text="Medical history",
                                                   font=("Arial", 20, "bold"))
        label_history.pack(pady=10)

        # Section Current Medical Consultation
        label_consultation = customtkinter.CTkLabel(scrollable_frame, text="Current Medical Consultation",
                                                    font=("Arial", 20, "bold"))
        label_consultation.pack(pady=10)

        label_reason = customtkinter.CTkLabel(scrollable_frame, text="Reason for consultation")
        label_reason.pack(pady=5)
        entry_reason = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_reason.pack(pady=5)

        label_condition = customtkinter.CTkLabel(scrollable_frame, text="Patient condition")
        label_condition.pack(pady=5)
        entry_condition = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_condition.pack(pady=5)

        label_date = customtkinter.CTkLabel(scrollable_frame, text="Consultation date")
        label_date.pack(pady=5)
        entry_date = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_date.pack(pady=5)

        # Section Ongoing Treatment
        label_treatment = customtkinter.CTkLabel(scrollable_frame, text="Ongoing Treatment",
                                                 font=("Arial", 20, "bold"))
        label_treatment.pack(pady=10)

        label_medications = customtkinter.CTkLabel(scrollable_frame, text="Current medication",width=400)
        label_medications.pack(pady=5)
        entry_medications = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_medications.pack(pady=5)

        # Section Additional Documents
        label_documents = customtkinter.CTkLabel(scrollable_frame, text="Additional Documents",
                                                 font=("Arial", 20, "bold"))
        label_documents.pack(pady=10)

        select_button = customtkinter.CTkButton(scrollable_frame, text="Select documents",
                                                command=self.select_documents)
        select_button.pack(pady=5)

        self.file_listbox = customtkinter.CTkTextbox(scrollable_frame, height=100,width=400)
        self.file_listbox.pack(pady=5)

        # Submit button
        submit_button = customtkinter.CTkButton(
            self.create_window,width=400,fg_color="#64B5A0",
            text="Create Medical Folder",
            command=lambda: self.submit_medical_folder(
                address=entry_address.get(),
                doctor_private_key=entry_pk.get(),address_doctor=self.address,
                name=entry_name.get(),
                doctor=entry_doctor.get(),
                blood_group=entry_blood_group.get().strip(),
                phone_number=entry_phone_number.get().strip(),
                reason=entry_reason.get("1.0", "end").strip(),
                condition=entry_condition.get("1.0", "end").strip(),
                date=entry_date.get(),
                medications=entry_medications.get("1.0", "end").strip()
            )
        )
        submit_button.pack(pady=5)

    def submit_medical_folder(self, **kwargs):
        # Display collected data
        print("Collected data for the medical folder:", kwargs)

        patient_address = kwargs.get('address')

        # Retrieve the doctor's private key
        doctor_private_key = kwargs.get('doctor_private_key')
        # Convert other data to JSON (without the private key)
        kwargs_without_private_key = {key: value for key, value in kwargs.items() if key != 'doctor_private_key'}
        json_data = json.dumps(kwargs_without_private_key, indent=4, ensure_ascii=False)
        print(json_data)
        # Create a JSON file (without the private key)
        json_file_path = "medical_folder.json"
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)

        print("\nGenerated JSON file:\n", json_data)

        # Add selected files to a temporary folder
        temp_dir = self.create_temp_directory(self.file_listbox.get("1.0", "end-1c").splitlines(), json_file_path)

        # Send the temporary folder to Pinata and get the hash
        ipfs_hash = upload_directory_to_pinata(temp_dir)

        # Close the medical folder creation window
        self.create_window.destroy()

        # Display the IPFS hash in the console
        print(f"The medical folder was successfully uploaded to IPFS. Hash: {ipfs_hash}")

        # Add the IPFS hash to the blockchain
        self.add_record_to_blockchain(doctor_private_key,patient_address, ipfs_hash)

        message = "Medical folder created Successfully!!"
        self.show_message(message)

    def add_record_to_blockchain(self,doctor_private_key, patient_address, ipfs_hash):

        # Create the transaction to call addRecordForPatient
        transaction = self.doctor_contract.functions.addRecordForPatient(
            patient_address, ipfs_hash
        ).build_transaction({
            'gas': 2000000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': web3.eth.get_transaction_count(self.address),
        })

        #return transaction

        # Sign the transaction with the private key
        signed_transaction = web3.eth.account.sign_transaction(transaction, doctor_private_key)

        print(signed_transaction)

        # Send the transaction and get the transaction hash
        #transaction_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        transaction_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)

        print(f"Transaction sent: {transaction_hash.hex()}")

        # Wait for the transaction confirmation
        receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
        if receipt['status'] == 1:
            print("The medical folder was successfully recorded on the blockchain.")
        else:
            print("Error recording the medical folder on the blockchain.")

    def create_temp_directory(self, file_paths, json_file_path):
        import tempfile
        import shutil
        """Creates a temporary folder containing the files and the JSON file."""
        temp_dir = tempfile.mkdtemp()  # Creates a temporary folder

        # Copy each selected file to the temporary folder
        for file_path in file_paths:
            if os.path.exists(file_path):  # Check if the file exists
                shutil.copy(file_path, temp_dir)
            else:
                print(f"The file {file_path} does not exist.")

        # Copy the JSON file to the temporary folder
        shutil.copy(json_file_path, temp_dir)

        print(f"Temporary folder created at: {temp_dir}")
        return temp_dir

    def create_zip_from_directory(self, directory_path):
        """Creates a ZIP file from a folder."""
        zip_file_path = f"{directory_path}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, directory_path))

        print(f"The folder was compressed into: {zip_file_path}")
        return zip_file_path

    def select_documents(self):
        from tkinter import filedialog
        # Open the file selection dialog
        file_paths = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("All files", "*.*"), ("PDF files", "*.pdf"), ("Image files", "*.jpg *.png *.jpeg")]
        )

        if file_paths:
            self.selected_files.extend(file_paths)  # Add selected files to the list

            # Display file names in the list
            self.file_listbox.delete("1.0", "end")  # Clear the previous list
            for file in self.selected_files:
                self.file_listbox.insert("end", f"{file}\n")

#######################################################################################################################

    def open_update_window(self):
        """Opens a new window to update an existing medical folder."""
        self.update_window = customtkinter.CTkToplevel(self)
        self.update_window.title("Update Medical Folder")
        self.update_window.geometry("500x200")

        label_cid = customtkinter.CTkLabel(self.update_window, text="CID of your folder")
        label_cid.pack(pady=10)
        entry_cid = customtkinter.CTkEntry(self.update_window, width=400)
        entry_cid.pack(pady=10)

        submit_cid_button = customtkinter.CTkButton(self.update_window, text="Upload Folder",
                                          command=lambda: self.load_existing_folder(entry_cid.get()))
        submit_cid_button.pack(pady=10)

    def load_existing_folder(self, cid):
        """Loads the existing medical folder from IPFS using the CID."""
        # Download the ZIP file from IPFS
        json_MF = self.download_zip_from_ipfs(cid)

        print(json_MF)

        # Extract information from the ZIP and pre-fill the form
        self.extract_and_fill_form(json_MF)

        # Display a submit button to validate the changes
        #submit_button = customtkinter.CTkButton(self.update_window, text="Update folder",
        #                              command=lambda: self.submit_update(folder_path))
        #submit_button.pack(pady=10)

    def download_zip_from_ipfs(self, cid):
        import io
        """Downloads and extracts the ZIP file from IPFS via the Pinata gateway in memory."""

        # URL to access the ZIP file on IPFS
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"

        # Make the request to get the ZIP file
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            print(f"ZIP file successfully downloaded from IPFS.")

            # Load the ZIP file into memory using BytesIO
            zip_data = io.BytesIO(response.content)

            # Extract the contents of the ZIP from memory
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                # List of files in the ZIP
                zip_file_list = zip_ref.namelist()

                # Dictionary to store extracted JSON files in memory
                extracted_json = None

                # Extract each file into the dictionary
                for file_name in zip_file_list:
                    if file_name.endswith('.json'):  # Check if it's a JSON file
                        with zip_ref.open(file_name) as file:
                            file_content = file.read()

                            # Load the JSON content and return it
                            try:
                                extracted_json = json.loads(file_content)
                                print(f"JSON file {file_name} successfully loaded.")
                            except json.JSONDecodeError:
                                print(f"Error decoding JSON file: {file_name}")

            # Check if a JSON file was extracted, otherwise return None
            if extracted_json is not None:
                return extracted_json
            else:
                print("No JSON file found in the archive.")
                return None
        else:
            print(f"Error downloading {url}. Status: {response.status_code}")
            return None

    def extract_and_fill_form(self, medical_data_json):
        """Extract and fill the form with the medical folder data."""

        # Load the JSON data (assuming 'medical_data_json' is already a dict or loaded json)
        if isinstance(medical_data_json, str):
            # If it's a string, load it as JSON
            medical_data = json.loads(medical_data_json)
        else:
            medical_data = medical_data_json

        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Update Medical Folder")
        self.create_window.geometry("500x600")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window, height=500, width=500)
        scrollable_frame.pack(padx=20, pady=5)
        # Medical Information Section
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Medical Information",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_address = customtkinter.CTkLabel(scrollable_frame, text="Patient address")
        label_address.pack(pady=5)
        entry_address = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_address.pack(pady=5)

        label_pk = customtkinter.CTkLabel(scrollable_frame, text="Your private key")
        label_pk.pack(pady=5)
        entry_pk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_pk.pack(pady=5)

        label_name = customtkinter.CTkLabel(scrollable_frame, text="Patient name")
        label_name.pack(pady=5)
        entry_name = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_name.insert(0, medical_data.get('patient_name', ''))
        entry_name.pack(pady=5)

        label_doctor = customtkinter.CTkLabel(scrollable_frame, text="Current doctor's name")
        label_doctor.pack(pady=5)
        entry_doctor = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_doctor.pack(pady=5)

        # Medical History Section
        label_history = customtkinter.CTkLabel(scrollable_frame, text="Medical History",
                                                   font=("Arial", 20, "bold"))
        label_history.pack(pady=10)

        label_blood_group = customtkinter.CTkLabel(scrollable_frame, text="Blood group")
        label_blood_group.pack(pady=5)
        entry_blood_group = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_blood_group.pack(pady=5)

        label_phone_number = customtkinter.CTkLabel(scrollable_frame, text="Phone number")
        label_phone_number.pack(pady=5)
        entry_phone_number = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_phone_number.pack(pady=5)

        # Section Current Medical Consultation
        label_consultation = customtkinter.CTkLabel(scrollable_frame, text="Current Medical Consultation",
                                                    font=("Arial", 20, "bold"))
        label_consultation.pack(pady=10)

        label_reason = customtkinter.CTkLabel(scrollable_frame, text="Reason for consultation")
        label_reason.pack(pady=5)
        entry_reason = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_reason.pack(pady=5)

        label_condition = customtkinter.CTkLabel(scrollable_frame, text="Patient condition")
        label_condition.pack(pady=5)
        entry_condition = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_condition.pack(pady=5)

        label_date = customtkinter.CTkLabel(scrollable_frame, text="Consultation date")
        label_date.pack(pady=5)
        entry_date = customtkinter.CTkEntry(scrollable_frame,width=400)
        entry_date.pack(pady=5)

        # Section Ongoing Treatment
        label_treatment = customtkinter.CTkLabel(scrollable_frame, text="Ongoing Treatment",
                                                 font=("Arial", 20, "bold"))
        label_treatment.pack(pady=10)

        label_medications = customtkinter.CTkLabel(scrollable_frame, text="Current medication",width=400)
        label_medications.pack(pady=5)
        entry_medications = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
        entry_medications.pack(pady=5)

        # Section Additional Documents
        label_documents = customtkinter.CTkLabel(scrollable_frame, text="Additional Documents",
                                                 font=("Arial", 20, "bold"))
        label_documents.pack(pady=10)

        select_button = customtkinter.CTkButton(scrollable_frame, text="Select documents",
                                                command=self.select_documents)
        select_button.pack(pady=5)

        self.file_listbox = customtkinter.CTkTextbox(scrollable_frame, height=100,width=400)
        self.file_listbox.pack(pady=5)

        # Fill the form fields with the medical folder data

        entry_address.insert(0, medical_data.get('address', ''))
        #entry_pk.insert(0, medical_data.get('doctor_private_key', ''))
        entry_name.insert(0, medical_data.get('name', ''))
        entry_doctor.insert(0, medical_data.get('doctor', ''))

        # Medical history
        entry_blood_group.insert("1.0", medical_data.get('blood_group', ''))
        entry_phone_number.insert("1.0", medical_data.get('phone_number', ''))

        # Current medical consultation
        entry_reason.insert("1.0", medical_data.get('reason', ''))
        entry_condition.insert("1.0", medical_data.get('condition', ''))
        entry_date.insert(0, medical_data.get('date', ''))

        # Ongoing treatment
        entry_medications.insert("1.0", medical_data.get('medications', ''))

        # Additional documents
        # If documents have been added to the JSON folder, display them in the list
        if 'documents' in medical_data:
            for doc in medical_data['documents']:
                self.file_listbox.insert("end", doc)

        # Submit button
        submit_button = customtkinter.CTkButton(
                self.create_window, width=400, fg_color="#64B5A0",
                    text="Create Medical Folder",
                    command=lambda: self.submit_medical_folder(
                        address=entry_address.get(),
                        doctor_private_key=entry_pk.get(),address_doctor=self.address,
                        name=entry_name.get(),
                        doctor=entry_doctor.get(),
                        blood_group=entry_blood_group.get("1.0", "end").strip(),
                        phone_number=entry_phone_number.get("1.0", "end").strip(),
                        reason=entry_reason.get("1.0", "end").strip(),
                        condition=entry_condition.get("1.0", "end").strip(),
                        date=entry_date.get(),
                        medications=entry_medications.get("1.0", "end").strip()
                    )
                )
        submit_button.pack(pady=5)
        self.update_window.destroy()
        print("Form filled successfully.")

    def submit_update(self, folder_path):
        """Submit the changes and create a new updated ZIP file."""
        new_zip_path = self.create_zip_from_folder(folder_path)

        # Upload the new ZIP file to Pinata
        new_cid = upload_directory_to_pinata(new_zip_path)

        # Delete the old ZIP file from Pinata
        self.delete_old_file_from_pinata(folder_path)

        # Update the blockchain with the new CID
        #self.update_blockchain(new_cid)

    def delete_old_file_from_pinata(self, cid):
        """Delete the old file on Pinata with a JWT token."""
        url = f"https://api.pinata.cloud/pinning/unpin/{cid}"

        # Retrieve the JWT token from the environment
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

        # Define the headers with the Bearer authorization token
        headers = {
            'Authorization': f'Bearer {PINATA_JWT_TOKEN}'
        }

        # Make the DELETE request to remove the old file
        response = requests.request("DELETE", url, headers=headers)

        # Check the response
        if response.status_code == 200:
            print("Old file successfully deleted from Pinata.")
        else:
            print(f"Error deleting the old file: {response.status_code}, {response.text}")

    def create_zip_from_folder(self, folder_path, zip_file_path="updated_medical_folder.zip"):
        """Create a ZIP file from a folder containing modified files."""
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        return zip_file_path

    def show_message(self, message):
        # Ensure self.toplevel_window is initialized
        if not hasattr(self,
                       'toplevel_window') or self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # Create a new instance of ToplevelWindow and pass the message
            self.toplevel_window = ToplevelWindow(msg=message)
        else:
            # If the window exists, bring it to the front
            self.toplevel_window.focus()

if __name__ == "__main__":
    app = App()
    app.mainloop()
