from fastapi import FastAPI, Response


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
