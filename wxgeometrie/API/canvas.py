# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

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

from math import isinf, isnan

import numpy
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .moteur_graphique import Moteur_graphique
from ..pylib import decorator, property2, print_error, WeakList, str2, no_argument
from ..geolib import Feuille
from .. import param


class GelAffichage(object):
    def __init__(self, canvas, geler=True, actualiser=False, seulement_en_apparence=False, sablier=False):
        self.sablier = sablier
        self.canvas = canvas
        self.geler = geler
        self.actualiser = actualiser
        self.attribut = ('_affichage_gele_en_apparence' if seulement_en_apparence else '_affichage_gele')

    def __enter__(self):
        self._ancienne_valeur = getattr(self.canvas, self.attribut)
        if self.geler is not None:
            setattr(self.canvas, self.attribut, self.geler)
        if self.sablier:
            self.canvas._curseur(sablier=True)

    def __exit__(self, type, value, traceback):
        setattr(self.canvas, self.attribut, self._ancienne_valeur)
        if self.actualiser:
            self.canvas.rafraichir_affichage()
        if self.sablier:
            self.canvas._curseur(sablier=False)


# Garde une trace dans les logs de chaque appel de la m�thode pour d�bogage.
@decorator
def track(meth, self, *args, **kw):
    if param.debug:
        s = "%s - Args: %s, %s" % (meth.func_name, args, kw)
        self.parent.action_effectuee(s)
    return meth(self, *args, **kw)

# Garde une trace dans les logs de chaque appel *isol�* de la m�thode pour d�bogage.
# Par exemple, en cas de zoom avec la roulette de souris, seul le dernier zoom
# sera enregistr�, pour ne pas saturer le fichier .log
@decorator
def partial_track(meth, self, *args, **kw):
    if param.debug:
        s = "%s - Args: %s, %s" % (meth.func_name, args, kw)
        self.parent.action_effectuee(s, signature = meth.func_name)
    return meth(self, *args, **kw)







