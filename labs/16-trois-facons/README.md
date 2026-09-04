# Labo 16 — Le même service, de trois façons

**Chapitre** : [16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket](../../cours/16-web-services-panorama.md)

## Objectif
Exposer un même service (conversion de température + status) en REST/JSON, en XML-RPC (l'ancêtre direct de SOAP) et en JSON-RPC 2.0, avec la bibliothèque standard seulement, puis regarder les octets qui passent sur le fil pour comprendre ce qui distingue vraiment les familles.

## Consignes
1. Lis `service.py` : deux fonctions, zéro HTTP. C'est le service. Tout le reste n'est qu'une façon de l'appeler à distance. Lance `pytest -k service_pur`.
2. Complète `do_GET()` dans `rest_serveur.py` : routes `/status` et `/convert?c=20`, 400 si `c` manque ou n'est pas un nombre, 404 sinon. Lance-le (`python3 rest_serveur.py`), teste avec `curl -i "http://127.0.0.1:8001/convert?c=20"` et `curl -i http://127.0.0.1:8001/convert?c=chaud`. Puis `python3 rest_client.py`. `pytest -k rest` doit passer.
3. Complète `creer_serveur()` dans `xmlrpc_serveur.py` (trois lignes). Lance-le, puis `python3 xmlrpc_client.py`. Regarde `proxy.system.listMethods()` : le client découvre les fonctions disponibles. `pytest -k xmlrpc`.
4. Complète `traiter()` et `do_POST()` dans `jsonrpc_serveur.py`. Teste avec `curl` : `curl -s -X POST http://127.0.0.1:8003/ -d '{"jsonrpc":"2.0","method":"convertir","params":[20],"id":1}'`, puis avec une méthode inconnue. Quel code HTTP obtiens-tu dans le cas d'erreur ? Pourquoi ? `pytest` doit être tout vert.
5. Lance `python3 comparer.py` : les trois serveurs partent dans des threads et on envoie à chacun la requête « 20 °C » avec un socket brut. Compare : taille de la requête, de la réponse, où est le nom de la fonction, où sont les arguments, qui porte l'erreur (code HTTP ou enveloppe). Note tes réponses en commentaire en haut de `comparer.py`.
6. Bonus : ajoute `POST /convert` en REST (corps JSON `{"celsius": 20}`) et une méthode `batch` en JSON-RPC (la spec autorise une liste de requêtes). Bonus 2 : ajoute une quatrième façon, `xmlrpc` mais en passant par `http.client` à la main, et compte les octets d'une enveloppe SOAP équivalente (cherche « SOAP envelope example ») : combien de fois plus lourd ?

## Comment lancer
```bash
source ../../.venv/bin/activate
pytest                                   # lance chaque serveur dans un thread sur un port libre
SOLUTION=1 pytest
python3 rest_serveur.py    &  python3 rest_client.py    8001
python3 xmlrpc_serveur.py  &  python3 xmlrpc_client.py  8002
python3 jsonrpc_serveur.py &  python3 jsonrpc_client.py 8003
kill %1 %2 %3
python3 solution/comparer.py             # les trois protocoles, octets bruts
```

Extrait de `comparer.py` (solution) :
```
REST / JSON        requête  47 octets   réponse 199 octets
XML-RPC            requête 234 octets   réponse 499 octets
JSON-RPC 2.0       requête 154 octets   réponse 238 octets
```

## Pour aller plus loin
- `python3 -m http.server` et `python3 -m xmlrpc.server`... n'existe pas, mais `python3 -c "import xmlrpc.server, inspect; print(inspect.getsource(xmlrpc.server.SimpleXMLRPCDispatcher._dispatch))"` montre comment le serveur retrouve la fonction à partir du nom : un `dict`, comme ton `METHODES`.
- Le chapitre 17 refait `rest_serveur.py` avec FastAPI : validation de `c`, 422 automatique, documentation OpenAPI générée. Garde ta version stdlib sous les yeux pour mesurer ce que le framework t'apporte.
- Un vrai serveur SOAP en Python : la bibliothèque `spyne` côté serveur, `zeep` côté client. Regarde un WSDL public (par exemple celui d'un service de conversion de devises) et compare-le à `system.listMethods()`.
