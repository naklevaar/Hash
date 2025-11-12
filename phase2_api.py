import hashlib
import os
import hmac
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from upstash_redis import Redis  # Import the Upstash library

# This line automatically finds the 'UPSTASH_REDIS_...' keys
# that Vercel added for you.
redis = Redis.from_env()

app = FastAPI()

# --- Endpoint 1: GET a New Commitment ---

@app.get("/get_commitment")
async def get_commitment():
    """
    Generates a new server_seed and commitment_hash.
    Stores the seed in Upstash Redis and returns the hash.
    """
    server_seed = os.urandom(32).hex()
    commitment_hash = hashlib.sha256(server_seed.encode('utf-8')).hexdigest()
    
    # 'await redis.setex(...)' stores the key in your new database
    # for 1 hour (3600 seconds).
    await redis.setex(commitment_hash, 3600, server_seed)
    
    return {"commitment_hash": commitment_hash}

# --- Endpoint 2: Play the Game ---

class PlayRequest(BaseModel):
    commitment_hash: str
    client_seed: str

@app.post("/play_game")
async def play_game(request: PlayRequest):
    """
    Takes a commitment_hash and client_seed, finds the matching
    server_seed in Upstash Redis, calculates the roll, and returns proof.
    """
    client_seed = request.client_seed
    commitment_hash = request.commitment_hash
    
    # 'await redis.getdel(...)' finds the key, gets the value,
    # and deletes it all in one step.
    server_seed_bytes = await redis.getdel(commitment_hash)
    
    if server_seed_bytes is None:
        raise HTTPException(status_code=404, detail="Commitment hash not found or already used.")
    
    # Data from this library comes back as 'bytes', so we .decode() it
    server_seed = server_seed_bytes.decode('utf-8')

    # 4. Same game logic as before
    combined_hash_object = hmac.new(
        server_seed.encode('utf-8'),
        client_seed.encode('utf-8'),
        hashlib.sha256
    )
    combined_hash = combined_hash_object.hexdigest()

    hash_substring = combined_hash[:5]
    hash_as_int = int(hash_substring, 16)
    roll_result = (hash_as_int % 10001) % 100

    return {
        "roll_result": roll_result,
        "server_seed": server_seed,
        "client_seed": client_seed,
        "verification_hash": combined_hash
    }