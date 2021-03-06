# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from pytest import XFAIL

from tools.testlib import assertRaises, assertAlmostEqual

from wxgeometrie.mathlib.interprete import Interprete
from sympy import S

VERBOSE = False


def assert_resultat(s, resultat, latex = None, **parametres):
    i = Interprete(verbose=VERBOSE, **parametres)
    r, l = i.evaluer(s)
    if r != resultat:
        i = Interprete(verbose = True, **parametres)
        r, l = i.evaluer(s)
        print "ERREUR (" + s + "): ", r, " != ",  resultat
    assert(r == resultat)
    if latex is not None:
        latex = "$" + latex + "$"
        if l != latex:
            print "ERREUR (" + s + "): ", l, " != ",  latex
        assert(l == latex)

def assert_resoudre(s, *args, **kw):
    assert_resultat("resoudre(" + s + ")", *args, **kw)

def assert_approche(s, resultat, latex = None, **parametres):
    assert_resultat(s, resultat, latex, calcul_exact = False, **parametres)

def assertEqual(x, y):
    if x != y:
        print "ERREUR:", repr(x), "!=", repr(y)
    assert(x == y)

def assertDernier(i, s):
    assertEqual(str(i.derniers_resultats[-1]), s)

def test_exemples_de_base():
    # Nombres
    assert_resultat('2+2', '4', '4')
    # Symboles
    assert_resultat('pi+1+2pi', '1 + 3 pi', '1 + 3 \\pi')
    assert_resultat('oo+5*oo', '+oo')
    assert_resultat('i**2-i', '-1 - i', '-1 - \\mathrm{i}')
    assert_resultat('5e-3', '-3 + 5 e', '-3 + 5 \\mathrm{e}')
    # Analyse
    assert_resultat('limite(x^2-x+3, +oo)', '+oo', '+\\infty')
    assert_resultat('derive(x^2+2x-3)', '2 x + 2', '2 x + 2')
    assert_resultat('integre(2x+7)', 'x^2 + 7 x', 'x^{2} + 7 x')
    assert_resultat('integre(x+1, (x, -1, 1))', '2', '2')
    assert_resultat('integre(x+1, x, -1, 1)', '2', '2')
    assert_resultat('taylor(sin x, x, 0, 4)', 'x - x^3/6 + O(x^4)', \
                                    'x - \\frac{1}{6} x^{3} + \\mathcal{O}\\left(x^{4}\\right)')
    assert_resultat('cos x>>taylor', \
                                    '1 - x^2/2 + x^4/24 + O(x^5)', \
                                    '1 - \\frac{1}{2} x^{2} + \\frac{1}{24} x^{4} + \\mathcal{O}\\left(x^{5}\\right)')
    # Alg�bre
    assert_resultat('developpe((x-3)(x+7)(2y+x+5))', \
                                    'x^3 + 2 x^2 y + 9 x^2 + 8 x y - x - 42 y - 105', \
                                    'x^{3} + 2 x^{2} y + 9 x^{2} + 8 x y - x - 42 y - 105')
    assert_resultat('factorise(x^2-7x+3)', \
                                    '(x - 7/2 - sqrt(37)/2)(x - 7/2 + sqrt(37)/2)',
                                    r'\left(x - \frac{7}{2} - \frac{1}{2} \sqrt{37}\right) \left(x - \frac{7}{2} + \frac{1}{2} \sqrt{37}\right)')
    assert_resultat('factorise(x^2+x)', 'x(x + 1)',  'x \\left(x + 1\\right)')
    assert_resultat('factor(exp(x)x^2+5/2x*exp(x)+exp(x))', '(x + 1/2)(x + 2)exp(x)')
    ##assert_resultat('factor(exp(x)x^2+2.5x*exp(x)+exp(x))', '(x + 0,5)(x + 2)exp(x)')
    assert_resultat('factor(exp(x)x^2+2.5x*exp(x)+exp(x))', '(x + 1/2)(x + 2)exp(x)')
    assert_resultat('factorise(exp(2x)*x^2+x*exp(x))', \
                                    'x(x exp(x) + 1)exp(x)',  \
                                    'x \\left(x \\mathrm{e}^{x} + 1\\right) \\mathrm{e}^{x}')
    assert_resultat('factorise(x^2+7x+53)', 'x^2 + 7 x + 53', 'x^{2} + 7 x + 53')
    assert_resultat('factor(exp(x)x^2+2x*exp(x)+exp(x))', \
                                    '(x + 1)^2 exp(x)', \
                                    '\left(x + 1\\right)^{2} \\mathrm{e}^{x}')
    assert_resultat('cfactorise(x^2+7x+53)', \
            '(x + 7/2 - sqrt(163)i/2)(x + 7/2 + sqrt(163)i/2)', \
            r'\left(x + \frac{7}{2} - \frac{1}{2} \sqrt{163} \mathrm{i}\right) '
            r'\left(x + \frac{7}{2} + \frac{1}{2} \sqrt{163} \mathrm{i}\right)')
    assert_resultat('evalue(pi-1)', '2,14159265358979324', '2,14159265358979324')
    assert_resultat('somme(x^2, (x, 1, 7))', '140', '140')
    assert_resultat('somme(x^2, x, 1, 7)', '140', '140')
    assert_resultat('product(x^2, (x, 1, 7))', '25401600', '25401600')
    assert_resultat('product(x^2;x;1;7)', '25401600', '25401600')
    assert_resultat('limit(x^2-x, oo)', '+oo', '+\infty')
    assert_resultat('abs(pi-5)', '-pi + 5', r'- \pi + 5')
    assert_resultat('abs(x-5)', 'abs(x - 5)', r'\left|{x - 5}\right|')
    assert_resultat('i(1+i)', r'-1 + i',  r'-1 + \mathrm{i}')
    assert_resultat('i sqrt(3)', r'sqrt(3)i',  r'\sqrt{3} \mathrm{i}')
    assert_resultat('pi sqrt(3)', r'sqrt(3)pi',  r'\sqrt{3} \pi')
    assert_resultat('sqrt(1+e)', r'sqrt(1 + e)',  r'\sqrt{1 + \mathrm{e}}')
    assert_resultat('(5-2i)(5+2i)', r'29',  r'29')
    assert_resultat('resous(2x=1)', r'{1/2}',  r'\left\{\frac{1}{2}\right\}')
    assert_resultat('jhms(250000)', r'2 j 21 h 26 min 40 s',
                    r'2 \mathrm{j}\, 21 \mathrm{h}\, 26 \mathrm{min}\, 40 \mathrm{s}')
    assert_resultat(r'pi\approx', r'3,14159265358979324',  r'3,14159265358979324',
                    formatage_LaTeX=True)
    assert_resultat('rassemble(1/x+1/(x*(x+1)))', '(x + 2)/(x^2 + x)', r'\frac{x + 2}{x^{2} + x}')
    assert_resultat('factorise(-2 exp(-x) - (3 - 2 x)exp(-x))', '(2 x - 5)exp(-x)',
                    r'\left(2 x - 5\right) \mathrm{e}^{- x}')
    assert_resultat('-x^2+2x-3>>factor', '-x^2 + 2 x - 3')
    assert_resultat('abs(-24/5 - 2 i/5)', '2 sqrt(145)/5')
    assert_resultat('+oo - 2,5', '+oo', r'+\infty')

