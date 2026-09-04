# 15. Asynchrone : asyncio, async/await

*Python de zéro à FastAPI — chapitre 15 sur 21.* ← [14. HTTP et APIs, côté client](14-http-et-apis-cote-client.md) · [Sommaire](../README.md) · [16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket](16-web-services-panorama.md) →

> 🧪 Labo associé : [`labs/15-async`](../labs/15-async/README.md)

### 15.1 Le problème : attendre

Ton script du chapitre 14 vérifie vingt sites. Chaque requête prend 500 ms, presque entièrement passées à **attendre** que le réseau réponde. Le processeur ne fait rien. Vingt requêtes à la suite : dix secondes. Cent : cinquante. Mille sites à surveiller : huit minutes pour un tour, et pendant ce temps le processeur est à 0 %.

Mesuré sur le serveur lent du labo (vingt URLs, entre 0,2 et 0,8 s chacune) :

```
séquentiel : 10.27 s
threads    : 1.67 s
asyncio    : 0.90 s
```

Ce chapitre explique les deux dernières lignes. Le mot-clé est **I/O bound** : le programme est limité par les entrées/sorties (réseau, disque, base de données), pas par le calcul. C'est le cas de presque tout ce qu'un DevOps écrit. Le cas inverse, **CPU bound** (compresser, chiffrer, calculer), se traite autrement (15.8).

### 15.2 La réponse classique : les threads

Tu connais les threads depuis le C (`pthread_create`) ou Java (`Thread`, `ExecutorService`). Python les a aussi, et pour l'I/O ils marchent très bien :

```python
import time, httpx
from concurrent.futures import ThreadPoolExecutor

URLS = [f"http://127.0.0.1:8000/site/{i}" for i in range(1, 21)]

def verifier(url: str) -> int:
    return httpx.get(url, timeout=5).status_code

debut = time.perf_counter()
with ThreadPoolExecutor(max_workers=20) as pool:
    codes = list(pool.map(verifier, URLS))        # comme map(), mais 20 en parallèle
print(f"threads : {time.perf_counter() - debut:.2f} s", codes[:3])
```

```
threads : 1.67 s [200, 200, 200]
```

`ThreadPoolExecutor` gère une réserve de threads ; `pool.map` distribue les URLs et rend les résultats dans l'ordre. Pas de `pthread_join`, pas de mutex à écrire : pour « exécuter cette fonction N fois en parallèle », c'est la bonne réponse, et elle n'oblige pas à réécrire `verifier()`.

> **Le GIL** : tu as peut-être lu que « les threads Python ne sont pas parallèles ». C'est vrai pour le calcul (chapitre 10) : un seul thread exécute du bytecode Python à la fois. Mais pendant qu'un thread **attend** le réseau, il relâche le verrou, et un autre tourne. Pour l'I/O, les threads Python sont donc parfaitement efficaces. Ce qui leur manque : ils coûtent cher (8 Mo de pile chacun par défaut, un changement de contexte par le noyau), on n'en lance pas dix mille, et partager des données entre eux demande des verrous.

### 15.3 L'autre réponse : ne pas attendre

L'idée de l'asynchrone est différente : **un seul thread**, mais qui, au lieu de bloquer sur une lecture réseau, note « préviens-moi quand ça arrive » et passe à autre chose. Une **boucle d'événements** (event loop) tient la liste de ce qui attend quoi, et réveille le bon morceau de code quand le noyau signale qu'un socket a des données.

Ce n'est pas nouveau : c'est `select()`/`poll()`/`epoll`/`kqueue` en C, Node.js depuis 2009, et le modèle de nginx. Python l'a généralisé avec `asyncio` (3.4, 2014) et la syntaxe `async`/`await` (3.5).

```python
import asyncio, time, httpx

URLS = [f"http://127.0.0.1:8000/site/{i}" for i in range(1, 21)]

async def verifier(client: httpx.AsyncClient, url: str) -> int:
    r = await client.get(url)                      # ici, on rend la main
    return r.status_code

async def principal() -> list[int]:
    async with httpx.AsyncClient(timeout=5) as client:
        return await asyncio.gather(*(verifier(client, u) for u in URLS))

debut = time.perf_counter()
codes = asyncio.run(principal())
print(f"asyncio : {time.perf_counter() - debut:.2f} s", codes[:3])
```

```
asyncio : 0.90 s [200, 200, 200]
```

0,9 s, soit le temps de la requête la plus lente (0,8 s) plus des broutilles. Les vingt requêtes sont parties en même temps, dans un seul thread. Quatre mots nouveaux : `async def`, `await`, `asyncio.run`, `gather`. Voyons-les.

### 15.4 `async def` et `await`

Une fonction déclarée `async def` est une **coroutine**. L'appeler ne l'exécute pas : ça fabrique un objet coroutine, en attente.

```python
>>> import asyncio
>>> async def salut():
...     return "bonjour"
...
>>> salut()
<coroutine object salut at 0x105c6cf60>
>>> asyncio.run(salut())
'bonjour'
```

