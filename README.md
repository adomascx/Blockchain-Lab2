# Blockchain Lab v0.1

Blockchain Lab v0.1 is a centralized proof-of-work environment designed for experimenting with account-model transactions and block assembly. The project processes 10,000 generated transfers against 1,000 synthetic accounts, applies a custom PHA256 hash function, and persists the resulting chain state for review. The implementation favors clarity and traceability for instructional use while remaining faithful to core blockchain concepts.

## System Overview

- **Accounts**: `Functions/userGen.py` produces 1,000 deterministic user records with reproducible public keys derived from their index and balances sampled from the interval `[100, 1_000_000]`.
- **Transactions**: `Functions/transGen.py` generates 10,000 random transfers. Each transaction identifier hashes the sender, receiver, amount, and ordinal value to reduce the risk of collisions.
- **Blocks**: The header stores the previous hash, timestamp, version, nonce, difficulty target, and a deterministic transaction root. The body records 100 validated transactions per block.
- **Blockchain Core**: `Functions/blockchain.py` manages account state, transaction validation, proof-of-work, and persistence. Shadow balances protect intra-block consistency.
- **Hashing**: `Functions/hash.py` centralizes hashing. Proof-of-work iterates until the computed hash satisfies a three-leading-zero target.

## Running the Application

1. Execute `python main.py` from the repository root.
2. Select option `1` to generate `json/users_start.json` with 1,000 accounts.
3. Select option `2` to generate `json/transactions.json` with 10,000 transactions.
4. Select option `3` to mine blocks until the pending pool is exhausted or no valid transactions remain. Results are written to `json/blockchain.json`, and final balances are saved to `json/users_end.json`.

The mining workflow performs input validation. If user or transaction data is missing, the application reports the issue and stops the run.

## Console Snapshot

![Console mining output](docs/console-output.png)

## Repository Map

- `main.py`: Command-line interface for dataset generation and mining operations.
- `Functions/block.py`: Block data structure with deterministic transaction root hashing.
- `Functions/blockchain.py`: Core engine implementing validation, proof-of-work, state updates, and persistence.
- `Functions/userGen.py` and `Functions/transGen.py`: Data generation utilities for accounts and transactions.
- `json/*.json`: Input and output datasets, including snapshots of user balances and block history.
- `docs/console-output.png`: Example mining output.

## Additional Notes

- Difficulty level `3` balances demonstration speed with a meaningful proof-of-work exercise.
- Invalid transactions (for example, incorrect hashes, missing participants, or insufficient balances) are rejected and recorded in the chain dump for later inspection.
- The project intentionally omits decentralization and security features. It serves as a structured sandbox for understanding the mechanics of block validation.