def test_ecriture_decimale_periodique():
    assert_resultat('0,[3]', '1/3', r'\frac{1}{3}')
    assert_resultat('0,1783[3]', '107/600', r'\frac{107}{600}')

@XFAIL
def test_resolution_complexe():
    assert_resultat('resoudre(2+\i=\dfrac{2\i z}{z-1})', '3/5 + 4*i/5',
                                        r'\frac{3}{5} + \frac{4}{5} \mathrm{i}')

def test_fonctions_avances():
    pass

def test_frac():
    assert_resultat('frac(0,25)', '1/4', r'\frac{1}{4}')
    assert_resultat('frac(0,333333333333333)', '1/3', r'\frac{1}{3}')

def test_resoudre():
    assert_resoudre('2x+3>5x-4 et 3x+1>=4x-4', r']-oo ; 7/3[')
    assert_resoudre('2=-a+b et -1=3a+b', r'{a: -3/4 ; b: 5/4}')
    assert_resoudre(r'3-x\ge 1+2x\\\text{et}\\4x<2+10x', ']-1/3 ; 2/3]',
                    r'\left]- \frac{1}{3};\frac{2}{3}\right]', formatage_LaTeX=True)
    assert_resoudre('2exp(x)>3', ']-ln(2) + ln(3) ; +oo[')
    #TODO: Rassembler les ln: ]ln(3/2);+oo[
    assert_resoudre('x^3-30x^2+112=0', '{-6 sqrt(7) + 14 ; 2 ; 14 + 6 sqrt(7)}',
                r'\left\{- 6 \sqrt{7} + 14\,;\, 2\,;\, 14 + 6 \sqrt{7}\right\}')
    # assert_resoudre(r'ln(x^2)-ln(x+1)>1', ']-1;e/2 - sqrt(4 e + exp(2))/2[U]e/2 + sqrt(4 e + exp(2))/2;+oo[')
    assert_resoudre(r'ln(x^2)-ln(x+1)>1', ']-1 ; -sqrt(e + 4)exp(1/2)/2 + e/2[U]e/2 + sqrt(e + 4)exp(1/2)/2 ; +oo[')
    assert_resoudre('0.5 exp(-0.5 x + 0.4)=0.5', '{4/5}')

