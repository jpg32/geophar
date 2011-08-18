# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
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

from PyQt4.QtGui import QApplication#, QPalette, QColor
from PyQt4.QtCore import QLocale, QTranslator, QLibraryInfo


class App(QApplication):
    def __init__(self, args=[], **kw):
        QApplication.__init__(self, args)
        locale = QLocale.system().name()
        translator=QTranslator ()
        translator.load("qt_" + locale,
                      QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        self.installTranslator(translator)

    def boucle(self):
        self.exec_()

    def nom(self, nom=''):
        self.setApplicationName(nom)

    def vers_presse_papier(self, texte):
        self.clipboard().setText(texte)
        return True

app = App()
#app.setStyleSheet("background-color:white")
#palette = app.palette()
#palette.setColor(QPalette.Active, QPalette.Window, QColor('white'))
#palette.setColor(QPalette.Inactive, QPalette.Window, QColor('white'))