`asyncio.run()` crée la boucle d'événements, y lance la coroutine, attend qu'elle finisse, ferme la boucle. C'est le point d'entrée, et il n'y en a qu'un par programme : ton `main()` devient `async def main()` et la dernière ligne du script devient `asyncio.run(main())`.

À l'intérieur d'une coroutine, `await x` veut dire : « lance `x`, et si `x` doit attendre quelque chose, rends la main à la boucle ; reprends-moi ici quand `x` a fini ». Le résultat de `await` est la valeur de retour de `x`. On ne peut `await` que des objets **awaitables** : une autre coroutine, une `Task`, un `Future`, ou un objet qui implémente `__await__`. Et on ne peut écrire `await` que dans une `async def`.

**Ce qu'est vraiment un `await`.** Rappelle-toi les générateurs du chapitre 11 : `yield` suspend une fonction en gardant son état, et `next()` la reprend. Une coroutine, c'est exactement ça. `await` est un `yield` qui remonte jusqu'à la boucle d'événements, en lui disant « voilà le socket que j'attends ». La boucle appelle `select()` (ou `kqueue` sur ton Mac) sur tous les sockets en attente, et quand l'un est prêt, elle fait `send()` sur la coroutine correspondante, qui repart de son `await`. Avant Python 3.5, on écrivait littéralement `yield from` à la place de `await`. La syntaxe a changé, le mécanisme non.

Conséquence importante : **une coroutine n'est jamais interrompue ailleurs qu'à un `await`**. Entre deux `await`, ton code a la boucle pour lui tout seul. Pas de verrou à prendre pour modifier un dict partagé : personne d'autre ne tourne. C'est ce qui rend l'asynchrone plus simple que les threads pour raisonner. Et c'est aussi son point faible : une coroutine qui fait un gros calcul sans jamais `await` bloque toutes les autres.

### 15.5 Lancer plusieurs choses : `gather`, `create_task`, `TaskGroup`

`await a(); await b()` exécute `a` **puis** `b` : c'est séquentiel, l'asynchrone n'apporte rien. Pour les faire tourner ensemble :

```python
import asyncio, time

async def tache(nom: str, duree: float) -> str:
    print(f"{nom} : début")
    await asyncio.sleep(duree)                     # la version async de time.sleep
    print(f"{nom} : fin après {duree} s")
    return nom.upper()

async def principal():
    debut = time.perf_counter()
    resultats = await asyncio.gather(tache("a", 1), tache("b", 0.5), tache("c", 0.7))
    print(resultats, f"en {time.perf_counter() - debut:.1f} s")

asyncio.run(principal())
```

```
a : début
b : début
c : début
b : fin après 0.5 s
c : fin après 0.7 s
a : fin après 1 s
['A', 'B', 'C'] en 1.0 s
```

`gather` lance tout, attend tout, et rend les résultats **dans l'ordre des arguments** (pas dans l'ordre d'arrivée). Si une coroutine lève une exception, `gather` la propage (et les autres continuent en arrière-plan, ce qui est un défaut historique) ; avec `return_exceptions=True`, les exceptions sont rendues dans la liste à la place des résultats, à toi de trier.

`asyncio.create_task(coro)` lance une coroutine **tout de suite** en tâche de fond et rend une `Task` qu'on peut `await` plus tard, annuler (`task.cancel()`), ou oublier. Attention à ne pas l'oublier vraiment : garde une référence, sinon le ramasse-miettes peut la tuer en plein vol.

Depuis 3.11, `asyncio.TaskGroup` est la version propre : toutes les tâches créées dedans sont attendues à la sortie du `async with`, et si l'une échoue, **les autres sont annulées** et l'erreur remonte. C'est ce qu'il faut utiliser en 2026 :

```python
async def principal():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(tache("a", 0.2))
        t2 = tg.create_task(tache("b", 0.1))
    # ici, tout est fini (ou tout a été annulé)
    print(t1.result(), t2.result())
```

### 15.6 Limiter, chronométrer, annuler

**Sémaphore.** Lancer mille requêtes d'un coup, c'est se faire bannir par le serveur ou épuiser les descripteurs de fichiers. Un `Semaphore(n)` laisse passer `n` coroutines à la fois, les autres attendent :

```python
sem = asyncio.Semaphore(5)                         # 5 requêtes simultanées maximum

async def verifier_borne(client, url):
    async with sem:                                # attend qu'une place se libère
        return await verifier(client, url)
```

C'est l'équivalent asynchrone du `max_workers=5` du pool de threads.

**Timeout.** `asyncio.timeout(s)` (3.11) est un context manager qui annule ce qu'il contient et lève `TimeoutError` :

```python
try:
    async with asyncio.timeout(0.5):
        await tache("lente", 2)
except TimeoutError:
    print("TimeoutError après 0.5 s")
```

**Annulation.** `task.cancel()` injecte une `CancelledError` au prochain `await` de la tâche. Si tu attrapes `Exception` dans une coroutine, tu n'attrapes pas `CancelledError` (elle hérite de `BaseException`, exprès), donc l'annulation marche quand même. Ne l'avale pas avec un `except BaseException`.

### 15.7 `async with`, `async for`, et les bibliothèques

