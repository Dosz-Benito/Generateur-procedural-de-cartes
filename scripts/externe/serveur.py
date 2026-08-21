import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import scripts.preliminaires

from fastapi import FastAPI, Response
from ..generation import generer_carte

app = FastAPI()

@app.get("/")
def accueil():
    return Response("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mon serveur de génération</title>
</head>
<body>
    <h1>Bienvenue sur l'accueil du serveur Raydash !!!</h1>
</body>
</html>""")

@app.get("/nouvelle_carte")
def nouvelle_carte():
    carte = generer_carte("Ile")
    return carte