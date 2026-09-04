# 0. Pourquoi Python, et pourquoi maintenant

*Python de zéro à FastAPI — chapitre 0 sur 21.* [Sommaire](../README.md) · [1. Installer, outiller, lancer](01-installer-et-outiller.md) →

Tu as connu le BASIC du Commodore 64 : tu tapais une ligne, tu appuyais sur RETURN, la machine répondait. Puis le C : tu écris, tu compiles, tu lies, tu lances, et entre les deux, le compilateur te dispute sur un point-virgule. Puis Java : tout est une classe, même quand tu voulais juste afficher un nombre.

Python, c'est un peu le retour au C64, mais avec quarante ans de progrès dedans. Tu ouvres un terminal, tu tapes `python3`, tu écris `2 ** 100`, et la machine répond `1267650600228229401496703205376` sans que tu aies à te demander dans combien de bits ça tient. Pas de compilation à lancer, pas de déclaration de type, pas de `public static void main`. Et pourtant ce n'est pas un jouet : c'est le langage des scripts d'infrastructure, d'Ansible, de la data, de l'IA, et d'une bonne partie des API web modernes.

### 0.1 Ce que Python fait différemment

Trois choses à savoir avant même la première ligne, parce qu'elles expliquent tout le reste :

1. **Interprété, pas compilé en machine.** Ton fichier `.py` est lu, transformé en *bytecode* (un jeu d'instructions pour une machine virtuelle, pas pour ton processeur), puis exécuté par l'interpréteur CPython, lui-même écrit en C. Conséquence : tu peux tester une idée en trois secondes, et le programme tourne tel quel sur Mac, Linux et Windows. L'autre conséquence : c'est plus lent que du C, souvent 10 à 100 fois. On verra au chapitre 10 quand ça compte et quand ça ne compte pas (spoiler : rarement pour ce que tu vas faire).
2. **Typage dynamique, mais fort.** `x = 5` puis `x = "cinq"` est légal : la variable n'a pas de type, c'est la *valeur* qui en a un. Mais `5 + "cinq"` plante, là où C aurait fait n'importe quoi en silence et où JavaScript t'aurait donné `"5cinq"`. Python ne devine pas à ta place.
3. **Tout est objet, et les variables sont des étiquettes.** En C, `int a = 5;` réserve 4 octets qui *contiennent* 5. En Python, `a = 5` crée un objet entier quelque part et colle l'étiquette `a` dessus. `b = a` colle une deuxième étiquette sur le *même* objet. Tant que tu manipules des nombres et des chaînes, ça ne change rien. Dès que tu manipules des listes, ça change tout. C'est le piège numéro un de ceux qui viennent du C, et on y consacre le chapitre 10.

### 0.2 Ce que tu vas faire avec

Le cours suit un fil : **chapitre → labo**. Lis le chapitre, fais le labo (il y a un squelette à compléter avec des `# TODO` et une solution commentée), passe au suivant.

Les chapitres 1 à 9 posent le langage. Si tu as déjà bricolé en Python, lis-les quand même vite : ils sont écrits pour quelqu'un qui vient du C, et ils corrigent les habitudes qu'on prend en copiant-collant.

Les chapitres 10 à 13 font de toi quelqu'un qui *comprend* Python : ce qui se passe en mémoire, les générateurs et décorateurs (partout dans les bibliothèques que tu vas utiliser), les tests, et les outils en ligne de commande, parce que c'est ce qu'un DevOps écrit tous les jours.

Les chapitres 14 à 21 sont le web : HTTP côté client, l'asynchrone, un panorama honnête des web services (REST, SOAP, GraphQL, gRPC, WebSocket… et pourquoi tout le monde a fini par faire du REST avec du JSON), FastAPI, une base de données, l'authentification, les tests d'API, Docker et le déploiement.

### 0.3 Ce que tu sauras faire à la fin

- écrire du Python idiomatique, pas du C traduit mot à mot ;
- structurer un projet (modules, paquets, `pyproject.toml`, tests, linter) ;
- manipuler fichiers, JSON, CSV, SQLite ;
- écrire des outils en ligne de commande pour ton quotidien ;
- consommer et exposer des API HTTP, expliquer les différences entre les familles de web services ;
- construire, tester et déployer une API FastAPI complète ;
- lire du code Python de bibliothèque sans être perdu.

### 0.4 Comment lire ce cours

Le code est en Python 3.13. Tout ce qui est écrit dans un bloc `python` a été exécuté. Les blocs qui commencent par `>>>` sont des sessions dans l'interpréteur interactif : tape la ligne, regarde la réponse.

```python
>>> 2 ** 100
1267650600228229401496703205376
>>> type(2 ** 100)
<class 'int'>
```

Quand une notion a un équivalent en C ou en Java, il est donné dans un encadré. Quand Python fait quelque chose qui te paraîtra bizarre venant du C, c'est signalé par **piège**. Il y en a une dizaine dans tout le cours, et les connaître d'avance fait gagner des heures.

Compte une à deux heures par chapitre. Ne saute pas les labos : lire du Python donne l'impression de comprendre, écrire du Python fait comprendre.

---

[Sommaire](../README.md) · [1. Installer, outiller, lancer](01-installer-et-outiller.md) →
