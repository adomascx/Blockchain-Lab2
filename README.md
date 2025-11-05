# Blockchain Lab v0.2

## Greita apžvalga

- **Hashas**: mūsų PHA256 (iš 1 LD). Naudojamas transakcijų, Merkle šaknims ir bloko PoW hash skaičiavimui.
- **PoW tikslas**: bloko antraštės hash turi prasidėti **mažiausiai trimis nuliais**.
- **Kasimas**: vienu metu ruošiami 5 kandidatiniai blokai ir jų `nonce` ieškoma lygiagrečiai (multiprocessing).
- **Duomenys**: 1 000 vartotojų su balansais `[100, 1_000_000]`, iki 10 000 transakcijų.
- **Bloko dydis**: iki 100 transakcijų viename bloke (priklauso nuo galimų UTXO).
- **Saugojimas**: rezultatai JSON formatu `json/` kataloge.

## Turinys

- [Blockchain Lab v0.2](#blockchain-lab-v02)
  - [Greita apžvalga](#greita-apžvalga)
  - [Turinys](#turinys)
  - [Kaip paleisti](#kaip-paleisti)
  - [Ką pamatysite konsolėje](#ką-pamatysite-konsolėje)
    - [Konsolės pavyzdys](#konsolės-pavyzdys)
  - [Kaip veikia viduje](#kaip-veikia-viduje)
    - [Blokas](#blokas)
    - [Transakcijos (UTXO)](#transakcijos-utxo)
    - [Kasimas](#kasimas)
  - [Failų žemėlapis](#failų-žemėlapis)
  - [JSON išvestis](#json-išvestis)
  - [Nustatymai](#nustatymai)
  - [DI](#di)

## Kaip paleisti

1. Paleiskite iš repo šaknies:

   ```bash
   py -3.12 main.py
   ```

2. Meniu pasirinkimai:

   - `1` – sugeneruoja `json/users_start.json` (1 000 vartotojų).
   - `2` – sugeneruoja `json/transactions.json` (10 000 transakcijų).
   - `3` – kasa blokus iki kol baseinas ištuštėja. Išvestis:

     - `json/blockchain.json` – blokų grandinė;

   - `4` – išeina iš programos.

Jei kažko trūksta (pvz., nesugeneruoti vartotojai ar transakcijos), programa tai pasakys ir sustos. `json/` katalogas sukuriamas automatiškai.

## Ką pamatysite konsolėje

- Blokų ciklą: `=== Mining Block #N ===` su eilės būsena.
- Kandidatų žinutes, pvz. `Candidate #3 found valid hash! (max_attempts: 1500)`.
- Bloko santrauką `Block mined with X valid transactions (Y rejected).`

### Konsolės pavyzdys

<img src="console-output.png" alt="Console mining output" width="600" />

## Kaip veikia viduje

### Blokas

- **Antraštė**: previous_hash, timestamp, version, nonce, difficulty, Merkle root.
  - **Merkle medis**: kiekvieno lygio hash dubliuojamas, jei parodymų skaičius nelyginis, todėl gaunama deterministinė šaknis net esant vienai operacijai.
- **Turinys**: iki 100 transakcijų (tik tos, kurios pereina paprastą UTXO patikrą).

### Transakcijos (UTXO)

Generatorius palaiko vieną UTXO rinkinį ir kiekvienam vartotojui kuria atsitiktinius pervedimus su „change“ išėjimu.

**Forma** (`json/transactions.json`):

```json
{
  "transaction_id": "...",
  "inputs": ["<spent_utxo_id>", "..."],
  "outputs": [
    {"ID": "...", "owner": "<receiver_public_key>", "amount": 2500},
    {"ID": "...", "owner": "<change_public_key>", "amount": 7500}
  ]
}
```

### Kasimas

1. Iš eilės surenkama iki 100 UTXO tranzakcijų (neleidžiami dubliuoti `inputs`).
2. Sukuriami 5 kandidatai su tomis pačiomis atrinktomis transakcijomis, bet skirtingais atsitiktiniais pradiniais `nonce` (naudojama lygiagrečiam PoW).
3. Kandidatai kasami lygiagrečiai (`multiprocessing.Pool`) iki kol vienas iš jų atitinka `difficulty` (pradinis limitas 1 000 iteracijų, po nesėkmės +500).
4. Laimėjęs (iškastas) kandidatas pridedamas prie grandinės, o išnaudotos UTXO pašalinamos iš laukiančiųjų.

## Failų žemėlapis

- `main.py` – paprastas meniu duomenų generavimui ir kasimui.
- `functions/block.py` – bloko struktūra ir Merkle šaknies skaičiavimas.
- `functions/blockchain.py` – kandidatų parinkimas, lygiagretus PoW, UTXO registras ir JSON išsaugojimas.
- `functions/userGen.py`, `functions/transGen.py` – duomenų generatoriai (`HashFunction` naudojamas raktams/UTXO ID).
- `functions/hash.py` – PHA256 realizacija.
- `json/*.json` – įvestys ir išvestys (`users_start`, `transactions`, `blockchain`).
- `console-output.png` – konsolės pavyzdys.

## JSON išvestis

- `json/users_start.json` – 1 000 vartotojų (`name`, `public_key`, `balance`).
- `json/transactions.json` – sugeneruotos transakcijos (`transactions` masyve) su UTXO I/O.
- `json/blockchain.json` – dabartinė grandinė: `difficulty`, `block_size`, blokų `header`/`transactions`/`hash`, `rejected_transactions` skaitiklis.

## Nustatymai

- **Difficulty**: `3`. Greita demonstracija, bet matomas PoW efektas.
- **Bloko dydis**: iki `100` (keičiasi `blockchain(block_size=...)`).
- **Kandidatų kiekis**: `5` (konstanta `blockchain._build_candidates`).
- **Pradiniai bandymai**: `1000` iteracijų kandidatui, po nesėkmės padidėja `+500`.
- **Naudotojų/Tx kiekiai**: `USERS_COUNT = 1000`, `TRANSACTIONS_COUNT = 10_000`.

## DI

DI buvo naudojamas kaip "konsultantas":

- Kodo stiliui (kad atitiktų šiuolaikinius standartus)
- Klaidų taisymui ("bug fixes")
- PHA256 vertimo į Python pagalbai