class Canvas(FigureCanvasAgg):
    u'Partie du canvas ind�pendante de la librairie graphique (Wx actuellement).'

    def __init__(self, couleur_fond = 'w', dimensions = None, feuille = None):
        self.figure = Figure(dpi = param.dpi_ecran, frameon=True, facecolor = couleur_fond)
        FigureCanvasAgg.__init__(self, self.figure)
        self.axes = self.figure.add_axes([0, 0, 1, 1], frameon=False)
        self._dimensions = dimensions
        self.__feuille_actuelle = feuille
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        # Ces param�tres ne sont utiles que pour les sur-classes s'int�grant dans un GUI.
        self.editeur = None
        self.select = None             # objet couramment s�lectionn�

        #if self.param("transformation_affine") is not None:
        #    self.transformation = matplotlib.transforms.Affine(*self.param("transformation_affine"))
        #    self.figure.set_transform(self.transformation)
        #    self.axes.set_transform(self.transformation)
        #else:
        #    self.transformation = None
        if self.param("transformation") is not None:
            a, b, c, d = self.param("transformation")
            # CODE � R��CRIRE et � ADAPTER
            self.transformation = numpy.matrix([[a, b], [c, d]])
        else:
            self.transformation = None

        self._affichage_gele = False
        # Ne pas utiliser directement.
        # Si on met la valeur a True, self.rafraichir_affichage() ne fait plus rien.
        # Cela permet d'effectuer un certain nombre d'actions rapidement,
        # et de n'actualiser qu'� la fin.
        # En particulier, cela sert pour charger une figure depuis un fichier .geo
        self._affichage_gele_en_apparence = False
        # Ne pas utiliser directement.
        # Si on met la valeur a True, self.rafraichir_affichage() fonctionne toujours,
        # mais les changements ne s'affichent pas � l'�cran.
        # Cela permet d'effectuer un certain nombre d'actions sans que l'utilisateur s'en apercoive
        # (pas de clignotement de l'affichage).
        # Par contre, le gain de temps est n�gligeable par rapport � un vrai gel de l'affichage.
        # En particulier, cela sert pour exporter une figure.


        self.graph = Moteur_graphique(self)
        self.parametres = [u"taille", u"gradu", u"afficher_axes", u"afficher_quadrillage",
                           u"afficher_fleches", u"repere", u"resolution", u"origine_axes",
                           u"utiliser_repere", u"quadrillages", u"couleur_papier_millimetre",
                           u"liste_axes", u"orthonorme", u"grille_aimantee", u"zoom_texte", "zoom_ligne"]
        self.liste_objets_en_gras = WeakList()
        self.initialiser()


    @property2
    def feuille_actuelle(self, val = None):
        if val is None:
            return self.__feuille_actuelle
        self.__feuille_actuelle = val

    def initialiser(self):
        # actions a effectuer avant de r��xecuter l'historique
        for parametre in self.parametres:
            setattr(self, parametre, self.param(parametre))


    def exporter(self, fichier, format=None, dpi=None, zone=None, echelle=None, taille=None, keep_ratio=False):
        u"""Export de la feuille sous forme d'un fichier (png, eps, ...).

        :param string,unicode,file fichier: le fichier lui-m�me, ou son emplacement.
        :param format: le format de l'image (PNG, SVG, ...).
                       Inutile si le nom du fichier est donn� avec une extension connue.
        :param int,float dpi: r�solution souhait�e (en dot par inch)
        :param tuple zone: (xmin, xmax, ymin, ymax) : pour n'exporter qu'une partie de la feuille (png seulement).
        :param tuple echelle: (x, y) : nombre de cm pour une unit� en abscisse ; en ordonn�e
        :param tuple taille: (largeur, hauteur) : taille de l'image en cm.
        :param bool keep_ratio: indique si le ratio doit �tre pr�serv� en cas de redimensionnement.

        Les param�tres `echelle` et `taille` ne peuvent �tre fournis simultan�ment.
        """

        if isinstance(fichier, unicode):
            fichier = str2(fichier) # la m�thode savefig ne g�re pas l'unicode
        dpi = dpi or param.dpi_export

        if self.editeur is not None:
            # Evite d'exporter la feuille avec un nom d'objet en cours d'�dition
            self.editeur.close()
        # De m�me, aucun objet ne doit �tre en gras
        self.feuille_actuelle.objets_en_gras()
        # Les objets invisibles ne doivent pas apparaitre
        afficher_objets_caches = self.afficher_objets_caches
        self.afficher_objets_caches = False

        self.graph.exporter(fichier=fichier, format=format, dpi=dpi, zone=zone, echelle=echelle, taille=taille, keep_ratio=keep_ratio)

        self.afficher_objets_caches = afficher_objets_caches
        self.selection_en_gras()



    def selection_en_gras(self):
        self.feuille_actuelle.objets_en_gras(self.select, *self.liste_objets_en_gras)

#   Alias
######################

    def dessiner_ligne(self, *args, **kw):
        return self.graph.ajouter_ligne(*args, **kw)

    def dessiner_polygone(self, *args, **kw):
        return self.graph.ajouter_polygone(*args, **kw)

    def dessiner_texte(self, *args, **kw):
        return self.graph.ajouter_texte(*args, **kw)

    def dessiner_arc(self, *args, **kw):
        return self.graph.ajouter_arc(*args, **kw)

    def dessiner_point(self, *args, **kw):
        return self.graph.ajouter_point(*args, **kw)


    def ligne(self, *args, **kw):
        return self.graph.ligne(*args, **kw)

    def polygone(self,  *args, **kw):
        return self.graph.polygone(*args, **kw)

    def texte(self, *args, **kw):
        return self.graph.texte(*args, **kw)

    def arc(self, *args, **kw):
        return self.graph.arc(*args, **kw)

    def point(self, *args, **kw):
        return self.graph.point(*args, **kw)

    def fleche(self, *args, **kw):
        return self.graph.fleche(*args, **kw)

    def fleche_courbe(self, **kw):
        return self.graph.fleche_courbe(**kw)

    def codage(self, **kw):
        return self.graph.codage(**kw)

    def angle(self, **kw):
        return self.graph.angle(**kw)

    def codage_angle(self, **kw):
        return self.graph.codage_angle(**kw)

    def rectangle(self, **kw):
        return self.graph.rectangle(**kw)

    def decoration_texte(self, **kw):
        return self.graph.decoration_texte(**kw)

    def lignes(self, *args, **kw):
        return self.graph.lignes(*args, **kw)

    def dessiner(self, objet):
        self.graph.ajouter(objet)

