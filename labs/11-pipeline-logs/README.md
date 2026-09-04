# Labo 11 — Pipeline de logs en générateurs

**Chapitre** : [11. Itérateurs, générateurs, décorateurs, `with`](../../cours/11-iterateurs-generateurs-decorateurs.md)

## Objectif
Analyser un `access.log` nginx de 500 lignes (`data/access.log`) comme un tube Unix : chaque étage est un générateur, rien n'est chargé en mémoire, et le même code marcherait sur 40 Go.

## Consignes
1. Complète `chrono` : un décorateur qui affiche sur `stderr` la durée de l'appel, avec `@functools.wraps`. Vérifie que `top_ips.__name__` vaut bien `"top_ips"` et pas `"enveloppe"`.
2. Complète `fichier_log` : un gestionnaire de contexte (`@contextmanager`) qui affiche `[ouverture]` et `[fermeture]`, et ferme le fichier **même si** le bloc lève une exception (`try / finally` autour du `yield`).
3. Complète les étages `lire_lignes`, `parser`, `filtrer_code`, `filtrer_chemin` : chacun est un générateur qui consomme le précédent. La regex du format nginx est fournie ; `m.groupdict()` donne un dict, à toi de convertir `code` et `taille` en entiers.
4. Complète les agrégations avec `Counter` et termine `main` : top 5 des IP, répartition des codes, top 5 des IP en erreur (code ≥ 400), octets servis par chemin sous `/api`. Sortie attendue (les chiffres, pas les lignes `[chrono]`) :
   ```
   Top 5 des IP :
     203.0.113.42      140
     ...
   Répartition des codes HTTP :
     200   ...
   ```
   Compare avec `python3 solution/pipeline.py`.
5. Bonus : `suivre()` est un `tail -f` en générateur infini (`seek` à la fin, `readline`, `sleep` si rien). Lance `python3 pipeline.py data/access.log --follow` dans un terminal et, dans un autre, `echo '10.0.0.1 - - [04/Sep/2026:10:00:00 +0200] "GET /test HTTP/1.1" 200 12 "-" "curl"' >> data/access.log`. Ctrl-C pour arrêter. Remets le fichier d'origine avec `git checkout data/access.log`.
6. Bonus 2 : `main` relit le fichier quatre fois parce qu'un générateur épuisé ne se rembobine pas. Réécris-le pour ne lire qu'une fois, en alimentant plusieurs `Counter` dans la même boucle. Mesure la différence avec `@chrono`.

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 pipeline.py                     # ton squelette (plante sur les TODO)
python3 solution/pipeline.py            # la solution
python3 solution/pipeline.py data/access.log 2>/dev/null   # sans les lignes [chrono]
```

## Pour aller plus loin
- Remplace `Counter(e["ip"] for e in entrees)` par une version avec une liste intermédiaire et compare `sys.getsizeof` sur un fichier de 1 million de lignes (`for i in {1..2000}; do cat data/access.log; done > /tmp/gros.log`).
- `itertools.groupby` sur les entrées triées par heure (`date[:14]`) donne un histogramme par heure en trois lignes.
- La même chose en shell : `grep -v ' 200 ' data/access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -5`. Compare la lisibilité et la vitesse.
