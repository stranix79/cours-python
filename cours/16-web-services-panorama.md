# 16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket

*Python de zéro à FastAPI — chapitre 16 sur 21.* ← [15. Asynchrone : asyncio, async/await](15-async.md) · [Sommaire](../README.md) · [17. FastAPI : premiers pas](17-fastapi-premiers-pas.md) →

> 🧪 Labo associé : [`labs/16-trois-facons`](../labs/16-trois-facons/README.md)

Ce chapitre ne contient presque pas de Python. C'est un chapitre de culture : d'où viennent les web services, pourquoi il y en a cinq familles, ce qu'elles ont en commun, et laquelle choisir. Après ça, FastAPI (chapitre 17) ne sera pas « un framework de plus » mais la réponse actuelle à une question vieille de trente ans.

### 16.1 Un web service, c'est quoi

Un **site web** sert du HTML à un humain devant un navigateur. Un **web service** sert des **données** à un **programme**, via HTTP. Même protocole, même port 443, mais le client n'est pas une personne : c'est ton script Python, une application mobile, un autre serveur.

Dit autrement : un web service, c'est un programme qui expose des **fonctions appelables à distance**. `convertir(20)` tourne sur une machine, et une autre machine peut l'appeler et récupérer le résultat. Toute la question, depuis trente ans, c'est *comment* on encode l'appel et la réponse sur le fil. Les réponses ont changé avec les modes et les besoins ; c'est ça, les « familles ».

Trois mots qu'on confond :

- **API** (Application Programming Interface) : le contrat, la liste des fonctions et de leurs paramètres. Une bibliothèque a une API ; `requests.get(url, timeout=)` est une API. Quand on dit « l'API GitHub », on parle d'un web service, par raccourci.
- **Web service** : une API accessible par le réseau, via HTTP.
- **Microservice** : une façon de découper une application en plusieurs petits web services indépendants (un pour les utilisateurs, un pour la facturation…), chacun déployé et mis à l'échelle séparément. Une architecture, pas un protocole.

### 16.2 Un peu d'histoire, parce que ça explique tout

**1993, CGI.** Le serveur web lance un programme (souvent Perl, ou du C) à chaque requête, lui passe la query string dans des variables d'environnement, et renvoie ce que le programme écrit sur sa sortie standard. Primitif, mais c'est le premier « programme derrière une URL ». `python3 -m http.server --cgi` le fait encore.

**1998, XML-RPC.** Dave Winer veut appeler une fonction sur une autre machine. Sa recette : un `POST` sur une URL unique, le nom de la fonction et les arguments emballés en XML, la réponse aussi. Tu l'as vu dans le labo :

```xml
<methodCall>
  <methodName>convertir</methodName>
  <params><param><value><int>20</int></value></param></params>
</methodCall>
```

C'est simple, ça marche encore (WordPress, la stdlib Python), et c'est le point de départ de tout ce qui suit.

**1999-2005, SOAP.** Microsoft et IBM prennent XML-RPC et le font grossir jusqu'à couvrir tous les besoins d'une grande entreprise : types complexes, sécurité (WS-Security), transactions, routage, fiabilité (WS-ReliableMessaging)… la famille **WS-\***. Le contrat est décrit dans un fichier **WSDL** (Web Services Description Language), lui-même en XML, à partir duquel un outil génère le code client (« stub ») dans ton langage. Une requête ressemble à :

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <wsse:Security>…un jeton signé, 40 lignes…</wsse:Security>
  </soap:Header>
  <soap:Body>
    <m:Convertir xmlns:m="http://exemple.be/temperature">
      <m:Celsius>20</m:Celsius>
    </m:Convertir>
  </soap:Body>
