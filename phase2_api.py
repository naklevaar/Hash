import hashlib
import os
import hmac
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # We use this to define the 'POST' request data

# 1. Create the app
app = FastAPI()

# 2. A "database" for our prototype
# APIs are "stateless," meaning they forget everything after a request is done.
# We need a simple, temporary place to store the 'server_seed' after we
# create it in /get_commitment, so that /play_game can find it.
# A simple dictionary is perfect for this prototype.
#
# We will store: { "commitment_hash" : "server_seed" }
commitment_storage = {}


# --- Endpoint 1: GET a New Commitment ---

@app.get("/get_commitment")
def get_commitment():
    """
    Generates a new server_seed and commitment_hash.
    Stores the seed and returns the hash to the user.
    """
    # 1. Generate a new, secret server_seed
    server_seed = os.urandom(32).hex()
    
    # 2. Hash it to create the commitment
    commitment_hash = hashlib.sha256(server_seed.encode('utf-8')).hexdigest()
    
    # 3. Store the seed, using the hash as its "key"
    commitment_storage[commitment_hash] = server_seed
    
    # 4. Return the hash to the user. This is their "proof"
    #    that the game is locked in.
    return {"commitment_hash": commitment_hash}


# --- Endpoint 2: Play the Game ---

# 1. Define the *shape* of the data we expect from the user.
#    When a user makes a POST request, they will send us a JSON body.
#    This 'BaseModel' tells FastAPI to expect JSON that looks like:
#    { "commitment_hash": "...", "client_seed": "..." }
class PlayRequest(BaseModel):
    commitment_hash: str
    client_seed: str

@app.post("/play_game")
def play_game(request: PlayRequest):
    """
    Takes a commitment_hash and client_seed, finds the matching
    server_seed, calculates the roll, and returns the result + proof.
    """
    # 1. Get the data from the user's request
    client_seed = request.client_seed
    commitment_hash = request.commitment_hash
    
    # 2. Try to find the server_seed in our storage.
    #    .pop() is perfect: it *gets* the seed AND *deletes* it
    #    from storage. This prevents it from ever being used again!
    server_seed = commitment_storage.pop(commitment_hash, None)
    
    # 3. Check if we found it.
    if server_seed is None:
        # If not, the commitment_hash is invalid or was already used.
        # We send a 404 "Not Found" error.
        raise HTTPException(status_code=404, detail="Commitment hash not found or already used.")

    # 4. --- IT'S THE SAME LOGIC FROM YOUR STEP 2 SCRIPT! ---
    # We found the seed, so now we run the game logic.
    combined_hash_object = hmac.new(
        server_seed.encode('utf-8'),  # Key
        client_seed.encode('utf-8'),  # Message
        hashlib.sha256
    )
    combined_hash = combined_hash_object.hexdigest()

    # Turn the hash into a 0-99 roll
    hash_substring = combined_hash[:5]
    hash_as_int = int(hash_substring, 16)
    roll_result = (hash_as_int % 10001) % 100
    # --- END OF GAME LOGIC ---

    # 5. Return everything to the user.
    #    They now have all three pieces (server_seed, client_seed, roll_result)
    #    and can verify the game was fair.
    return {
        "roll_result": roll_result,
        "server_seed": server_seed,
        "client_seed": client_seed,
        "verification_hash": combined_hash
    }