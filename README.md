# Blockchain Lab v0.1

## Greita apžvalga

* **Hashas**: mūsų PHA256 (iš 1 LD). Naudojamas ir transakcijų/šaknies skaičiavimui, ir PoW.
* **PoW tikslas**: bloko antraštės hash turi prasidėti **mažiausiai trimis nuliais**.
* **Duomenys**: 1 000 vartotojų su balansais `[100, 1_000_000]`, 10 000 transakcijų.
* **Bloko dydis**: ~100 patikrintų transakcijų viename bloke.
* **Saugojimas**: rezultatai JSON formatu `json/` kataloge.

## Turinys

- [Blockchain Lab v0.1](#blockchain-lab-v01)
  - [Greita apžvalga](#greita-apžvalga)
  - [Turinys](#turinys)
  - [Kaip paleisti](#kaip-paleisti)
  - [Ką pamatysite konsolėje](#ką-pamatysite-konsolėje)
    - [Konsolės pavyzdys](#konsolės-pavyzdys)
  - [Kaip veikia viduje](#kaip-veikia-viduje)
    - [Blokas](#blokas)
    - [Transakcijos (UTXO)](#transakcijos-utxo)
    - [Taisyklės](#taisyklės)
    - [Kasimas](#kasimas)
  - [Failų žemėlapis](#failų-žemėlapis)
  - [JSON išvestis](#json-išvestis)
  - [Nustatymai](#nustatymai)

## Kaip paleisti

1. Paleiskite iš repo šaknies:

   ```bash
   python main.py
   ```

2. Meniu pasirinkimai:

   * `1` – sugeneruoja `json/users_start.json` (1 000 vartotojų).
   * `2` – sugeneruoja `json/transactions.json` (10 000 transakcijų).
   * `3` – kasa blokus iki kol baseinas ištuštėja. Išvestis:

     * `json/blockchain.json` – blokų grandinė;
     * `json/users_end.json` – galutiniai balansai.

   * `4` – išeina iš programos.

Jei kažko trūksta (pvz., nesugeneruoti vartotojai ar transakcijos), programa tai pasakys ir sustos.

## Ką pamatysite konsolėje

* Transakcijų rinkimo ir validavimo žingsnius (atmestos transakcijos su priežastimi).
* Kasančio nonco paiešką (kas 5 000 iteracijų – tarpinius pranešimus).
* Rasto bloko suvestinę: antraštę, transakcijų skaičių, hash, bendrą grandinės ilgį.

### Konsolės pavyzdys

<img src="console-output.png" alt="Console mining output" width="600" />

## Kaip veikia viduje

### Blokas

* **Antraštė**: previous_hash, timestamp, version, nonce, difficulty, tx_root.
* **Turinys**: 100 validžių transakcijų.

### Transakcijos (UTXO)

Generatorius kuria UTXO tipo pervedimus ir palaiko laikiną UTXO rinkinį, kad nuorodos būtų į *nesunaudotus* išėjimus. Mineris šiuos duomenis interpretuoja paskyrų lygmeniu, todėl tikrina tik siuntėjo ir gavėjo balansus.

**Forma** (`json/transactions.json`):

```json
{
  "transaction_id": "...",
  "inputs": ["<consumed_utxo_id>", "..."],
  "outputs": [
    {"UTXO_id": "...", "owner": "<receiver_public_key>", "amount": 2500},
    {"UTXO_id": "...", "owner": "<change_public_key>", "amount": 7500}
  ]
}
```

### Taisyklės

* Siuntėjas ir gavėjas turi egzistuoti vartotojų sąraše.
* Suma turi būti teigiama ir neviršyti siuntėjo balanso (naudojama „šešėlinė“ balansų kopija bloko rinkimo metu).
* `transaction_id` turi sutapti su `Hash(sender|receiver|amount)` (yra išlyga suderinamumui su ankstesniu formatu).

### Kasimas

1. Iš baseino paimame ~100 valid transakcijų.
2. Skaičiuojame antraštės hash su skirtingais `nonce` iki kol gauname `000...` pradžią.
3. Patvirtinus bloką:

    * transakcijas pašaliname iš baseino;
    * atnaujiname vartotojų balansus;
    * bloką pridedame prie `json/blockchain.json`.

## Failų žemėlapis

* `main.py` – paprastas meniu trijoms užduotims.
* `functions/block.py` – bloko struktūra ir šaknies skaičiavimas.
* `functions/blockchain.py` – validavimas, PoW, būsena, atmestų transakcijų registras, išsaugojimas.
* `functions/userGen.py`, `functions/transGen.py` – duomenų generatoriai.
* `functions/hash.py` – centralizuotas PHA256 kvietimas.
* `json/*.json` – įvestys ir išvestys.
* `console-output.png` – konsolės pavyzdys.

## JSON išvestis

* `json/blockchain.json` – metaduomenys (`difficulty`, `block_size`), kiekvieno bloko `header`/`transactions`/`hash`, bei sąrašas `rejected_transactions` su priežastimis.
* `json/users_end.json` – galutiniai vartotojų balansai (`users` masyvas).
* `json/transactions.json` – pradinės transakcijos (`transactions` masyvas). Miner’io metu jos perskirstomos į blokus arba atmetamos.

## Nustatymai

* **Difficulty**: `3`. Greita demonstracija, bet matomas PoW efektas.
* **Bloko dydis**: `~100` transakcijų. Keiskite, jei norite pamatyti kitą dinamiką.
