#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                  Erreurs                    #
##--------------------------------------#######
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

# version unicode


# g�n�r� par :
# import exceptions;l = ["    " + key + ": u\"\"\"" + val.__doc__ + "\"\"\"" for key, val in vars(exceptions).items() if not isinstance(val, basestring)];l.sort();print "messages = {\n" + ",\n".join(l) + "\n}"


messages = {
    ArithmeticError: u"""Erreur de calcul.""",
    AssertionError: u"""Assertion failed.""",
    AttributeError: u"""L'attribut n'existe pas.""",
    BaseException: u"""Common base class for all exceptions""",
    DeprecationWarning: u"""Base class for warnings about deprecated features.""",
    EOFError: u"""Read beyond end of file.""",
    EnvironmentError: u"""Base class for I/O related errors.""",
    Exception: u"""Common base class for all non-exit exceptions.""",
    FloatingPointError: u"""Erreur de calcul (flottants).""",
    FutureWarning: u"""Base class for warnings about constructs that will change semantically
in the future.""",
    GeneratorExit: u"""Request that a generator exit.""",
    IOError: u"""Impossible d'�crire sur le p�riph�rique.""",
    ImportWarning: u"""Base class for warnings about probable mistakes in module imports""",
    ImportError: u"""Module introuvable.""",
    IndentationError: u"""Indentation incorrecte.""",
    IndexError: u"""Indexage incorrect.""",
    KeyError: u"""R�f�rence non trouv�e (cl�).""",
    KeyboardInterrupt: u"""Program interrupted by user.""",
    LookupError: u"""Base class for lookup errors.""",
    MemoryError: u"""Manque de m�moire.""",
    NameError: u"""Nom inconnu.""",
    NotImplementedError: u"""Method or function hasn't been implemented yet.""",
    OSError: u"""OS system call failed.""",
    OverflowError: u"""Le r�sultat est trop grand.""",
    PendingDeprecationWarning: u"""Base class for warnings about features which will be deprecated
in the future.""",
    ReferenceError: u"""R�f�rence non trouv�e (r�f�rence faible).""",
    RuntimeError: u"""Unspecified run-time error.""",
    RuntimeWarning: u"""Base class for warnings about dubious runtime behavior.""",
    StandardError: u"""Base class for all standard Python exceptions that do not represent interpreter exiting.""",
    StopIteration: u"""Fin d'it�ration.""",
    SyntaxError: u"""Erreur de syntaxe.""",
    SyntaxWarning: u"""Base class for warnings about dubious syntax.""",
    SystemError: u"""Internal error in the Python interpreter.""",
    SystemExit: u"""Request to exit from the interpreter.""",
    TabError: u"""Improper mixture of spaces and tabs.""",
    TypeError: u"""Type d'argument incorrect.""",
    UnboundLocalError: u"""R�f�rence � une variable non d�finie.""",
    UnicodeDecodeError: u"""Probl�me de d�codage (caract�res sp�ciaux).""",
    UnicodeEncodeError: u"""Probl�me d'encodage (caract�res sp�ciaux).""",
    UnicodeError: u"""Erreur unicode (caract�res sp�ciaux).""",
    UnicodeTranslateError: u"""Erreur unicode (caract�res sp�ciaux).""",
    UnicodeWarning: u"""Probl�me d'encodage.""",
    UserWarning: u"""Base class for warnings generated by user code.""",
    ValueError: u"""Valeur interdite.""",
    Warning: u"""Base class for warning categories.""",
    ZeroDivisionError: u"""Division par z�ro."""
}

try:
    messages[WindowsError] = u"""MS-Windows OS system call failed."""
except NameError: # non d�fini sous Linux par exemple
    pass

def message(erreur):
    try:
        super(erreur) # si �a marche, c'est une "classe", sinon, c'est une instance
        return messages.get(erreur, u"Erreur inconnue.")
    except TypeError:
        return messages.get(type(erreur), u"Erreur inconnue.")