#TODO: @SLOW wrapper should be defined, and the test only run in some circonstances
# (for ex, a 'slow' keyword in tools/tests.py arguments)
def test_longs():
    # NB: Test tr�s long (15-20 secondes) !
    pass

def test_approches():
    assert_approche('pi-1', '2,14159265358979324', '2,14159265358979324')
    assert_approche('factor(x^2+2.5x+1)', '(x + 0,5)(x + 2)')
    assert_approche('factor(exp(x)x^2+2.5x*exp(x)+exp(x))', '(x + 0,5)(x + 2)exp(x)')
    assert_approche('ln(2.5)', '0,916290731874155065')
    assert_approche('ln(2,5)', '0,916290731874155065')
    assert_approche('resoudre(x^3-30x^2+112=0)',
                    '{-1,87450786638754354 ; 2 ; 29,8745078663875435}',
                    r'\left\{-1,87450786638754354\,;\, 2\,;\, 29,8745078663875435\right\}')


def test_session():
    i = Interprete(verbose=VERBOSE)
    i.evaluer("1+7")
    i.evaluer("x-3")
    i.evaluer("ans()+ans(1)")
    assertDernier(i, "x + 5")
    i.evaluer("f(x, y, z)=2x+3y-z")
    i.evaluer("f(-1, 5, a)")
    assertDernier(i, "-a + 13")
    i.evaluer("f(x)=x^2-7x+3")
    i.evaluer("f'(x)")
    assertDernier(i, "2*x - 7")

    # Noms r�serv�s
    assertRaises(NameError, i.evaluer, "e=3")
    assertRaises(NameError, i.evaluer, "pi=3")
    assertRaises(NameError, i.evaluer, "i=3")
    assertRaises(NameError, i.evaluer, "oo=3")
    assertRaises(NameError, i.evaluer, "factorise=3")
    # Etc.

    # Test des g�n�rateurs
    i.evaluer('f(x)=x+3')
    i.evaluer('[f(j) for j in range(1, 11)]')
    assertDernier(i, '[4, 5, 6, 7, 8, 9, 10, 11, 12, 13]')
    i.evaluer('tuple(i for i in range(7))')
    assertDernier(i, '(0, 1, 2, 3, 4, 5, 6)')
    i.evaluer('[j for j in range(7)]')
    assertDernier(i, '[0, 1, 2, 3, 4, 5, 6]')

    # _11 is an alias for ans(11)
    i.evaluer('_11 == _')
    assertDernier(i, 'True')
    i.evaluer('_7')
    assertDernier(i, "2*x - 7")
    # _ is an alias for ans(-1), __ is an alias for ans(-2), and so on.
    i.evaluer('_ == -7 + 2*x')
    assertDernier(i, 'True')
    i.evaluer('__')
    assertDernier(i, "2*x - 7")
    i.evaluer('______') # ans(-6)
    assertDernier(i, '(0, 1, 2, 3, 4, 5, 6)')

    # Affichage des cha�nes en mode text (et non math)
    i.evaluer('"Bonjour !"')
    assert i.latex_dernier_resultat == u'\u201CBonjour !\u201D'

    # Virgule comme s�parateur d�cimal
    resultat, latex = i.evaluer('1,2')
    assert resultat == '1,2'
    assertAlmostEqual(i.derniers_resultats[-1], 1.2)
    # Avec un espace, c'est une liste (tuple) par contre
    resultat, latex = i.evaluer('1, 2')
    assertEqual(resultat, '(1 ; 2)')
    resultat, latex = i.evaluer('"1.2"')
    assert resultat == '"1.2"'
    i.evaluer('?aide')
    i.evaluer('aide?')
    i.evaluer('aide(aide)')
    msg_aide = u"\n== Aide sur aide ==\nRetourne (si possible) de l'aide sur la fonction saisie."
    resultats = i.derniers_resultats
    assert resultats[-3:] == [msg_aide, msg_aide, msg_aide]

    # LaTeX
    latex = i.evaluer("gamma(x)")[1]
    assertEqual(latex, r'$\Gamma\left(x\right)$')

    # V�rifier qu'on ait bien ln(x) et non log(x) qui s'affiche
    resultat, latex = i.evaluer('f(x)=(ln(x)+5)**2')
    assertEqual(resultat, 'x -> (ln(x) + 5)^2')
    assertEqual(latex, r'$x\mapsto \left(\ln(x) + 5\right)^{2}$')


