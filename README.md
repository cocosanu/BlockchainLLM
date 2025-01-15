# Med-Chain

Welcome to the **Med-Chain** project, a decentralized application (DApp) for managing medical records using the Ethereum blockchain, Pinata (IPFS) for decentralized storage, Web3.py for backend interactions, and a graphical interface built with CustomTkinter.

## Prerequisites

Before starting, make sure you have installed the following:

- [Python](https://www.python.org/) (version 3.6 or higher)
- [pip](https://pip.pypa.io/en/stable/) (Python package manager)
- [Remix IDE](https://remix.ethereum.org/) (to deploy and interact with smart contracts)
- An Ethereum provider (such as [Ganache](https://archive.trufflesuite.com/ganache/) for local testing)
- A Pinata account with a JWT API key (for file storage)
- [MetaMask](https://metamask.io/) (browser extension to interact with the blockchain)
 
## Installation

### 1. Clone the GitHub repository

```bash
git clone https://github.com/cocosanu/BlockchainLLM-med-chain-2.git
cd BlockchainLLM-med-chain-2
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a .env file at the root of the project with the following information:

```env
PINATA_JWT_TOKEN= Your_Pinata_JWT_Secret
```

Replace `Your_Pinata_JWT_Secret` with your JWT keys obtained from [Pinata](https://www.pinata.cloud/).

## Configuration and Deployment

### 1. Deploying Smart Contracts

1. Open [Remix IDE](https://remix.ethereum.org/).
2. Import the contract files located in the `contracts` directory of this project.
3. Compile the contracts using a compatible version of Solidity (indicated at the top of each contract file).
4. Deploy the contracts on an Ethereum network (local or public):
   - For a local network, use [Ganache](https://trufflesuite.com/ganache/).
5. Note the deployed contract address, it will be used in the backend code.

### 2. Configuring the Graphical Interface (CustomTkinter)

1. Launch the graphical application named **<<MED-CHAIN>>**:
   ```bash
   python app_.py
   ```
2. Ensure that the Pinata API keys and the deployed contract address are correctly configured in the backend Python file.

## Main Features

1. **Adding Medical Records**:
   - Users can upload medical files to Pinata (IPFS).
   - File hashes are recorded on the blockchain.

2. **Authorizing Doctors**:
   - Patients can authorize doctors to access specific records via the graphical interface.

3. **Revoking Access**:
   - Patients can revoke doctors' access to their records.

## Project Structure

```
BlockchainLLM-med-chain-2/
|— contracts/            # Solidity contracts (backend)
|— frontend/             # Code for the Med-Chain graphical interface
|— requirements.txt      # Python dependencies
|— README.md             # Documentation
```

## Deployment on a Public Network

1. **Choose a Network**:
   - Testnet (Ropsten, Goerli, etc.) or Mainnet.
2. **Add Funds**:
   - Ensure you have enough ETH to cover gas fees.
3. **Reconfigure the Backend**:
   - Update the contract address in the backend script.
4. **Launch the Application**:
   ```bash
   python app_.py
   ```

## Important Notes

- Ensure that your private keys and sensitive information are not exposed publicly.
- Test the application on a test network before any deployment on Mainnet.

For any questions or suggestions, please open an issue on the GitHub repository or contact us directly.

---
This project is licensed under the MIT License. See the LICENSE file for more information.