Les protocoles du chapitre 11 ont leur version asynchrone : `async with` pour un context manager dont l'entrée ou la sortie attend (ouvrir/fermer une connexion), `async for` pour itérer sur une source qui attend entre deux éléments (lignes d'une réponse en flux, messages d'une file).

```python
async with httpx.AsyncClient() as client:                  # ouverture/fermeture async
    async with client.stream("GET", url) as r:             # réponse en flux
        async for ligne in r.aiter_lines():                # une ligne à la fois, sans bloquer
            traiter(ligne)
```

Ce qui compte : **une bibliothèque bloquante ne devient pas asynchrone par magie**. `requests` n'a pas de version async : dans une coroutine, `requests.get()` bloque la boucle et tout le programme avec. Il faut la version conçue pour : `httpx.AsyncClient`, `aiohttp`, `asyncpg` (PostgreSQL), `aiosqlite`, `aiofiles`. Et pour tout le reste, 15.8.

### 15.8 Les pièges, et quand ne pas faire d'async

> **Piège 1 : oublier `await`.** `enregistrer()` au lieu de `await enregistrer()` ne fait **rien**, sans erreur : ça crée un objet coroutine et le jette. Python prévient, mais en warning, souvent noyé :
> ```
> RuntimeWarning: coroutine 'enregistrer' was never awaited
> ```
> Lance tes scripts avec `python3 -W error` en développement : le warning devient une exception.

> **Piège 2 : bloquer la boucle.** `time.sleep(1)`, `requests.get()`, un `open().read()` de 2 Go, un calcul de 3 s : dans une coroutine, tout ça gèle **toutes** les autres coroutines. Le symptôme : « mon serveur async est plus lent que le synchrone ». La solution pour du code bloquant que tu ne peux pas remplacer : `await asyncio.to_thread(fonction, args)`, qui l'exécute dans un thread et rend la main pendant ce temps.
> ```python
> await asyncio.gather(asyncio.to_thread(time.sleep, 1), asyncio.to_thread(time.sleep, 1))
> # deux time.sleep(1) via to_thread : 1.0 s, pas 2
> ```

> **Piège 3 : mélanger.** Appeler `asyncio.run()` depuis une coroutine (déjà dans une boucle) plante. Appeler une coroutine depuis une fonction synchrone normale ne marche pas sans `asyncio.run()`. Le code async est **contagieux** : une fonction qui `await` doit être `async`, donc ce qui l'appelle aussi, jusqu'au `main`. Décide au début du projet.

Quand choisir quoi :

| Situation | Outil | Pourquoi |
|---|---|---|
| Quelques requêtes ou commandes, script court | rien, séquentiel | la simplicité gagne |
| Des dizaines à des centaines d'I/O, code existant bloquant | `ThreadPoolExecutor` | pas de réécriture, le GIL est relâché pendant l'I/O |
| Des milliers d'I/O, un serveur, du temps réel | `asyncio` | un thread, peu de mémoire, pas de verrous |
| Du calcul lourd (CPU bound) | `ProcessPoolExecutor` / `multiprocessing` | contourne le GIL avec plusieurs processus |
| Une API web | FastAPI (chapitre 17), qui est async par construction | un seul processus tient des milliers de connexions |

Depuis Python 3.13, un mode expérimental sans GIL (« free-threaded ») existe. Il ne change pas ce tableau pour l'instant.

### 15.9 Tester du code async

`pytest` ne sait pas exécuter une coroutine tout seul. Le plugin `pytest-asyncio` (dans le `requirements.txt`) s'en charge ; avec `asyncio_mode = auto` dans le `pytest.ini` du labo, toute fonction de test `async def` est lancée dans une boucle :

```python
async def test_verifier_ok():
    def faux_serveur(request):
        return httpx.Response(200)
    async with httpx.AsyncClient(transport=httpx.MockTransport(faux_serveur)) as client:
        assert await verifier(client, "http://x/") == 200
```

Même `MockTransport` qu'au chapitre 14 : il marche pour le client sync et le client async.

### 15.10 Ce qu'il faut retenir

- **I/O bound** (attendre le réseau, le disque) : threads ou asyncio. **CPU bound** : plusieurs processus. Un script court : rien.
- `ThreadPoolExecutor` + `pool.map` parallélise du code bloquant existant sans le réécrire.
- `async def` fabrique une coroutine, `await` rend la main à la boucle, `asyncio.run()` lance le tout. Une coroutine n'est interrompue qu'à un `await`.
- `gather` ou, mieux, `TaskGroup` pour lancer plusieurs coroutines ; `Semaphore` pour limiter ; `asyncio.timeout` pour borner.
- Ne bloque jamais la boucle : bibliothèques async (`httpx.AsyncClient`) ou `asyncio.to_thread`. `python3 -W error` attrape les `await` oubliés.

**Labo 15** : un vérificateur de disponibilité en trois versions (séquentielle, threads, asyncio avec sémaphore), chronométrées sur un serveur local lent, avec des tests `pytest-asyncio` sans réseau.

---

← [14. HTTP et APIs, côté client](14-http-et-apis-cote-client.md) · [Sommaire](../README.md) · [16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket](16-web-services-panorama.md) →