def test_issue_sialle1():
    # Probl�me : Si on tape 1/(1-sqrt(2)), on obtient le r�sultat 1/-sqrt(2)+1,
    # qui est faux (il manque les parenth�ses...).
    assert_resultat("1/(1-sqrt(2))", "1/(-sqrt(2) + 1)")

def test_1_pas_en_facteur():
    assert_resultat("together(1/x-.5)", "-(x - 2)/(2 x)", r"- \frac{x - 2}{2 x}")
    ##assert_resultat("together(1/x-.5)", "-0,5(x - 2)/x", r"- 0,5 \frac{x - 2}{x}")

def test_issue_129():
    assert_resultat('"x(x+1)" + """x!"""', '"x(x+1)x!"')
    assert_resultat(r'""" "" """ + " \"\"\" "', r'" \"\"  \"\"\" "')

def test_issue_185():
    i = Interprete(verbose=VERBOSE)
    i.evaluer("a=1+I")
    i.evaluer("a z")
    assertDernier(i, 'z*(1 + I)')


def test_issue_206():
    i = Interprete(verbose=VERBOSE)
    etat_interne = \
u"""_ = 0

@derniers_resultats = [
    're(x)',
    ]"""
    i.load_state(etat_interne)
    i.evaluer("-1+\i\sqrt{3}")
    assertDernier(i, '-1 + sqrt(3)*I')
    i.evaluer('-x**2 + 2*x - 3>>factor')
    assertDernier(i, '-x**2 + 2*x - 3')


def test_issue_206_bis():
    i = Interprete(verbose=VERBOSE)
    etat_interne = \
u"""_ = 0

@derniers_resultats = [
    'Abs(x)',
    ]"""
    i.load_state(etat_interne)
    i.evaluer('abs(-24/5 - 2 i/5)')
    assertDernier(i, '2*sqrt(145)/5')


def test_issue_206_ter():
    i = Interprete(verbose=VERBOSE)
    etat_interne = \
u"""_ = 0

@derniers_resultats = [
    'atan2(x, y)',
    ]"""
    i.load_state(etat_interne)
    i.evaluer('ln(9)-2ln(3)')
    assertDernier(i, '0')


def test_systeme():
    i = Interprete(verbose=VERBOSE)
    i.evaluer("g(x)=a x^3+b x^2 + c x + d")
    i.evaluer("resoudre(g(-3)=2 et g(1)=6 et g(5)=3 et g'(1)=0)")
    res = i.derniers_resultats[-1]
    assert isinstance(res, dict)
    assertEqual(res, {S('a'): S(1)/128, S('b'): -S(31)/128, S('c'): S(59)/128, S('d'): S(739)/128})