##################################
# Les fonctions suivantes assurent la conversion pixel <-> coordonnees
##################################
# en multipliant m par coeff(0), on convertit un ecart en abcisses de m pixels en coordonnees.
# en multipliant n par coeff(1), on convertit un ecart en ordonnees de n pixels en coordonnees.
# Les fonctions qui suivent permettent la conversion d'un couple de coordonnees en pixels, et reciproquement.
# Si le mode est fixe a 1, le pixel (0,0) sera le coin inferieur gauche (plus intuitif).
# Si le mode est fixe a -1, le pixel (0,0) sera le coin superieur gauche (convention, respectee par WxPython).

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def largeur(self):
        return self.dimensions[0]

    @property
    def hauteur(self):
        return self.dimensions[1]

    def pas(self):
        #print 'pas:', self.fenetre, self.resolution
        return (self.fenetre[1] - self.fenetre[0])/(self.resolution)

    ## <DESUET> ##
    def coeff(self, i): # DESUET
#        warning("Desuet. Utiliser dpix2coo (*coeff) et dcoo2pix (/coeff)")
        return (self.fenetre[1+2*i] - self.fenetre[2*i])/self.dimensions[i]
        # Rq: une ZeroDivisionError se produit juste apr�s avoir beaucoup r�duit une fen�tre,
        # wxpython renvoit parfois (0,0) pour la taille.
        # le plus simple serait de laisser l'erreur, mais �a innonde le d�bugueur de messages... :-/

    def coeffs(self): # DESUET
#        warning("Desuet. Utiliser dpix2coo et dcoo2pix")
        return self.coeff(0), self.coeff(1)
    ## </DESUET> ##

    def txt_box(self, matplotlib_text):
        u"""Retourne l'espace (rectangulaire) occup� par le texte.

        Retourne un objet Bbox, poss�dant des attributs xmin, xmax, ymin,
        ymax, height et width. (En pixels)."""
        return matplotlib_text.get_window_extent(self.get_renderer())

    def coo2pix(self, x, y):
        u"""Convertit des coordonn�es en pixel."""
        if isinstance(x, (list, tuple)):
            x = numpy.array(x)
        if isinstance(y, (list, tuple)):
            y = numpy.array(y)
        l, h = self.dimensions
        px = l*(x - self.fenetre[0])/(self.fenetre[1] - self.fenetre[0])
        py = h*(self.fenetre[3] - y)/(self.fenetre[3] - self.fenetre[2])
        return px, py

    def pix2coo(self, px, py):
        u"""Convertit un pixel en coordonn�es."""
        if isinstance(px, (list, tuple)):
            px = numpy.array(px)
        if isinstance(py, (list, tuple)):
            py = numpy.array(py)
        l, h = self.dimensions
        x = px*(self.fenetre[1] - self.fenetre[0])/l + self.fenetre[0]
        y = py*(self.fenetre[2] - self.fenetre[3])/h + self.fenetre[3]
#        print x,  y,  -x,  -y
        return x, y

    def dcoo2pix(self, dx, dy):
        u"""Convertit un d�placement exprim� en coordonn�es en un d�placement en pixels."""
        l, h = self.dimensions
        dpx = l*dx/(self.fenetre[1] - self.fenetre[0])
        dpy = h*dy/(self.fenetre[2] - self.fenetre[3])
        return dpx, dpy

    def dpix2coo(self, dpx, dpy):
        u"""Convertit un d�placement exprim� en pixels en un d�placement exprim� en coordonn�es."""
        l, h = self.dimensions
        dx = dpx*(self.fenetre[1] - self.fenetre[0])/l
        dy = dpy*(self.fenetre[2] - self.fenetre[3])/h
        return dx, dy


    def _affiche_module(self):
        u"Affichage sp�cifique au module en cours. (� surclasser.)"
        pass

    def geler_affichage(self, geler=True, actualiser=False, seulement_en_apparence=False, sablier=False):
        u"""� utiliser au sein d'un contexte 'with':

            .. sourcecode:: python

            with self.geler_affichage():
                # some action

        Si actualiser = True, l'affichage est rafraichi au d�gel.
        Si seulement_en_apparence = True, l'affichage n'est pas gel� en interne, mais les modifications
        ne s'affichent pas � l'�cran (le gain de vitesse est alors n�gligeable, mais esth�tiquement �a �vite
        que des modifications successives apparaissent � l'�cran).

        Si sablier = True, le pointeur de la souris est remplac� temporairement par un sablier.
        """
        return GelAffichage(self, geler=geler, actualiser=actualiser, sablier=sablier)

    def _curseur(self, sablier):
        u"""Changer le curseur en sablier.

        � surclasser."""
        raise NotImplementedError

    @property
    def affichage_gele(self):
        return self._affichage_gele

    @property
    def affichage_gele_en_apparence(self):
        return self._affichage_gele_en_apparence

    def saturation(self, i):
        return self.zoom_ligne*self.coeff(i)/self.gradu[i]


