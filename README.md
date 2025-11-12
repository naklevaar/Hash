# Provably Fair API 🎲  
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)  
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)  
![Host](https://img.shields.io/badge/Hosted_on-Render-blueviolet)  

A **simple, fast, and stateful** API for generating **provably fair random numbers (0–99)** for your games, built with **FastAPI** and **Python**.

This project uses a **Commit-Reveal** scheme to ensure **cryptographic fairness**.  
The server *commits* to a secret, and the player provides a seed. The combination of both seeds generates the result — which can be **independently verified**.

---

## 🚀 Live Endpoints

The full API is deployed on **Render** and ready to use.

- **Live API Docs:**  
  [https://hash-s4pd.onrender.com/docs](https://hash-s4pd.onrender.com/docs)

- **Live Verifier Page:**  
  [https://naklevaar.github.io/Hash/](https://naklevaar.github.io/Hash/)  
  

---

## 🛠️ API Quickstart

You can test the API from any terminal using `curl`.

### Step 1: Get a Commitment

First, ask the server for a **commitment hash** — this is the server’s "promise" that its secret is locked in.

```bash
curl -X 'GET' 'https://hash-s4pd.onrender.com/get_commitment'
```

**Response:**
```json
{
  "commitment_hash": "a1b2c3d4e5f6..."
}
```

---

### Step 2: Play the Game

Now, send the `commitment_hash` along with your own unique `client_seed`.

```bash
curl -X 'POST' 'https://hash-s4pd.onrender.com/play_game' \
  -H 'Content-Type: application/json' \
  -d '{
    "commitment_hash": "a1b2c3d4e5f6...",
    "client_seed": "my_super_secret_string_123"
  }'
```

**Response:**
```json
{
  "roll_result": 77,
  "server_seed": "long_secret_server_seed_that_was_hidden...",
  "client_seed": "my_super_secret_string_123",
  "verification_hash": "..."
}
```

> You now have the result **and** all the data needed to prove the roll was fair.

---

## ✅ How to Verify

**How do you know the roll (77) is legitimate?**

1. Go to the **[Verifier Page](https://naklevaar.github.io/Hash/)**
2. Paste the `server_seed` and `client_seed` from the API response
3. The page runs the **exact same cryptographic calculation** in your browser  
   → **Proving the server didn’t cheat**

---

## 💻 Technology Stack

| Layer       | Tech                                      |
|-------------|-------------------------------------------|
| **Backend** | FastAPI                                   |
| **Logic**   | Python 3.11, `hmac`, `hashlib`             |
| **Host**    | Render (Stateful Web Service)             |
| **Verifier**| HTML + JavaScript (CryptoJS), GitHub Pages |

---

*Fairness you can verify. Speed you can feel.*  
Built for games, lotteries, and trustless randomness.

## Built by : Affan Qureshi 3rd Year BCA Student
Email: affanahmadq10@gmail.com
``` 
