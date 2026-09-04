# outils/reseau.py — Labo 20 : fonctions réseau. Volontairement sale.
import socket, ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse
import re

def est_ip_valide(s):
    try:
        ipaddress.ip_address(s)
        return True
    except:
        return False

def est_privee(s) -> str:
    return ipaddress.ip_address(s).is_private

def decouper_url(url):
    p = urlparse(url)
    port = p.port
    if port == None:
        port = 443 if p.scheme == "https" else 80
    return (p.scheme, p.hostname, port, p.path or "/")

def port_ouvert(hote, port, timeout = 1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((hote, port))
        return True
    except (OSError):
        return False
    finally:
        s.close()

def masque_vers_prefixe(masque):
    return ipaddress.IPv4Network("0.0.0.0/%s" % masque).prefixlen