#    Reglage des parametres d'affichage
##########################################
# Gestion des variables d'environnement li�es � l'affichage.
# A standardiser.


##    _liste_parametres_repere = ("quadrillages", "affiche_quadrillage", "affiche_axes",
##                                    "affiche_fleches", "repere", "gradu", "utiliser_repere",
##                                    "liste_axes", "orthonorme", "fenetre",
##                                    )


    # Parametres bool�ens g�r�s par une entr�e du menu
    for _nom_, _doc_ in (
    ('afficher_axes', u"Afficher ou non les axes."),
    ('afficher_quadrillage', u"Afficher ou non le(s) quadrillage(s)."),
    ('orthonorme', u"Afficher la figure dans un rep�re toujours orthonorm�."),
    ('afficher_objets_caches', u"Indique si les objets cach�s sont affich�s ou non."),
    ('grille_aimantee', u"Indique si les points doivent se placer sur le quadrillage."),
    ):
        exec('''@track
def gerer_parametre_%(_nom_)s(self, afficher = None):
    """%(_doc_)s"""
    if afficher is not None:
        if isinstance(afficher, bool):
            self.%(_nom_)s = afficher
        else:
            self.%(_nom_)s = not self.%(_nom_)s
        self.rafraichir_affichage()
    assert isinstance(self.%(_nom_)s, bool), '%(_nom_)s: ' + repr(self.%(_nom_)s)
    return self.%(_nom_)s''' %locals(), globals(), locals())

    # Param�tres g�r�s directement par la feuille
    for _nom_ in Feuille._parametres_repere:
        exec('''assert "%(_nom_)s" not in locals(), "Erreur: %(_nom_)s est deja defini !"
@property2
def %(_nom_)s(self, valeur = no_argument):
    if valeur is no_argument:
        return self.feuille_actuelle.%(_nom_)s
    self.feuille_actuelle.%(_nom_)s = valeur''' %locals(), globals(), locals())

    del _nom_, _doc_



