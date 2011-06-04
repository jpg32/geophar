#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#        Global search utility           #
##--------------------------------------##
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import os
import sys

def gs(chaine = '', case = True, exclude_comments = True, extensions = (".py", ".pyw"), exclude_prefixe = ("tmp_", "Copie"), exclude_suffixe = ("_OLD", "(copie)"), exclude_dir = ('sympy', 'tools', 'BAZAR', 'OLD'), maximum = 100, codec="latin1", statistiques = False):
    u"""Parcourt le r�pertoire courant et les sous-r�pertoire, � la recherche des fichiers dont l'extension
    est comprise dans 'extensions', mais passe les r�pertoires et les fichiers dont le nom commence par un pr�fixe
    de 'exclude_prefixe', ou finit par un suffixe de 'exclude_suffixe'.
    Pour chaque fichier trouv�, renvoie toutes les lignes o� 'chaine' se trouve.
    (Par d�faut, la casse est prise en compte, sinon, il suffit de modifier la valeur de 'case'.)
    Le nombre maximal de lignes renvoy�es est fix� par 'maximum', afin d'�viter de saturer le syst�me.
    Si ce nombre est d�pass� (ie. toutes les occurences de 'chaine' ne sont pas affich�es), la fonction renvoie False, sinon, True.
    """
    if not chaine:
        statistiques = True
    if not case:
        chaine = chaine.lower()
    repertoires = os.walk(os.getcwd())
    fichiers = []
    for root, dirs, files in repertoires:
        #print root
        if any((os.sep + prefixe in root) for prefixe in exclude_prefixe):
            continue
        if any((os.sep + dir + os.sep) in root for dir in exclude_dir):
            continue
        if any(root.endswith(os.sep + dir) for dir in exclude_dir):
            continue
        if any(root.endswith(suffixe) for suffixe in exclude_suffixe):
            continue
        if any((suffixe + os.sep) in root for suffixe in exclude_suffixe):
            continue
        files = [f for f in files if not any(f.startswith(prefixe) for prefixe in exclude_prefixe) and not any(f.endswith(suffixe + extension) for suffixe in exclude_suffixe for extension in extensions)]
        files = [f for f in files if f[f.rfind("."):] in extensions]

        fichiers += [root + os.sep + f for f in files]
    # nombre de lignes de code au total
    N = 0
    # nombre de lignes de commentaires au total
    C = 0
    # nombre de fichiers
    F = 0
    # nombre de lignes vides
    B = 0
    # nombre de lignes contenant l'expression recherch�e
    n_lignes = 0
    # Nombre d'occurences trouv�es.
    occurences = 0
    for f in fichiers:
        F += 1
        fichier = open(f, "r")
        # n� de la ligne analys�e � l'int�rieur du fichier
        n = 0
        for s in fichier:
            n += 1
            if statistiques:
                s = s.strip()
                if s:
                    if s[0] != '#':
                        N += 1
                    elif s.strip('#'):
                        C += 1
                    else:
                        B += 1
                else:
                    B += 1
                continue
            if (exclude_comments and s.lstrip().startswith("#")):
                continue
            if not case:
                s = s.lower()
            if s.find(chaine) != -1:
                occurences += 1
                print u"in %s " %f
                print u"line " + unicode(n) + ":   " + s.decode(codec)
                n_lignes += 1
                if n_lignes > maximum:
                    print "Maximum output exceeded...!"
                    return False
        fichier.close()
    if statistiques:
        # C - 20*F : on d�compte les pr�ambules de tous les fichiers
        return str(N) + " lignes de code\n" + str(C) + " lignes de commentaires (" + str(C - 20*F) + " hors licence)\n" + str(B) + " lignes vides\n" + str(F) + " fichiers"
    return u"%s occurence(s) trouv�e(s)." %occurences


def gr(chaine, chaine_bis, exceptions = (), extensions = (".py", ".pyw")):
    u"""Remplace 'chaine' par 'chaine_bis' dans tous les fichiers dont l'extension (.txt, .bat, ...)
    est comprise dans 'extensions', et n'est pas comprise dans 'exceptions'.
    """
    y = yes = True
    n = no = False
    txt_exceptions = exceptions and "but " + ", ".join(exceptions) + " " or ""
    b = input("Warning: Replace string '%s' by string '%s' in ALL files %s[y/n] ?" %(chaine, chaine_bis, txt_exceptions))
    if b is not True:
        return "Nothing done."
    repertoires=os.walk(os.getcwd())
    fichiers = []
    for r in repertoires:
        fichiers += [r[0] + os.sep + f for f in r[2] if f[f.rfind("."):] in extensions and f not in exceptions]
    n_lignes = 0
    occurences = 0 # nombre de remplacements effectu�s
    for f in fichiers:
        fichier = open(f, "r")
        s = fichier.read()
        fichier.close()
        fichier = open(f, "w")
        occurences += s.count(chaine)
        s = fichier.write(s.replace(chaine, chaine_bis))
        fichier.close()
    return u"%s remplacement(s) effectu�(s)." %occurences


def usage():
    print u"""\n    === Usage ===\n
    - Rechercher la cha�ne 'hello' dans le code :
        $ ./tools/search.py "hello"
    - Remplacer partout la cha�ne 'hello' par la cha�ne 'world':
        $ ./tools/search.py -r "hello" "world"
        """
    exit()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        usage()
    if args[0] == '-r':
        if len(args) < 3:
            usage()
        print gr(args[1], args[2])
    else:
        print "\n=== Recherche de %s ===\n" %repr(args[0])
        print gs(args[0])
