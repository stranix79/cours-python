# Labo 13 — `srvctl`, un outil DevOps en ligne de commande

**Chapitre** : [13. Ligne de commande et scripts DevOps](../../cours/13-ligne-de-commande-et-devops.md)

## Objectif
Écrire avec typer un outil `srvctl` qui lit un inventaire JSON, pingue des serveurs, lance des commandes locales et affiche l'environnement, avec une sortie humaine (tableaux rich) ou JSON, un `--dry-run`, des codes de sortie corrects, et des tests qui ne lancent jamais un vrai `ping`.

## Consignes
1. Lance `pytest` : 22 tests, presque tous en échec sur `NotImplementedError`. Lance aussi `python3 srvctl.py --help` : la structure des commandes est déjà là, l'aide est générée depuis les signatures et les docstrings.
2. Complète les **fonctions pures** (`charger_inventaire`, `filtrer`, `trouver`, `masquer`) jusqu'à ce que les tests `test_charger_*`, `test_filtrer`, `test_trouver_*`, `test_masquer_*` passent. `pytest -k "filtrer or masquer"` pour ne lancer que ceux-là.
3. Complète `ping_hote` et `lancer` (les seules fonctions qui touchent `subprocess`), puis les commandes `ping`, `exec`, `env`. Règles du contrat shell : résultat sur stdout, messages sur stderr, `--json` = JSON brut sur stdout (`print`, pas `console.print`), code 0 si tout va bien, 1 si un ping échoue, 2 si aucune cible, celui de la commande pour `exec`.
4. Vérifie à la main :
   ```bash
   python3 srvctl.py list -g ops
   python3 srvctl.py --json list -t nginx | python3 -c "import json,sys; print([s['nom'] for s in json.load(sys.stdin)])"
   python3 srvctl.py ping web1 bastion --timeout 1 ; echo "code $?"
   python3 srvctl.py --dry-run ping --all
   python3 srvctl.py exec -- ls /nexiste ; echo "code $?"
   APP_TOKEN=xyz APP_ENV=dev python3 srvctl.py env -p APP_
   ```
   `web1` répond (c'est `127.0.0.1`), `bastion` ne se résout pas, `db1` (une adresse de documentation, 192.0.2.10) tombe en timeout.
5. Regarde `test_srvctl.py` : la fixture `faux_run` remplace `subprocess.run` par une fonction qui note les appels. Ajoute un test pour `exec` qui vérifie le code 127 quand la commande n'existe pas (fais lever `FileNotFoundError` par le faux `run`).
6. Bonus : `chmod +x srvctl.py` puis `./srvctl.py list`. Ajoute un gestionnaire `SIGTERM` (chapitre 13.6) qui affiche « arrêt demandé » et sort avec 143 ; teste avec `python3 srvctl.py exec -- sleep 30 &` puis `kill %1`.
7. Bonus 2 : une sous-commande `ssh NOM -- COMMANDE` qui construit `["ssh", hote, commande]` avec `shlex.join`, en `--dry-run` seulement (tu n'as sûrement pas ces serveurs). Le test vérifie la ligne affichée.

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 srvctl.py --help
pytest                          # tes tests contre ton squelette
pytest -k pures -v              # (adapte -k au nom des tests que tu vises)
SOLUTION=1 pytest               # les mêmes tests contre solution/srvctl.py
python3 solution/srvctl.py list # la solution, à la main
```

## Pour aller plus loin
- Remplace typer par argparse dans une copie du fichier : même comportement, combien de lignes en plus ? C'est le prix de zéro dépendance.
- `python3 srvctl.py --json ping --all | jq '.[] | select(.ok == false) | .hote'` : ton outil s'enchaîne maintenant avec le reste du monde Unix.
- Chapitre 20 : un `pyproject.toml` avec `[project.scripts] srvctl = "srvctl:app"` et `pip install -e .` font apparaître la commande `srvctl` dans ton `PATH`.
