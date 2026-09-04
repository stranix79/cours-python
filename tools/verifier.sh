#!/usr/bin/env bash
# tools/verifier.sh — vérifie que le cours est cohérent :
#   1. tous les liens relatifs des .md pointent vers un fichier existant ;
#   2. chaque solution de labo se lance (ou ses tests passent avec SOLUTION=1).
# Lancé par : ./tools/verifier.sh depuis la racine du dépôt (le .venv doit exister).
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
erreurs=0

echo "== Liens markdown"
# Extrait chaque [texte](cible) des .md, ignore les URLs, vérifie que la cible existe.
while IFS=: read -r fichier cible; do
    cible="${cible%%#*}"                       # enlève l'ancre #section
    [ -z "$cible" ] && continue
    chemin="$(dirname "$fichier")/$cible"
    if [ ! -e "$chemin" ]; then
        echo "  CASSÉ  $fichier → $cible"
        erreurs=$((erreurs + 1))
    fi
done < <(grep -r --include='*.md' -H '' README.md cours labs tools \
         | awk -F: '{ if ($2 ~ /^```/) { fence[$1] = !fence[$1]; next } if (!fence[$1]) print }' \
         | sed -E 's/`[^`]*`//g' \
         | grep -o -E '^[^:]+:.*\]\([^)]+\)' \
         | sed -E 's/^([^:]+):.*\]\(([^)]+)\)$/\1:\2/' | grep -v -E ':(https?:|mailto:)')
echo "  liens vérifiés"

echo "== Labos"
for labo in labs/*/; do
    nom=$(basename "$labo")
    if ls "$labo"/test_*.py >/dev/null 2>&1; then
        # Labo avec tests : la solution doit les faire passer.
        if (cd "$labo" && SOLUTION=1 ../../$PY -m pytest -q -p no:cacheprovider >/tmp/verif_$nom.log 2>&1); then
            echo "  OK     $nom (pytest)"
        else
            echo "  ÉCHEC  $nom (pytest) → /tmp/verif_$nom.log"
            erreurs=$((erreurs + 1))
        fi
    elif [ -f "$labo/solution/verifier.sh" ]; then
        # Labo qui fournit son propre script de vérification.
        if (cd "$labo/solution" && bash verifier.sh >/tmp/verif_$nom.log 2>&1); then
            echo "  OK     $nom (verifier.sh)"
        else
            echo "  ÉCHEC  $nom (verifier.sh) → /tmp/verif_$nom.log"
            erreurs=$((erreurs + 1))
        fi
    else
        echo "  —      $nom (pas de test automatique, voir son README)"
    fi
done

find . -name __pycache__ -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null
echo
if [ "$erreurs" -eq 0 ]; then echo "Tout est bon."; else echo "$erreurs problème(s)."; exit 1; fi
