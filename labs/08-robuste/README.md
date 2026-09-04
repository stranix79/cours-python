# Labo 08 — Un script de déploiement qui échoue proprement

**Chapitre** : [8. Erreurs, exceptions, logging](../../cours/08-erreurs-exceptions-logging.md)

## Objectif
Prendre un script naïf qui lit un `config.json` et un fichier de hosts, et le rendre robuste : messages d'erreur utiles, exception maison, logging console + fichier, codes de sortie que le shell peut tester.

## Consignes
1. Lance la version naïve sur les bons fichiers, puis sur chaque fichier cassé de `data/` (`config-absent.json` qui n'existe pas, `config-invalide.json`, `config-incomplet.json`, `config-port-texte.json`, `hosts-vide.txt`). Note ce qui se passe : traceback brut, ou pire, exécution avec des données fausses (regarde ce que fait `hosts.txt` avec ses commentaires).
2. Définis `ConfigError(Exception)`. Dans `charger_config`, convertis `FileNotFoundError`, `PermissionError` et `json.JSONDecodeError` en `ConfigError` avec un message clair et chaîné (`raise ... from e`). Vérifie les clés obligatoires et le type de `port` et `replicas`.
3. Dans `charger_hosts`, ignore les lignes vides et les commentaires, et refuse une liste vide. Décide si tu convertis les erreurs de fichier en exception maison ou si tu les laisses remonter, et écris pourquoi en commentaire.
4. Dans `main`, un seul `try` : `ConfigError` → code 2, erreur de hosts → code 3, `KeyboardInterrupt` → 130, tout le reste → `log.exception` et code 1. Vérifie avec `echo $?` après chaque lancement.
5. Configure le logging : console (stderr) au niveau `INFO`, fichier `deploy.log` au niveau `DEBUG` avec date, niveau, fonction et ligne. Les commandes `docker run` restent sur stdout : `python3 deploy.py data/config.json data/hosts.txt 2>/dev/null` ne doit montrer qu'elles.
6. Teste la permission refusée : `chmod 000 data/config-prive.json`, lance, puis `chmod 644` pour remettre.
7. Bonus : ajoute `--dry-run` / `--verbose` en lisant `sys.argv` à la main (on fera ça proprement avec `argparse` au chapitre 13). `--verbose` passe la console en `DEBUG`.

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 deploy.py data/config.json data/hosts.txt ; echo "code=$?"
python3 deploy.py data/config-invalide.json data/hosts.txt ; echo "code=$?"
python3 solution/deploy.py data/config.json data/hosts.txt
cat deploy.log
```

Sortie attendue de la solution sur les bons fichiers :
```
INFO: déploiement simulé sur 3 hôte(s)
[web-01.stranix.net] docker run -d -p 8443:8443 --name api-facturation registry.stranix.net/api-facturation:2.4.1  (x3)
[web-02.stranix.net] docker run -d -p 8443:8443 --name api-facturation registry.stranix.net/api-facturation:2.4.1  (x3)
[web-03.stranix.net] docker run -d -p 8443:8443 --name api-facturation registry.stranix.net/api-facturation:2.4.1  (x3)
```
Et sur `config-invalide.json`, code de sortie 2 :
```
ERROR: JSON invalide dans data/config-invalide.json, ligne 5 colonne 16 : Illegal trailing comma before end of object
```

## Pour aller plus loin
- `logging.handlers.RotatingFileHandler` pour que `deploy.log` ne grossisse pas indéfiniment ; `SysLogHandler` pour l'envoyer à syslog/journald.
- Remplace le format texte du fichier par du JSON (une ligne par événement) : c'est ce que Loki, Elasticsearch ou Datadog attendent. Un `Formatter` maison qui renvoie `json.dumps({...})` suffit.
- `python3 -X dev deploy.py ...` active le mode développement : avertissements supplémentaires, dont les fichiers jamais fermés.
