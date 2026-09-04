# conftest.py — Labo 20 : fichier lu par pytest avant les tests.
#
# Il est vide, et c'est justement le point : sa seule présence fait que pytest
# ajoute CE dossier en tête de sys.path. Résultat, `import outils` marche dans
# les tests parce que le dossier outils/ est là, à côté, pas parce que le
# paquet est installé. C'est le défaut du layout « à plat » : les tests passent
# chez toi même si l'installation du paquet est cassée.
#
# Avec le src/ layout (consigne 4), ce fichier disparaît, et `import outils`
# ne marche plus que si le paquet est installé (pip install -e .).