</soap:Envelope>
```

Verbeux, lourd à parser, pénible à déboguer à la main, et le WSDL rend tout changement d'interface cérémonieux. Mais typé, contractuel, outillé, et toujours en production dans les banques, les assurances, les administrations, la SNCB, et chez beaucoup de partenaires B2B. Un DevOps en Belgique en croisera. Côté Python : `zeep` (client), `spyne` (serveur).

> **Venant de Java** : c'est le monde de JAX-WS, d'Axis, et des `wsimport` qui généraient trois cents classes. C'est exactement ce contre quoi REST a été une réaction.

**2000, REST.** Roy Fielding, un des auteurs de HTTP/1.1, décrit dans sa thèse le style d'architecture qui a fait marcher le web, et le nomme REST (*Representational State Transfer*). L'idée : arrêter d'inventer un protocole d'appel de fonction par-dessus HTTP, et **utiliser HTTP tel qu'il est**.

- Tout est une **ressource**, identifiée par une **URI** : `/depots/42`, `/utilisateurs/gilles/depots`.
- Les **méthodes HTTP** sont les verbes : `GET` lit, `POST` crée, `PUT`/`PATCH` modifie, `DELETE` supprime. Pas de `<methodName>` : l'action est dans la méthode, la cible dans l'URL.
- Le serveur renvoie une **représentation** de la ressource (aujourd'hui JSON, hier XML, demain autre chose), et les **codes de statut** portent le résultat : 200, 201, 404, 422, 500.
- **Sans état** : chaque requête contient tout ce qu'il faut (dont l'authentification). Pas de session côté serveur, donc n'importe quel serveur d'une ferme peut répondre.
- **Cacheable** : un `GET` peut être mis en cache par un proxy sans rien savoir de l'application.
- **HATEOAS** : la réponse contient les liens vers les actions possibles (comme l'en-tête `Link` de GitHub). C'est le principe le moins appliqué ; presque personne ne le fait complètement, et ce n'est pas grave.

En pratique, ce que 95 % des gens appellent « une API REST » est du **HTTP + JSON avec des URLs raisonnables**. Les puristes disent que ce n'est pas du REST « au sens de Fielding ». Ils ont raison, et ça n'a aucune importance : c'est le standard de fait depuis 2010, parce que c'est simple, lisible avec `curl`, et que tout langage sait faire du HTTP et du JSON.

**2011, OpenAPI (ex-Swagger).** REST n'a pas de WSDL, et ça manquait : comment un client sait-il quelles routes existent, avec quels paramètres ? Swagger, devenu OpenAPI en 2016, est un fichier JSON ou YAML qui décrit chaque route, ses paramètres, ses schémas de réponse. On en génère une doc interactive, des clients, des tests. C'est le contrat de REST. FastAPI le génère **automatiquement à partir du code Python**, ce qui est sa grande force (chapitre 17).

**2015, GraphQL.** Chez Facebook, l'application mobile faisait douze requêtes REST pour afficher un écran, et chaque réponse contenait des champs inutiles. GraphQL renverse la logique : **un seul endpoint** (`POST /graphql`), un **schéma typé** côté serveur, et **le client décrit exactement ce qu'il veut** :

```graphql
{
  utilisateur(login: "stranix79") {
    nom
    depots(premiers: 5) {
      nom
      langage
    }
  }
}
```

La réponse a exactement cette forme, rien de plus. Un aller-retour au lieu de douze, pas de sur-récupération. Le prix : un serveur plus complexe (résoudre un graphe arbitraire), le cache HTTP inutilisable (tout est `POST`), des requêtes potentiellement très coûteuses qu'il faut limiter, et une courbe d'apprentissage. Excellent quand un front riche parle à un back-end ; superflu pour un script qui veut la liste des dépôts. GitHub propose les deux (`api.github.com` en REST, `api.github.com/graphql`).

**2016, gRPC.** Google ouvre son protocole interne. Retour à l'appel de procédure (le « RPC » de XML-RPC), mais moderne : le contrat est un fichier **`.proto`** (Protocol Buffers), les messages sont **binaires** (dix fois plus compacts que JSON, et parsés cent fois plus vite), le transport est **HTTP/2** (multiplexage, streaming dans les deux sens), et le code client et serveur est **généré** dans une douzaine de langages.

```proto
service Temperature {
  rpc Convertir (Celsius) returns (Resultat);
}
message Celsius  { double valeur = 1; }
message Resultat { double celsius = 1; double fahrenheit = 2; double kelvin = 3; }
```

Typé, rapide, streaming natif. Mais illisible avec `curl`, pas appelable directement depuis un navigateur (il faut un proxy gRPC-Web), et un outillage à installer. Sa place : **entre microservices** dans un data center, là où le volume et la latence comptent et où personne ne lit les octets à la main. Kubernetes, etcd, et beaucoup de systèmes internes parlent gRPC.

> **Venant du C** : les Protocol Buffers, c'est un `struct` sérialisé avec un schéma versionné. Chaque champ a un numéro (`= 1`, `= 2`) et c'est ce numéro qui passe sur le fil, pas le nom : on peut renommer un champ sans casser les clients, et ajouter un champ sans recompiler les anciens.

### 16.3 Les protocoles à côté

Tout ce qui précède est du **requête-réponse** : le client demande, le serveur répond, fin. Trois besoins n'entrent pas dans ce moule.

**WebSocket** (2011). Le client ouvre une connexion HTTP, demande une « mise à niveau », et la connexion devient un tuyau **bidirectionnel persistant** : les deux côtés envoient des messages quand ils veulent. Chat, tableau de bord temps réel, terminal dans le navigateur, jeux. FastAPI le supporte nativement. Côté client Python : `websockets`.

**SSE** (Server-Sent Events). Le pauvre cousin de WebSocket, mais souvent suffisant : une réponse HTTP qui ne se termine jamais, dans laquelle le serveur pousse des événements texte. Unidirectionnel (serveur → client), passe partout où HTTP passe. C'est ce qu'utilisent les API de LLM pour renvoyer un texte mot par mot.

**Webhooks.** L'API **t'appelle**. Tu donnes une URL à GitHub, et à chaque `push`, GitHub fait un `POST` dessus avec le détail. Pas un protocole, une convention : ton serveur doit exposer une route, vérifier la signature (`X-Hub-Signature-256`), et répondre vite (le traitement lourd en arrière-plan). C'est l'inverse du *polling* (« y a-t-il du nouveau ? » toutes les minutes).

**MQTT.** Pas du HTTP du tout : un protocole publish/subscribe ultra-léger pour l'IoT (capteurs, domotique, Home Assistant). Un *broker* (Mosquitto) au milieu, des clients qui publient sur des *topics* et d'autres qui s'y abonnent. Cité pour que tu le reconnaisses.

**JSON-RPC** (2005, 2.0 en 2010). XML-RPC avec du JSON à la place du XML : un `POST`, `{"jsonrpc": "2.0", "method": "convertir", "params": [20], "id": 1}`. Une page de spécification, quarante lignes pour un serveur (le labo). Utilisé par le **Language Server Protocol** (ce qui fait parler VS Code avec `pyright`), par Ethereum et les portefeuilles crypto, par beaucoup d'outils internes. Preuve que le RPC n'est pas mort : il a juste changé d'habits.

### 16.4 Ce qui est commun à toutes les familles

Quel que soit le protocole, tu retrouveras les mêmes questions, et les mêmes réponses :

**Authentification.** Une clé d'API dans un en-tête (simple, pour un script ou un partenaire), Basic (un login/mot de passe encodé, acceptable seulement en TLS), un jeton **Bearer** obtenu par **OAuth2** (le standard pour déléguer l'accès : « cette application peut lire mes dépôts »), souvent sous forme de **JWT** (un JSON signé, vérifiable sans base de données). Le chapitre 19 implémente OAuth2 + JWT dans FastAPI. SOAP a WS-Security, gRPC a des *credentials* par canal, mais l'idée est la même : chaque requête prouve qui l'envoie.

**Versionnage.** Une API change. Les clients ne se mettent pas à jour tous en même temps. Les stratégies : dans l'URL (`/v1/depots`, le plus courant), dans un en-tête (`Accept: application/vnd.github.v3+json`), ou jamais casser (n'ajouter que des champs optionnels, ce que protobuf impose par construction). Règle : **ajouter est gratuit, retirer ou renommer coûte une version**.

**Idempotence.** Rejouer la même requête donne-t-il le même résultat ? `GET`, `PUT`, `DELETE` : oui par définition. `POST` : non, sauf si le client fournit une **clé d'idempotence** (`Idempotency-Key: uuid`) que le serveur mémorise. Ça compte dès qu'il y a des retries (chapitre 14) : un paiement rejoué deux fois, c'est deux paiements.

**Erreurs.** REST met le sens dans le code HTTP (404, 422) et un détail dans le corps (`{"detail": "..."}`, RFC 9457 « Problem Details » si on veut faire propre). RPC (XML-RPC, JSON-RPC, gRPC) renvoie toujours un transport réussi et met l'erreur **dans l'enveloppe** (`<fault>`, `"error": {"code": -32601}`, un `Status` gRPC). Le labo te fait toucher la différence.

**Contrat et outillage.** WSDL pour SOAP, OpenAPI pour REST, le schéma pour GraphQL, `.proto` pour gRPC. À partir du contrat : génération de clients, validation des entrées, doc, tests de non-régression. Une API sans contrat écrit est une API qu'on découvre en lisant le code du serveur. Ça existe, c'est pénible.

### 16.5 Le tableau

| | SOAP | REST + JSON | GraphQL | gRPC | WebSocket |
|---|---|---|---|---|---|
| Année | 1999 | 2000 (usage massif 2010) | 2015 | 2016 | 2011 |
| Format | XML | JSON (ou autre) | JSON | protobuf (binaire) | libre (texte ou binaire) |
| Transport | HTTP (ou autre) | HTTP | HTTP (`POST`) | HTTP/2 | TCP après poignée de main HTTP |
| Contrat | WSDL | OpenAPI (optionnel) | schéma GraphQL | `.proto` | aucun standard |
| Typage | fort | par convention | fort | fort, généré | aucun |
| Lisible avec `curl` | à peine | oui | oui | non | non |
| Cache HTTP | non | oui (`GET`) | non | non | non |
| Streaming | non | non (SSE à côté) | abonnements | oui, bidirectionnel | oui |
| Depuis un navigateur | pénible | trivial | trivial | via proxy | natif |
| Où on le croise | banques, admin, B2B legacy | partout | fronts riches, mobiles | entre microservices, K8s | temps réel |
| Python | `zeep`, `spyne` | `requests`/`httpx`, FastAPI | `strawberry`, `gql` | `grpcio` | `websockets`, FastAPI |

### 16.6 Que choisir

Pour ce que tu vas écrire :

1. **REST + JSON + OpenAPI**, par défaut. Lisible, universel, `curl`-able, un `TestClient` en trois lignes. C'est FastAPI, et c'est la suite du cours.
2. **gRPC** si tu écris deux services qui se parlent beaucoup dans le même réseau et que la latence ou le volume compte. Pas avant.
3. **GraphQL** si tu as un front-end riche avec des écrans qui agrègent beaucoup de données, et une équipe front qui le demande. Jamais pour un script.
4. **WebSocket ou SSE** dès que le serveur doit pousser (logs en direct, état d'un déploiement, notifications). SSE si c'est du serveur vers client uniquement : plus simple.
5. **SOAP** uniquement parce qu'un partenaire l'impose. Tu ne le choisis pas, tu le subis, et `zeep` rend ça supportable.
6. **Webhooks** pour être prévenu au lieu d'interroger.

Et dans tous les cas : un timeout, une authentification par en-tête, une stratégie de version, et une doc générée depuis le contrat.

### 16.7 Ce qu'il faut retenir

- Un web service expose des fonctions à des programmes via HTTP. Les familles diffèrent par la façon d'encoder l'appel : enveloppe RPC (XML-RPC, SOAP, JSON-RPC, gRPC) ou ressources + verbes HTTP (REST).
- SOAP : XML, WSDL, lourd, legacy d'entreprise. REST : HTTP tel quel, JSON, OpenAPI, standard de fait. GraphQL : le client choisit les champs. gRPC : binaire, typé, rapide, entre services. WebSocket/SSE : le serveur pousse.
- Les questions communes : authentification, versionnage, idempotence, où mettre l'erreur, quel contrat.
- En 2026, par défaut : REST + OpenAPI, donc FastAPI.

**Labo 16** : le même service exposé en REST, en XML-RPC et en JSON-RPC avec la stdlib, et les octets bruts côte à côte.

---

← [15. Asynchrone : asyncio, async/await](15-async.md) · [Sommaire](../README.md) · [17. FastAPI : premiers pas](17-fastapi-premiers-pas.md) →