#      Gestion du zoom, etc...
########################################



    def _get_fenetre(self):
        if self.orthonorme or getattr(self, 'ratio', None) is not None:
            if self.orthonorme:
                rat = 1
            else:
                rat = self.ratio # x:y -> x/y
                # ratio est le rapport "unit� en abscisse/unit� en ordonn�e"
            w, h = self.dimensions
            fenetre = self.feuille_actuelle.fenetre
            coeff0 = rat*(fenetre[1] - fenetre[0])/w
            coeff1 = (fenetre[3] - fenetre[2])/h
            xmin, xmax, ymin, ymax = fenetre
            xcoeff = (coeff1/coeff0 if coeff0 < coeff1 else 1)
            ycoeff = (1 if coeff0 < coeff1 else coeff0/coeff1)
            x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
            return x - xcoeff*rx, x + xcoeff*rx, y - ycoeff*ry, y + ycoeff*ry
        return self.feuille_actuelle.fenetre


    def _set_fenetre(self, xmin_xmax_ymin_ymax):
        self.feuille_actuelle.fenetre = xmin_xmax_ymin_ymax

    fenetre = property(_get_fenetre, _set_fenetre)

    @property
    def xmin(self):
        return self.fenetre[0]

    @property
    def xmax(self):
        return self.fenetre[1]

    @property
    def ymin(self):
        return self.fenetre[2]

    @property
    def ymax(self):
        return self.fenetre[3]

    @property
    def dimensions_fenetre(self):
        xmin, xmax, ymin, ymax = self.fenetre
        return xmax - xmin, ymax - ymin

    def synchroniser_fenetre(self):
        u"""D�tecte la fen�tre d'affichage et l'enregistre.
        Ce peut �tre utile si l'on utilise une commande de haut niveau de matplolib,
        qui calcule automatiquement la meilleure fen�tre d'affichage."""
        xmin, xmax = self.axes.viewLim.intervalx
        ymin, ymax = self.axes.viewLim.intervaly
        self.fenetre = xmin, xmax, ymin, ymax

    def zoomer(self, coeff):
        xmin, xmax, ymin, ymax = self.fenetre
        x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
        self.fenetre = x - rx/coeff, x + rx/coeff, y - ry/coeff, y + ry/coeff

    def zoom_in(self, event = None):
        self.zoomer(param.zoom_in)

    def zoom_out(self, event = None):
        self.zoomer(param.zoom_out)





    @track
    def zoom_auto(self, event = None):
        fenetre_initiale = a = self.fenetre
        compteur = 0
        condition = True
        while condition:
            self.graph._regler_fenetre()
            compteur += 1
            self._zoom_auto()
            # � cause du texte dont la taille est ind�pendante de l'�chelle, les calculs sont fauss�s.
            # Mais en r�it�rant le proc�d�, l'affichage converge rapidement (A OPTIMISER ?).
            b = a
            a = self.fenetre
            erreur_x = abs(a[0] - b[0]) + abs(a[1] - b[1])
            erreur_y = abs(a[2] - b[2]) + abs(a[3] - b[3])
            # l'erreur doit �tre inf�rieure � 1 pixel:
            condition = erreur_x/self.coeff(0) > 1 or erreur_y/self.coeff(1) > 1
            if compteur > 25:
                self.message(u"�chec du zoom automatique.")
                self.fenetre = fenetre_initiale
                break

    def _zoom_auto(self):
        objets = self.feuille_actuelle.liste_objets(objets_caches=False,
                                                    etiquettes=True)
        xxyy = zip(*(obj.espace_vital for obj in objets if obj.espace_vital))
        print 'xxyy', xxyy

        if xxyy:
            def num_only(item):
                # 'None' indique que l'objet ne fournit pas d'indication de dimension
                # pour les abscisses ou pour les ordonn�es.
                return not(item is None or isinf(item) or isnan(item))

            noms = ('xmin', 'xmax', 'ymin', 'ymax')
            # Listes brutes des extremas obtenus pour chaque objet.
            listes_extremas = zip(noms, xxyy, self.fenetre)
            # Synth�se : valeurs retenues pour l'ensemble de la feuille.
            extremas = {}
            # 'False' si le param�tre ne doit *pas* �tre modifi�.
            ajuster = {'xmin': True, 'xmax': True, 'ymin': True, 'ymax': True}

            for nom, liste, defaut in listes_extremas:
                liste_filtree = filter(num_only, liste)
                if param.debug:
                    print 'zoom_auto - valeurs obtenues:', nom, liste_filtree
                if liste_filtree:
                    if nom.endswith('min'):
                        extremas[nom] = min(liste_filtree)
                    else:
                        extremas[nom] = max(liste_filtree)
                else:
                    extremas[nom] = defaut
                    ajuster[nom] = False

            if param.debug:
                print 'zoom_auto - propositions:', extremas

            for axe in 'xy':
                nom_min = axe + 'min'
                nom_max = axe + 'max'
                ecart = extremas[nom_max] - extremas[nom_min]
                assert ecart > 0
                # Des valeurs trop proches pour xmin et xmax (ou pour ymin et ymax)
                # risqueraient de faire planter l'affichage.
                if ecart < 100*param.tolerance:
                    rayon = .5*(getattr(self, nom_max) - getattr(self, nom_min))
                    extremas[nom_min] -= rayon
                    extremas[nom_max] += rayon
                else:
                    # On pr�voit 5% de marge (de mani�re � ce qu'un point
                    # ne se retrouve pas coll� au bord de la fen�tre par exemple).
                    if ajuster[nom_min]:
                        extremas[nom_min] -= 0.05*ecart
                    if ajuster[nom_max]:
                        extremas[nom_max] += 0.05*ecart

            self.fenetre = tuple(extremas[nom] for nom in noms)
            if param.debug:
                print "ZOOM AUTO :", self.fenetre


    @track
    def orthonormer(self, event = None, mode = 1):
        u"""
        mode 0 : on orthonormalise le rep�re en restreignant la vue.
        mode 1 : on orthonormalise le rep�re en �largissant la vue."""
        if mode:
            xcoeff = self.coeff(1)/self.coeff(0) if self.coeff(0) < self.coeff(1) else 1
            ycoeff = 1 if self.coeff(0) < self.coeff(1) else self.coeff(0)/self.coeff(1)
        else:
            xcoeff = self.coeff(1)/self.coeff(0) if self.coeff(0) > self.coeff(1) else 1
            ycoeff = 1 if self.coeff(0) > self.coeff(1) else self.coeff(0)/self.coeff(1)
        xmin, xmax, ymin, ymax = self.fenetre
        x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
        self.fenetre = x - xcoeff*rx, x + xcoeff*rx, y - ycoeff*ry, y + ycoeff*ry

    # < Zooms concernant uniquement la taille des objets >

    def zoom_text(self, event = None, valeur = 100):
        self.zoom_texte = valeur/100
