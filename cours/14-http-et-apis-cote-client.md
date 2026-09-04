# 14. HTTP et APIs, côté client

*Python de zéro à FastAPI — chapitre 14 sur 21.* ← [13. Ligne de commande et scripts DevOps](13-ligne-de-commande-et-devops.md) · [Sommaire](../README.md) · [15. Asynchrone : asyncio, async/await](15-async.md) →

> 🧪 Labo associé : [`labs/14-client-api`](../labs/14-client-api/README.md)

Avant d'écrire une API (chapitre 17), il faut en consommer. Un DevOps passe ses journées à parler à des APIs : GitHub, GitLab, Cloudflare, Proxmox, Grafana, un cloud quelconque. Ce chapitre commence par démystifier HTTP en le tapant à la main, puis passe aux trois bibliothèques que tu croiseras : `urllib` (dans la boîte), `requests` (l'historique) et `httpx` (le moderne, qui fait aussi de l'asynchrone).

### 14.1 HTTP, c'est du texte

HTTP est un protocole texte au-dessus de TCP. Le client ouvre une connexion, envoie une **requête** (une ligne de commande, des en-têtes, une ligne vide, éventuellement un corps), le serveur renvoie une **réponse** (une ligne de statut, des en-têtes, une ligne vide, un corps). Version 1.1, la plus lisible ; HTTP/2 et /3 sont binaires mais transportent exactement les mêmes notions.

Tu peux voir tout ça avec `curl -v` :

```
$ curl -v "https://httpbin.org/get?q=python" 2>&1 | grep -E '^[<>]'
> GET /get?q=python HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/8.7.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Date: Fri, 04 Sep 2026 11:53:11 GMT
< Content-Type: application/json
< Content-Length: 229
```

Les lignes `>` partent, les lignes `<` arrivent. Et pour être sûr qu'il n'y a pas de magie, la même chose avec un socket brut en Python, sans aucune bibliothèque HTTP :

```python
import socket, ssl

ctx = ssl.create_default_context()                     # vérifie le certificat, comme un navigateur
with socket.create_connection(("httpbin.org", 443), timeout=10) as brut:
    with ctx.wrap_socket(brut, server_hostname="httpbin.org") as s:
        s.sendall(b"GET /get?q=python HTTP/1.1\r\n"
                  b"Host: httpbin.org\r\n"
                  b"Connection: close\r\n"
                  b"\r\n")                             # ligne vide = fin des en-têtes
        reponse = b""
        while morceau := s.recv(4096):                 # lit jusqu'à la fermeture
            reponse += morceau
print(reponse.decode())
```

```
HTTP/1.1 200 OK
Date: Fri, 04 Sep 2026 11:53:11 GMT
Content-Type: application/json
Content-Length: 229
Connection: close
Server: gunicorn/19.9.0

{
  "args": {
    "q": "python"
  },
  "url": "https://httpbin.org/get?q=python"
}
```

Voilà tout HTTP : des octets, `\r\n` entre les lignes, une ligne vide entre en-têtes et corps. Tout ce qui suit, ce sont des bibliothèques qui t'évitent d'écrire ces `b"..."`.

> **Venant du C** : c'est exactement ce qu'on ferait avec `socket()`, `connect()`, `send()`, `recv()` de `<sys/socket.h>`, plus OpenSSL pour le TLS. Python enveloppe les mêmes appels système ; `socket.create_connection` fait le `getaddrinfo` + `connect` pour toi.

### 14.2 Le vocabulaire à connaître

**La méthode** dit ce qu'on veut faire de la ressource :

| Méthode | Sens | Corps ? | Idempotent ? |
|---|---|---|---|
| `GET` | lire | non | oui |
| `POST` | créer, ou « faire une action » | oui | **non** |
| `PUT` | remplacer entièrement | oui | oui |
| `PATCH` | modifier partiellement | oui | pas garanti |
| `DELETE` | supprimer | rarement | oui |
| `HEAD` | comme GET, sans le corps | non | oui |

*Idempotent* : rejouer la requête deux fois donne le même état qu'une fois. Un `DELETE` deux fois, c'est toujours supprimé. Un `POST` deux fois, c'est peut-être deux commandes passées. Ça compte pour les retries (14.7).

**Le code de statut** de la réponse, par famille :

| Famille | Sens | Ceux que tu verras |
|---|---|---|
| 2xx | ça a marché | `200 OK`, `201 Created`, `204 No Content` |
| 3xx | va voir ailleurs | `301`/`302` redirection, `304 Not Modified` |
| 4xx | **tu** as fait une erreur | `400 Bad Request`, `401 Unauthorized` (pas authentifié), `403 Forbidden` (authentifié mais pas le droit), `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity` (validation, FastAPI adore), `429 Too Many Requests` |
| 5xx | **le serveur** a fait une erreur | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout` |

**Les en-têtes** (headers) : des paires `Nom: valeur`, insensibles à la casse. Ceux qui reviennent tout le temps : `Content-Type` (le format du corps : `application/json`, `text/html`, `application/x-www-form-urlencoded`), `Content-Length`, `Authorization`, `Accept` (ce que le client sait lire), `User-Agent`, `Location` (où aller après un 201 ou un 3xx).

**Query string vs corps.** `GET /repos?per_page=5&page=2` : les paramètres sont dans l'URL, visibles, limités en taille, mis en cache, dans les logs du serveur. Un `POST` avec un corps JSON : invisible dans l'URL, taille libre, pas mis en cache. Règle : ce qui **filtre** une lecture va dans la query string, ce qui **crée ou modifie** va dans le corps.

**JSON.** Le format d'échange par défaut depuis quinze ans. `import json` : `json.loads(texte)` donne des `dict`/`list`/`str`/`int`/`float`/`bool`/`None`, `json.dumps(objet)` fait l'inverse (chapitre 7). Toutes les bibliothèques ci-dessous ont un raccourci `.json()` sur la réponse.

### 14.3 `urllib.request` : sans rien installer

Dans la bibliothèque standard. Verbeux, mais quand tu écris un script qui doit tourner sur une machine où tu ne peux pas `pip install`, c'est lui.

```python
from urllib.request import urlopen, Request
import json

req = Request("https://api.github.com/repos/stranix79/cheatsheets",
              headers={"Accept": "application/vnd.github+json"})
with urlopen(req, timeout=10) as resp:            # resp est un objet fichier
    print(resp.status, resp.headers["Content-Type"])
    data = json.load(resp)                        # lit le corps et le parse
print(data["full_name"], data["language"], data["html_url"])
```

```
200 application/json; charset=utf-8
stranix79/cheatsheets HTML https://github.com/stranix79/cheatsheets
```

Un code 4xx ou 5xx lève `urllib.error.HTTPError` tout seul. Pour un `POST`, il faut encoder le corps soi-même (`data=json.dumps(obj).encode()`) et poser le `Content-Type`. Ça marche, c'est juste pénible, d'où la suite.

### 14.4 `requests` : le client historique

`requests` (2011) a fixé l'API que tout le monde copie depuis. Il n'est pas dans la stdlib mais il est partout, y compris dans le `requirements.txt` du cours.

```python
import requests

r = requests.get("https://api.github.com/users/stranix79/repos",
                 params={"per_page": 5},           # → ?per_page=5, encodé pour toi
                 headers={"Accept": "application/vnd.github+json"},
                 timeout=10)                       # TOUJOURS, voir 14.6
print(r.status_code, r.headers["Content-Type"])
for repo in r.json():                              # la liste des dépôts, déjà parsée
    print(repo["name"], repo["language"], repo["stargazers_count"])
```

```
200 application/json; charset=utf-8
asm-m1 None 0
cheatsheets HTML 0
dyndns-cloudflare Python 0
easy-duplicity Shell 0
hsb-scripts None 0
```

L'objet `Response` a ce qu'il faut : `r.status_code`, `r.headers` (un dict insensible à la casse), `r.text` (le corps décodé), `r.content` (les octets bruts), `r.json()`, `r.url` (l'URL finale après redirections), `r.ok` (vrai si < 400).

Envoyer du JSON, c'est `json=` :

```python
r = requests.post("https://httpbin.org/post",
                  json={"host": "morningstar", "up": True},   # sérialisé + Content-Type posé
                  timeout=10)
print(r.status_code, r.json()["json"], r.json()["headers"]["Content-Type"])
```

```
200 {'host': 'morningstar', 'up': True} application/json
```

`data={...}` enverrait un formulaire (`application/x-www-form-urlencoded`), ce que veulent les vieux endpoints et le login OAuth2 du chapitre 19. `files={...}` envoie un fichier en multipart.

**`raise_for_status()`.** `requests` ne lève **pas** d'exception sur un 404 ou un 500 : `r.status_code` vaut 404 et c'est tout. Le réflexe :

```python
r = requests.get("https://httpbin.org/status/500", timeout=10)
try:
    r.raise_for_status()                          # lève HTTPError si 4xx ou 5xx
except requests.exceptions.HTTPError as e:
    print("HTTPError:", e)
```

```
HTTPError: 500 Server Error: INTERNAL SERVER ERROR for url: https://httpbin.org/status/500
```

**`Session`.** Quand tu enchaînes des requêtes vers le même serveur, une `Session` réutilise la connexion TCP/TLS (au lieu d'en rouvrir une à chaque fois, ce qui coûte trois allers-retours), garde les cookies, et te laisse poser les en-têtes une fois pour toutes :

```python
with requests.Session() as s:
    s.headers["Accept"] = "application/vnd.github+json"
    s.headers["Authorization"] = f"Bearer {token}"
    repos = s.get("https://api.github.com/user/repos", timeout=10).json()
    for repo in repos:
        s.get(repo["url"], timeout=10)            # même connexion, mêmes en-têtes
```

### 14.5 `httpx` : la même API, en plus moderne

`httpx` (2019) reprend l'API de `requests` presque à l'identique, et ajoute HTTP/2, une vraie gestion des timeouts, et surtout un **client asynchrone** (chapitre 15). C'est lui qu'utilise le `TestClient` de FastAPI. Pour un nouveau projet, c'est le choix par défaut.

```python
import httpx

r = httpx.get("https://httpbin.org/status/404", timeout=10)
print(r.status_code, r.reason_phrase)
try:
    r.raise_for_status()
except httpx.HTTPStatusError as e:
    print("HTTPStatusError:", e)
```

```
404 NOT FOUND
HTTPStatusError: Client error '404 NOT FOUND' for url 'https://httpbin.org/status/404'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
```

Différences avec `requests` à connaître : `httpx.Client()` au lieu de `Session()` ; les redirections **ne sont pas suivies** par défaut (`follow_redirects=True`) ; un timeout de 5 s est appliqué par défaut (au lieu d'aucun) ; les exceptions s'appellent `httpx.TimeoutException`, `httpx.ConnectError`, `httpx.HTTPStatusError`. Et `httpx.MockTransport` permet de tester sans réseau, ce que fait le labo.

Le reste du chapitre utilise `requests` ou `httpx` indifféremment : ce que tu apprends sur l'un vaut pour l'autre.

### 14.6 Timeouts, erreurs, et ce qui casse vraiment

> **Piège** : `requests.get(url)` sans `timeout` peut bloquer **pour toujours**. Un serveur qui accepte la connexion et ne répond jamais (un firewall qui drop, un service à moitié mort) et ton script de sauvegarde nocturne attend jusqu'à la fin des temps. Aucune exception, aucun log. Mets toujours un timeout. Toujours.

Le paramètre accepte un nombre (en secondes) ou un tuple `(connexion, lecture)`. Trois familles d'erreurs, à attraper séparément parce qu'on n'y réagit pas pareil :

```python
import requests

try:
    r = requests.get("https://httpbin.org/delay/5", timeout=1)
    r.raise_for_status()
except requests.exceptions.Timeout:
    print("trop lent : on réessaie plus tard")
except requests.exceptions.ConnectionError:
    print("DNS, refus de connexion, TLS : le serveur n'est pas joignable")
except requests.exceptions.HTTPError as e:
    print("le serveur a répondu, mais mal :", e.response.status_code)
```

```
trop lent : on réessaie plus tard
```

Toutes héritent de `requests.exceptions.RequestException` si tu veux un filet global. Chez `httpx`, la base est `httpx.HTTPError`.

**TLS.** `verify=False` désactive la vérification du certificat. Tu le verras dans des scripts d'entreprise pour parler à un Proxmox ou un switch avec un certificat auto-signé. C'est une mauvaise réponse à un vrai problème : la bonne, c'est `verify="/chemin/vers/ca-interne.pem"`, qui fait confiance à *ton* autorité et à rien d'autre.

### 14.7 Pagination, retries, rate limits

**Pagination.** Une API ne renvoie jamais 10 000 objets d'un coup. GitHub renvoie 30 par page et donne la suite dans l'en-tête `Link` :

```
Link: <https://api.github.com/user/1789515/repos?per_page=5&page=2>; rel="next",
      <https://api.github.com/user/1789515/repos?per_page=5&page=3>; rel="last"
```

La boucle canonique, avec `requests` qui parse `Link` pour toi dans `r.links` :

```python
def tous_les_depots(utilisateur: str) -> list[dict]:
    url = f"https://api.github.com/users/{utilisateur}/repos"
    params = {"per_page": 100}
    resultat = []
    while url:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        resultat.extend(r.json())
        url = r.links.get("next", {}).get("url")   # None quand il n'y a plus de page
        params = None                              # l'URL "next" contient déjà les params
    return resultat
```

D'autres APIs paginent avec `?page=2`, `?offset=100&limit=50`, ou un `cursor` opaque à renvoyer. Le principe est le même : boucler tant qu'il y a une suite.

**Retries avec backoff.** Le réseau a des hoquets. Un 503 ou un timeout à 3 h du matin ne mérite pas de réveiller quelqu'un si la deuxième tentative passe. Mais réessayer immédiatement, en boucle, sur un serveur déjà à genoux, c'est l'achever. D'où le **backoff exponentiel** : attendre 1 s, puis 2, puis 4, avec un peu de hasard pour que mille clients ne réessaient pas à la même seconde.

```python
import random, time

def get_avec_retries(url: str, essais: int = 4, **kwargs) -> requests.Response:
    for tentative in range(essais):
        try:
            r = requests.get(url, timeout=10, **kwargs)
            if r.status_code < 500 and r.status_code != 429:
                return r                            # 2xx, 3xx, 4xx : pas la peine d'insister
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            pass                                    # on retentera
        attente = 2 ** tentative + random.uniform(0, 1)
        print(f"tentative {tentative + 1} ratée, attente {attente:.1f} s")
        time.sleep(attente)
    raise RuntimeError(f"abandon après {essais} tentatives : {url}")
```

Ne réessaie que ce qui est **idempotent** (14.2) ou dont tu sais que le serveur déduplique. `urllib3.util.Retry` monté sur une `Session` fait la même chose en déclaratif ; `tenacity` est la bibliothèque dédiée.

**Rate limits.** GitHub te donne 60 requêtes par heure sans authentification, 5 000 avec. Il le dit dans les en-têtes :

```python
r = requests.get("https://api.github.com/users/stranix79/repos", timeout=10)
print(r.headers["X-RateLimit-Limit"], r.headers["X-RateLimit-Remaining"])
```

```
60 59
```

Un `429 Too Many Requests` vient souvent avec `Retry-After: 30` : le serveur te dit combien attendre. Lis-le.

### 14.8 S'authentifier

Quatre schémas couvrent 95 % des APIs :

| Schéma | Ça ressemble à | Avec `requests` |
|---|---|---|
| Basic | `Authorization: Basic base64(user:mdp)` | `auth=("user", "mdp")` |
| Bearer / token | `Authorization: Bearer eyJhbGci...` | `headers={"Authorization": f"Bearer {token}"}` |
| Clé d'API | `X-API-Key: abc123` (le nom varie) | `headers={"X-API-Key": cle}` |
| OAuth2 | un flux pour obtenir un Bearer | chapitre 19, côté serveur |

```python
r = requests.get("https://httpbin.org/basic-auth/gilles/secret",
                 auth=("gilles", "secret"), timeout=10)
print(r.status_code, r.json())
```

```
200 {'authenticated': True, 'user': 'gilles'}
```

> **Piège** : jamais de secret dans l'URL (`?api_key=...`). Les URLs finissent dans les logs du serveur, du proxy, de ton shell, de ton navigateur. Un en-tête, non. Et jamais de secret dans le code : une variable d'environnement, lue avec `os.environ["GITHUB_TOKEN"]` (chapitre 13), ou un fichier `.env` gitignoré.

### 14.9 Télécharger en flux

`r.content` charge tout le corps en mémoire. Pour une image ISO de 4 Go, non. `stream=True` lit par morceaux :

```python
from pathlib import Path

def telecharger(url: str, destination: Path) -> int:
    with requests.get(url, stream=True, timeout=(10, 60)) as r:
        r.raise_for_status()
        with destination.open("wb") as f:
            for morceau in r.iter_content(chunk_size=1024 * 1024):   # 1 Mo à la fois
                f.write(morceau)
    return destination.stat().st_size
```

Le timeout `(10, 60)` : 10 s pour se connecter, 60 s maximum *entre deux morceaux*, pas pour le total.

### 14.10 Lire la doc d'une API

Une API sérieuse publie un contrat **OpenAPI** (ex-Swagger) : un fichier JSON ou YAML qui liste chaque route, ses paramètres, ses codes de réponse, ses schémas. Souvent affiché en page interactive à `/docs` ou `/swagger`. Ce que tu y cherches, dans l'ordre : comment s'authentifier, comment ça pagine, quel `Content-Type` ça attend, et à quoi ressemble une erreur (un JSON `{"detail": "..."}` ou du HTML ?). FastAPI génère ce fichier tout seul à partir de ton code, et c'est un des chapitres 17 et 19.

Sans OpenAPI, la démarche reste la même : une requête dans le REPL, `r.headers`, `r.json()`, et on regarde ce qui revient avant d'écrire une ligne de script.

### 14.11 Ce qu'il faut retenir

- HTTP, c'est du texte : une ligne de requête, des en-têtes, une ligne vide, un corps. `curl -v` et un socket brut le montrent.
- Méthodes (`GET` lit, `POST` crée, `PUT`/`PATCH` modifient, `DELETE` supprime), codes (2xx bien, 4xx c'est toi, 5xx c'est lui), en-têtes (`Content-Type`, `Authorization`).
- `urllib` si tu ne peux rien installer, `requests` partout, `httpx` pour du neuf et de l'async.
- **Toujours un `timeout`**, toujours `raise_for_status()`, attraper `Timeout`, `ConnectionError`, `HTTPError` séparément.
- Paginer en boucle, réessayer avec backoff seulement ce qui est idempotent, lire les en-têtes de rate limit.
- Les secrets dans les en-têtes et les variables d'environnement, jamais dans l'URL ni dans le code.

**Labo 14** : un client de l'API GitHub qui liste les dépôts publics d'un utilisateur, page après page, compte les langages et affiche un tableau, avec un mode hors ligne et des tests sans réseau.

---

← [13. Ligne de commande et scripts DevOps](13-ligne-de-commande-et-devops.md) · [Sommaire](../README.md) · [15. Asynchrone : asyncio, async/await](15-async.md) →
