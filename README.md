# Blockchain Lab v0.1

This thing is a centralized, proof-of-work playground that chews through 10k fake account-model transactions and spits out mined blocks with a three-zero difficulty target using the custom PHA256 hash from task 1. It is unapologetically practical: everything is OOP, the chain is persisted, and the console keeps you in the loop while mining grinds away.

## Design Notes

- **Accounts**: 1,000 deterministic users (`Functions/userGen.py`) with reproducible public keys hashed from their index and balances in `[100, 1_000_000]`.
- **Transactions**: 10,000 random transfers (`Functions/transGen.py`), transaction IDs = hash of sender, receiver, amount, and ordinal to squash collisions.
- **Blocks**: Header packs previous hash, timestamp, version, deterministic Merkle surrogate (joined tx ids), nonce, and difficulty. Body is just the 100 executed tx dicts.
- **Blockchain Core**: `Functions/blockchain.py` owns user state, pending pool, PoW, validation, and persistence. Shadow balances during assembly guarantee intra-block consistency.
- **Hashing**: Everything critical routes through `Functions/hash.py`; PoW literally hammers that implementation until the hash starts with `000`.

## Running It

1. `python main.py` inside the repo (or smash the VS Code run button if you must).
2. Option `1` writes `json/users_start.json` with 1,000 accounts.
3. Option `2` spits out `json/transactions.json` with 10,000 transactions.
4. Option `3` mines until the pool is empty or every remaining tx is garbage--blocks land in `json/blockchain.json`, balances roll into `json/users_end.json`.

If you somehow manage to skip steps 1 or 2, the miner will yell at you and bail fast.

## Console Snapshot

![Console mining output](docs/console-output.png)

## File Map

- `main.py`: brutalist CLI, nothing fancy, just orchestrates generation and mining.
- `Functions/block.py`: block structure with deterministic transaction-root hashing.
- `Functions/blockchain.py`: the real engine; transaction validation, PoW, commits, and persistence live here.
- `Functions/userGen.py` / `Functions/transGen.py`: data generation utilities tuned for this lab.
- `json/*.json`: user snapshots, transaction pool, mined chain dump.
- `docs/console-output.png`: minimal proof that the thing runs; swap it out with a real screenshot if you care about aesthetics.

## Reality Check

- Difficulty `3` keeps the demo tolerable while still testing the PoW loop.
- Invalid transactions (bad hash, missing user, or broke sender) get roasted and removed; they are listed in the chain dump for forensic kicks.
- Nothing here is decentralized or secure--by design. It is a controlled sandbox to prove you understand the moving parts.