##        self.rafraichir_affichage()

    def zoom_line(self, event = None, valeur = 100):
        self.zoom_ligne = valeur/100
##        self.rafraichir_affichage()

    def zoom_normal(self, event = None):
        self.zoom_texte = 1
        self.zoom_ligne = 1
##        self.rafraichir_affichage()

    def zoom_large(self, event = None):
        self.zoom_texte = 1.2
        self.zoom_ligne = 1.4
##        self.rafraichir_affichage()

    def zoom_videoprojecteur(self, event = None):
        self.zoom_texte = 1.6
        self.zoom_ligne = 2
##        self.rafraichir_affichage()

    def zoom_videoprojecteur_large(self, event = None):
        self.zoom_texte = 2.2
        self.zoom_ligne = 3
##        self.rafraichir_affichage()

    # </ Fin des zooms sur la taille des objets >


    @track
    def repere_Oij(self, event = None):
        self.repere = ('O', 'i', 'j')
        self.gerer_parametre_afficher_axes(True)

    @track
    def repere_OIJ(self, event = None):
        self.repere = ('O', 'I', 'J')
        self.gerer_parametre_afficher_axes(True)

    @track
    def repere_011(self, event = None):
        ux, uy = self.gradu
        self.repere = ('0', str(ux), str(uy))
        self.gerer_parametre_afficher_axes(True)


    @track
    def quadrillage_millimetre(self, event = None):
        self.quadrillages = (  ((1, 1), ':', 1, 'k'),
                            ((0.5, 0.5), '-', 0.25, 'darkgray'),
                            ((0.1, 0.1), '-', 0.1, 'gray'),
                            )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_millimetre_colore(self, event = None, couleur = None):
        if couleur is None:
            couleur = self.couleur_papier_millimetre
        self.quadrillages = (  ((1, 1), ':', 1, couleur),
                                    ((0.5, 0.5), '-', 0.25, couleur),
                                    ((0.1, 0.1), '-', 0.1, couleur),
                                    )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_demigraduation(self, event = None):
        ux, uy = self.gradu
        self.quadrillages = (  ((ux, uy), ':', 1, 'k'),
                                    ((ux/2, uy/2), '-', 0.25, 'darkgray'),
                                    )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_demigraduation_colore(self, event = None, couleur = None):
        ux, uy = self.gradu
        if couleur is None:
            couleur = self.couleur_papier_millimetre
        self.quadrillages = (  ((ux, uy), ':', 1, couleur),
                                    ((ux/2, uy/2), '-', 0.25, couleur),
                                    )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_defaut(self, event = None):
        self.quadrillages = self.param("quadrillages", defaut = True)
        self.gerer_parametre_afficher_quadrillage(True)


