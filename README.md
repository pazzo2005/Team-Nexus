# Welcome to our project


## Project Title -Nexus

There are several ways of editing your application.

**Problem Statement**
In India and other emerging markets, verifying real human identities in Web3 ecosystems
remains a challenge. Existing solutions are either too centralized (like Aadhaar) or easily
manipulated. DAOs and decentralized apps are plagued by bots, duplicate accounts, and
governance attacks like double-voting or Sybil abuse. There is a critical need for
trustworthy, human-first identity systems — without sacrificing privacy or
self-sovereignty.
## Our Solution
BiometricNB is a biometric-gated identity vault built on top of soulbound NFTs. Instead of
relying on passwords or centralized KYC, users unlock their Web3 identity by scanning a
fingerprint or face, which generates an embedded representation stored securely in IPFS.
This embedding acts as the biometric key to decrypt user-specific identity documents (like
certificates, DAO credentials, etc.) and mint a non-transferable NFT tied to their real-world
presence.
This isn’t just minting a token — it’s turning your fingerprint into a decentralized, private
access key to your identity in Web3.
## Tech Stack
● Smart Contracts: Solidity (ERC-721 Soulbound), Foundry
● Biometric Capture: WebRTC (camera) / WebAuthn (fingerprint) / custom JS
● Storage: IPFS (biometric embeddings + encrypted documents)
● Encryption: AES-based encryption using derived biometric keys (on client-side)
● NFT Metadata Generation: Off-chain preprocessing → on-chain minting
● Frontend: React + Tailwind (Three.js for live camera feed)
● Blockchain: Ethereum (with optional Hive/Filecoin support)
● AI Integration (Planned): Local LLMs (LLaMA) to validate biometric embeddings
and classify documents
● Security: Minting locked behind biometric match + wallet signature

##  Demo
Link : https://drive.google.com/file/d/13mZcS4BG7jNWJAaa_R7Z1LvWbfKhEPuR/view?usp=drive_link
PDF : https://docs.google.com/presentation/d/1LD58Tb0sbhxl1OEC3XF-Iu5lX542hJ_v/edit?usp=drive_link&ouid=108856068259590193217&rtpof=true&sd=true

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

