import hashlib
import os
import hmac
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# The simple dictionary that just works!
commitment_storage = {}

@app.get("/get_commitment")
def get_commitment():
    server_seed = os.urandom(32).hex()
    commitment_hash = hashlib.sha256(server_seed.encode('utf-8')).hexdigest()
    
    # Store it in the simple dictionary
    commitment_storage[commitment_hash] = server_seed
    
    return {"commitment_hash": commitment_hash}

class PlayRequest(BaseModel):
    commitment_hash: str
    client_seed: str

@app.post("/play_game")
def play_game(request: PlayRequest):
    client_seed = request.client_seed
    commitment_hash = request.commitment_hash
    
    # Get it from the dictionary
    server_seed = commitment_storage.pop(commitment_hash, None)
    
    if server_seed is None:
        raise HTTPException(status_code=404, detail="Commitment hash not found or already used.")

    # --- Same game logic ---
    combined_hash_object = hmac.new(
        server_seed.encode('utf-8'),
        client_seed.encode('utf-8'),
        hashlib.sha256
    )
    combined_hash = combined_hash_object.hexdigest()
    hash_substring = combined_hash[:5]
    hash_as_int = int(hash_substring, 16)
    roll_result = (hash_as_int % 10001) % 100
    # --- End of game logic ---

    return {
        "roll_result": roll_result,
        "server_seed": server_seed,
        "client_seed": client_seed,
        "verification_hash": combined_hash
    }