def test_ecriture_fraction_decimaux():
    # En interne, les d�cimaux sont remplac�s par des fractions.
    # Cela �vite la perte de pr�cision inh�rente aux calculs avec flottants.
    # Ce remplacement doit �tre autant que possible transparent pour l'utilisateur,
    # qui, s'il rentre des d�cimaux, doit voir des d�cimaux s'afficher.
    i = Interprete(verbose=VERBOSE)
    r, l = i.evaluer('0,3+0,8')
    assertEqual(r, '1,1')
    r, l = i.evaluer('a=1,7')
    assertEqual(r, '1,7')
    r, l = i.evaluer("f(x)=0,3x+0,7")
    assertEqual(r, 'x -> 0,3 x + 0,7')
    # Le calcul suivant ne fonctionne pas en utilisant en interne des flottants
    # (le coefficient devant le x^2 n'est pas tout � fait nul lorsqu'on d�veloppe).
    # En utilisant en interne des fractions, par contre, le calcul est exact.
    i.evaluer("C(x)=0,003 x^2 + 60 x + 48000")
    r, l = i.evaluer("expand(C(x+1)-C(x))")
    assertEqual(r, '0,006 x + 60,003')
    r, l = i.evaluer('frac(0,5)')
    assertEqual(r, '1/2')
    r, l = i.evaluer('frac(0,166666666666666667)')
    assertEqual(r, '1/6')
    r, l = i.evaluer('frac(0,5x+0.3333333333333333)')
    assertEqual(r, 'x/2 + 1/3')


def test_issue_258():
    # Issue: "Le mode approch� ne fonctionne pas pour une liste."
    i = Interprete(verbose=VERBOSE)
    i.evaluer("v(p,n) = (p-1.96*sqrt(p*(1-p))/sqrt(n), p+1.96*sqrt(p*(1-p))/sqrt(n))")
    r, l = i.evaluer("v(0.28, 50)", calcul_exact=False)
    assertEqual(r, "(0,155543858327521659 ; 0,404456141672478341)")
    assertEqual(l, r"$\left(0,155543858327521659;\,0,404456141672478341\right)$")


def test_issue_129():
    assert_resultat("'1.2345'", '"1.2345"')
    assert_resultat("'x(x+1)'", '"x(x+1)"')


def test_issue_263():
    i = Interprete(verbose=VERBOSE)
    i.evaluer("A = mat([[1;2];[3;4]])")
    i.evaluer("B = mat(2)")
    i.evaluer("C = A*B")
    assert 'C' in i.vars()
    r, l = i.evaluer("C")
    assertEqual(r, "[1 ; 2]\n[3 ; 4]")
    etat_interne = i.save_state()
    i.clear_state()
    assert 'C' not in i.vars()
    i.load_state(etat_interne)
    assert 'C' in i.vars()
    r, l = i.evaluer("C")
    assertEqual(r, "[1 ; 2]\n[3 ; 4]")
    i.evaluer("A=[[0,1 ; 0,8]; [0,5; 0,5]]")
    r, l = i.evaluer("[[0,3 ; 0,4]]*A")
    assertEqual(r, "[23/100 ; 11/25]")
    # ou encore [0,23 ; 0,44]
    assertEqual(l, r"$\begin{pmatrix}0,23 & 0,44\end{pmatrix}$")



def test_proba_stats_basic_API():
    assert_resultat("inv_normal(.975)", "1,95996398612019")
    assert_resultat("normal(-1.96, 1.96)", "0,950004209703559")
    assert_resultat("normal(-1, 5, 7, 4)", "0,285787406777808")
    assert_resultat("normal(5, oo, 5, 3)", "0,5")
    assert_resultat("normal(-oo, 5, 5, 3)", "0,5")
    assert_resultat("normal(-oo, oo, 5, 3)", "1")
    assert_resultat("binomial(2, 5, 7, 0.3)", "0,666792")
    assert_resultat("fluctu(0.54, 150)", "(0,460239799398447 ; 0,619760200601553)")
    assert_resultat("confiance(0.27, 800)", "(0,234644660940673 ; 0,305355339059327)")


@XFAIL
def test_proba_stats_advanced_API():
    r, l = i.evaluer('X = normal()')
    r, l = i.evaluer('P(-1 < X < 1)')
    r, l = i.evaluer('P(X >= 2)')
    r, l = i.evaluer('P(X = 2)')