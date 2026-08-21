import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
from .. import preliminaires

from fastapi import FastAPI
from ..generation import generer_carte

app = FastAPI()

@app.get("/nouvelle_carte")
def nouvelle_carte():
    carte = generer_carte("Ile").en_dict()
    return carte