# S�lection d'une zone
######################

    def _rectangle_selection(self, debut, pixel, linestyle='-', facecolor='y', edgecolor='y', respect_ratio=False):
        x, y = pixel
        xmax, ymax = self.dimensions
        # Pour des questions d'arrondi lors de la conversion pixel -> coordonn�e,
        # on met 0.1 au lieu de 0 comme valeur minimale en pixel (0+ en fait).
        x = max(min(x, xmax - 1), 0.1)
        y = max(min(y, ymax - 1), 0.1)
        x1, y1 = self.pix2coo(x, y)
        x0, y0 = (debut if debut else (x1, y1))
        if respect_ratio and self.orthonorme or getattr(self, 'ratio', None) is not None:
            rymax = (ymax if self.orthonorme else ymax*self.ratio)
            if rymax*abs(x0 - x1) > xmax*abs(y0 - y1):
                y1 = y0 + rymax/xmax*abs(x0 - x1)*cmp(y1, y0)
            else:
                x1 = x0 + xmax/rymax*abs(y0 - y1)*cmp(x1, x0)

        # Exceptionnellement, il faut ici effacer manuellement le graphisme.
        # En effet, il n'est pas garanti qu'il y ait un rafraichissement
        # de l'affichage � chaque fois que le rectangle de s�lection change.
        # Si l'on n'efface pas manuellement l'affichage, on risque donc d'avoir
        # deux rectangles de s�lection diff�rents affich�s simultan�ment.
        self.graph._effacer_artistes()
        self.dessiner_polygone([x0, x0, x1, x1], [y0, y1, y1, y0], facecolor=facecolor, edgecolor=edgecolor, alpha=.1)
        self.dessiner_ligne([x0, x0, x1, x1, x0], [y0, y1, y1, y0, y0], edgecolor, linestyle=linestyle, alpha=1)

        self.rafraichir_affichage(dessin_temporaire = True) # pour ne pas tout rafraichir
        return (x0, y0), (x1, y1)


    def gestion_zoombox(self, pixel):
        self.debut_zoom, self.fin_zoom = self._rectangle_selection(
                self.debut_zoom, pixel, facecolor='c', edgecolor='c',
                respect_ratio=True)

    def selection_zone(self, pixel):
        self.debut_select, self.fin_select = self._rectangle_selection(
                self.debut_select, pixel, facecolor='y', edgecolor='g',
                linestyle=':')


# Evenements concernant directement la feuille
##############################################

    def coder(self, event):
        self.executer(u"coder()")

    def decoder(self, event):
        self.executer(u"effacer_codage()")

    def nettoyer_feuille(self, event):
        self.executer(u"nettoyer()")

    def effacer_traces(self, event):
        self.feuille_actuelle.effacer_traces()

    def executer(self, commande, parser = False):
        u"""Ex�cute une commande dans la feuille.

        NB: le parser n'est *PAS* activ� par d�faut, par souci de rapidit�."""
        self.feuille_actuelle.executer(commande, parser = parser)


#    Gestion de l'affichage
#################################




    def rafraichir_affichage(self, dessin_temporaire = False, rafraichir_axes = None):
        if rafraichir_axes is not None:
            self.feuille_actuelle._repere_modifie = rafraichir_axes
        self.feuille_actuelle.affichage_perime()
        self._dessin_temporaire = dessin_temporaire

    def _actualiser_si_necessaire(self, event = None, _n=[0]):
#        _n[0] += 1
        if self.feuille_actuelle._affichage_a_actualiser:
#            print _n[0], u"Affichage actualis�."
            self._actualiser()

    def _actualiser(self, _n = [0]):
        # Le code suivant est � activer uniquement pour le d�bogage de l'affichage:
        # <DEBUG>
        if param.debug:
            s = "Actualisation"
            if self.feuille_actuelle._repere_modifie:
                s += " complete"
            print s + str(_n) + ": " + self.parent.titre
            _n[0] += 1
        # </DEBUG>
        if 0 in self.dimensions:
            # Fen�tre pas encore affich�e (initialisation du programme).
            if param.debug:
                print u"Actualisation diff�r�e (fen�tre non charg�e : " + self.parent.titre + ")"
            return
        try:
            self.graph.dessiner(dessin_temporaire = self._dessin_temporaire,
                        rafraichir_axes = self.feuille_actuelle._repere_modifie)
        except Exception:
            # Ne pas bloquer le logiciel par des rafraichissements successifs en cas de probl�me.
            print_error()
        self.feuille_actuelle._repere_modifie = False
        self.feuille_actuelle._affichage_a_actualiser = False
        self._dessin_temporaire = False



    def param(self, key, **kw):
        return getattr(param, key)
