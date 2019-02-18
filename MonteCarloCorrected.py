import pandas as pd
import numpy as np
import random
import time

data = pd.read_csv('C:\\Users\\Martin Wolff\\Downloads\\Experiment.csv')

kilometer_aktuell = 0
kilometer_maximal = 250
laderate_maximal = 25

def draw():
    index = int(2965*random.random())
    drive_sample = data.iat[index, 0]
    departure_sample = data.iat[index, 1]
    return drive_sample, departure_sample

# Der Nutzer gibt keine Ladeflexibilität frei: er lädt mit maximaler Laderate bis die Batterie aufgeladen ist
def calc_ladedauer_maximal(standdauer):
    return min(standdauer, (kilometer_maximal-kilometer_aktuell)/laderate_maximal)

# Berechnet wie lange es dauert die Mindestreichweite sofort aufzuladen. Falls die Zeit nicht ausreicht wird die vom
# Nutzer spezifizierte Standdauer zurückgegeben
def calc_mindestreichweite_sofort_dauer(standdauer, mindestreichweite_sofort):
    return min(standdauer, (mindestreichweite_sofort-kilometer_aktuell)/laderate_maximal)

# Berechnet wie lange es dauert die Mindestreichweite sofort aufzuladen. Überprüft allerdings ob die vom System gezogene
# Zeit ausreicht die Mindestreichweite sofort aufzuladen.  Falls die Zeit nicht ausreicht wird die vom System
# spezifizierte Standdauer zurückgegeben
def calc_mindestreichweite_sofort_dauer_drawn(abfahrt, mindestreichweite_sofort):
    return min(abfahrt, (mindestreichweite_sofort-kilometer_aktuell)/laderate_maximal)

# Berechnet wie lange es dauert mit der maximaleln Laderate die restlichen Kilometer aufzuladen
def calc_mindestreichweite_spaeter_dauer(mindestreichweite_sofort, mindestreichweite_spaeter):
    return max(0, (mindestreichweite_spaeter-mindestreichweite_sofort)/laderate_maximal)

# Berechnet mit welcher Laderate nach Erreichen der Mindestreichweite sofort geladen werden muss um die
# Mindestreichweite später zu laden
def calc_gewichtungsfaktor_zaehler(mindestreichweite_sofort, mindestreichweite_spaeter, standdauer,
                                   mindestreichweite_sofort_dauer):
    return max(0, max(0, mindestreichweite_spaeter-mindestreichweite_sofort) /
               (standdauer-mindestreichweite_sofort_dauer))

# Berechnet ob die maximal verfügbare Laderate ausreicht um die Mindestreichweite später nach Erreichen der
# Mindestreichweite sofort innerhalb der Standdauer zu laden
def calc_gewichtungsfaktor(gewichtungsfaktor_zaehler):
    return gewichtungsfaktor_zaehler/laderate_maximal


def calc_ladeflaexibilitaet(mindestreichweite_sofort_dauer, mindestreichweite_spaeter_dauer, gewichtungsfaktor,
                            ladedauer_maximal):
    return round((1 - (mindestreichweite_sofort_dauer + gewichtungsfaktor * mindestreichweite_spaeter_dauer)
                  / ladedauer_maximal) * 100, 0)


def charge_up(mindestreichweite_sofort, mindestreichweite_spaeter, standdauer, abfahrt, mindestreichweite_sofort_dauer,
              mindestreichweite_sofort_dauer_drawn):
    # Erst muss ausgerechnet werden wie lange es dauert die gewünschte Mindestreichweite sofort aufzuladen. Sollte die Zeit nicht ausreichen wird die gewünschte Abfahrt genommen
    # mindestreichweite_sofort_dauer = min(self.gewuenschte_abfahrt, (self.mindestreichweite_sofort - Constants.aktuell_kilometer) / Constants.max_laderate)
    # dieser Block ist neu:
    if abfahrt >= standdauer:
        # Die gewünschte Abfahrt ist kleiner gleich der gezogenen Abfahrt, der Ladevorgang kann also wie geplant vorgenommen werden
        if mindestreichweite_sofort_dauer == standdauer:
            # Die gewünschte Mindestreichweite sofort aufzuladen dauert länger oder genauso lange wie das Auto steht. Es wird daher die gesamte Standzeit mit maximaler Laderate geladen. Die Ladeflexibilität sollte bei diesem Fall bei 0 liegen.
            return round(kilometer_aktuell + (standdauer*laderate_maximal), 2)
        else:
            # Die gewünschte Mindestreichweite sofort aufzuladen nimmt nicht die gesamte Standdauer in Anspruch
            if mindestreichweite_sofort >= mindestreichweite_spaeter:
                # Erst der einfache Fall: die geforderte Mindestreichweite sofort ist größer als die geforderte Mindestreichweite später. Es werden also einfach so viele Kilometer geladen wie in der Mindestreichweite sofort gefordert
                return mindestreichweite_sofort
            else:
                # Jetzt der etwas kompliziertere Fall: Die Mindestreichweite sofort wird aufgeladen, aber die geforderte Mindestreichweite später ist größer. Nach Erreichen der Mindestreichweite sofort wird also noch mit einer verringerten Laderate geladen.
                gewichtungsfaktor_zaehler = calc_gewichtungsfaktor_zaehler(mindestreichweite_sofort,
                                                                           mindestreichweite_spaeter, standdauer,
                                                                           mindestreichweite_sofort_dauer)# wir wissen, dass die mindestreichweite später größer ist als die mindestreichweite sofort, muss daher größer 0 sein
                # Nenner kann nicht 0 werden, da bereits festgestellt wurde, dass die Mindestreichweite sofort aufzuladen nicht die gesamte Standdauer benötigt
                # Insgesamt (die Variable die hier mit gewichtungsfaktor_zaehler bezeichnet wird) wird hier also berechnet wie viele Kilometer pro Stunde geladen werden müssen um die Mindestreichweite später vor Ende der Standzeit zu erreichen
                gewichtungsfaktor = calc_gewichtungsfaktor(gewichtungsfaktor_zaehler)
                # Der Gewichtungsfaktor überprüft ob die maximale Laderate ausreicht um die noch zu ladenden Kilometer aufzuladen. Ist er > 1 reicht die Zeit nicht aus. Es muss also die gesamte restliche Zeit mit maximaler Laderate geladen werden
                if gewichtungsfaktor <= 1:
                    # Erst der einfache Fall: der gewichtungsfaktor ist kleiner oder gleich 1: damit reicht die Zeit aus um das Autoa auf die geforderte Mindestreichweite später zu laden (auch wenn es sein kann, dass der Gewichtungsfaktor genau 1 ist und somit die gesamte Zeit mit maximaler Laderate aufgeladen werden muss - die Ladeflexibilität also 0 ist)
                    return mindestreichweite_spaeter
                else:
                    # Hier reicht die restliche Zeit nicht aus. Es wird daher erst berechnet wie viel Zeit nach erreichen der Mindestreichweite sofort noch übrig ist
                    restliche_zeit = standdauer - mindestreichweite_sofort_dauer
                    # Diese verbleibende Zeit wird mit maximaler Laderate geladen
                    return round(mindestreichweite_sofort + (restliche_zeit*laderate_maximal), 2)
    else:
        # Die gewünschte Abfahrt ist liegt nach der tatsächlichen Abfahrtszeit. Es kann also vorkommen, dass der Ladevorgang unterbrochen werden muss
        # Erst muss ausgerechnet werden wie lange es dauert die gewünschte Mindestreichweite sofort aufzuladen. Falls die Mindestreichweite sofort nicht in der tatsächlichen (hier: gezogenen) Standdauer erreicht werden kann wird dies signalisiert indem die dauer auf die (hier:gezogene) Standdauer gesetzt wird.
        if mindestreichweite_sofort_dauer == standdauer:
            # Die gewünschte Mindestreichweite kann nicht erreicht werden. Allerdings muss das Auto jetzt sogar noch früher los. Deswegen wird hier die restliche Zeit nicht über die gewünschte Abfahrtszeit bestimmt sondern über die tatsächliche, gezogene Abfahrtszeit
            return round(kilometer_aktuell + (abfahrt * laderate_maximal), 2)
        else:
            # Die Mindestreichweite sofort aufzuladen würde nicht die gesamte Standdauer in Anspruch nehmen.
            if mindestreichweite_sofort >= mindestreichweite_spaeter:
                # Erst der einfache Fall: die gewünschte Mindestreichweite sofort ist größer als die Mindestreichweite später. Die Mindestreichweite später kann also ignoriert werden.
                if mindestreichweite_sofort_dauer >= mindestreichweite_sofort_dauer_drawn:
                    # Dauert es länger die Mindestreichweite sofort zu laden als Zeit bis zur tatsächlichen Abfahrt zur Verfügung steht, wird der Ladeprozess unterbrochen sobald die tatsächliche Abfahrtszeit erreicht ist
                    return round(kilometer_aktuell + (abfahrt * laderate_maximal), 2)
                else:
                    # Die Mindesterichweite sofort dauer und die Mindestreichweite sofort dauer drawn sollten jetzt gleich sein
                    # Die Zeit sollte auch mit dem früheren Abfahrtstermin ausreichen die geforderte Mindestreichweite sofort zu erreichen. Zusätzlich muss nicht weiter geladen werden.
                    return mindestreichweite_sofort
            else:
                # Die Mindestreichweite später kann nicht einfach ignoriert werden
                gewichtungsfaktor_zaehler = calc_gewichtungsfaktor_zaehler(mindestreichweite_sofort,
                                                                           mindestreichweite_spaeter, standdauer,
                                                                           mindestreichweite_sofort_dauer)
                gewichtungsfaktor = calc_gewichtungsfaktor(gewichtungsfaktor_zaehler)
                if gewichtungsfaktor <= 1:
                    # Erst der einfachere Fall: Der Gewichtungsfaktor ist kleiner gleich 1, die restliche Zeit (gemessen an der gewünschten Abfahrtszeit) reicht also aus um die Mindestreichweite später zu laden
                    if mindestreichweite_sofort_dauer_drawn == abfahrt:
                        # Die gezogene Abfahrtszeit liegt so, dass noch nicht einmal die Mindestreichweite sofort aufgelden werden kann. Das Auto denkt aber es hat Zeit erst die Mindestreichweite sofort zu laden und dann noch die Mindestreichweite später
                        return round(kilometer_aktuell + (abfahrt*laderate_maximal), 2)
                    else:
                        # Die gezogene Abfahrtszeit reicht aus um die gewünschte Mindestreichweite sofort aufzuladen
                        # Reicht die Zeit auch um die Mindestreichweite später aufzuladen (Gewichtungfaktor <= 1) wird angenommen, dass die gesamte Restzeit mit einer verringerten Laderate geladen wird. D.h. hier wird erst die Mindestreichweite sofort aufgeladen um dann mit verringerter Laderate die restlich Zeit aufzuladen
                        restliche_zeit = abfahrt - mindestreichweite_sofort_dauer_drawn
                        return round(mindestreichweite_sofort + (restliche_zeit*gewichtungsfaktor_zaehler), 2)
                else:
                    # Der Gewichtungsfaktor ist > 1, also würde die urpsrüngliche Zeit nicht ausreichen um die Mindestreichweite später zu laden
                    # Hier würde auch normalerweise die gesamte Standdauer über mit der maximalen Laderate aufgeladen werden. Also muss nicht erst noch überprüft werden ob die Standdauer ausreicht um die Mindestreichweite sofort aufzuladen
                    return round(kilometer_aktuell + (abfahrt*laderate_maximal), 2)


def participant(standdauer, mindestreichweite_sofort, mindestreichweite_spaeter, mindestreichweite_sofort_dauer,
                ladeflexibilitaet):

    drawn_temp = draw()
    to_drive = drawn_temp[0]
    abfahrt = drawn_temp[1]

    mindestreichweite_sofort_dauer_drawn = calc_mindestreichweite_sofort_dauer_drawn(abfahrt, mindestreichweite_sofort)

    geladene_kilometer = charge_up(mindestreichweite_sofort, mindestreichweite_spaeter, standdauer, abfahrt,
                                   mindestreichweite_sofort_dauer, mindestreichweite_sofort_dauer_drawn)


    if geladene_kilometer >= to_drive:
        return (ladeflexibilitaet, True)
    else:
        return (-ladeflexibilitaet, False)


def participant_group(nparticipants, mindestreichweite_sofort, mindestreichweite_spaeter, standdauer):
    counter = 1

    winners = 0
    losers = 0
    agg_values = 0

    ladedauer_maximal = calc_ladedauer_maximal(standdauer)
    mindestreichweite_sofort_dauer = calc_mindestreichweite_sofort_dauer(standdauer, mindestreichweite_sofort)

    if mindestreichweite_sofort_dauer == standdauer:
        ladeflexibilitaet = 0
    else:
        gewichtungsfaktor_zaehler = calc_gewichtungsfaktor_zaehler(mindestreichweite_sofort, mindestreichweite_spaeter,
                                                                   standdauer, mindestreichweite_sofort_dauer)
        gewichtungsfaktor = calc_gewichtungsfaktor(gewichtungsfaktor_zaehler)
        if gewichtungsfaktor >= 1:
            ladeflexibilitaet = 0
        else:
            mindestreichweite_spaeter_dauer = calc_mindestreichweite_spaeter_dauer(mindestreichweite_sofort,
                                                                                   mindestreichweite_spaeter)
            ladeflexibilitaet = calc_ladeflaexibilitaet(mindestreichweite_sofort_dauer, mindestreichweite_spaeter_dauer,
                                                        gewichtungsfaktor, ladedauer_maximal)

    while counter <= nparticipants:
        results = participant(standdauer, mindestreichweite_sofort, mindestreichweite_spaeter,
                                    mindestreichweite_sofort_dauer, ladeflexibilitaet)
        if results[1]:
            winners += 1
        else:
            losers += 1
        agg_values += results[0]
        counter += 1
    return winners, losers, agg_values


number_participants = 3000

mindestreichweite_sofort_start = 0
mindestreichweite_spaeter_start = 0
standdauer_start = 0.5

mindestreichweite_sofort_list = []
mindestreichweite_spaeter_list = []
standdauer_list = []
gewinner_prozent_list = []
verlierer_prozent_list = []
avg_profit_list = []

for mindestreichweite_sofort in range(mindestreichweite_sofort_start, 251):
    print(mindestreichweite_sofort, time.time())
    for mindestreichweite_spaeter in range(mindestreichweite_spaeter_start, 251):
        for standdauer in np.arange(standdauer_start, 24.5, 0.5):

            results = participant_group(number_participants, mindestreichweite_sofort, mindestreichweite_spaeter,
                                        standdauer)

            mindestreichweite_sofort_list.append(mindestreichweite_sofort)
            mindestreichweite_spaeter_list.append(mindestreichweite_spaeter)
            standdauer_list.append(standdauer)
            gewinner_prozent_list.append((results[0] / number_participants)*100)
            verlierer_prozent_list.append((results[1] / number_participants)*100)
            avg_profit_list.append(results[2] / number_participants)

            print('##############################################################')
            print('Mindestreichweite sofort ist aktuell', mindestreichweite_sofort)
            print('Mindestreichweite später ist aktuell', mindestreichweite_spaeter)
            print('Standdauer ist aktuell', standdauer)
            print('Profitwahrscheinlichkeit der Teilnehmer', (results[0] / number_participants) * 100)
            print('Verlustwahrscheinlichkeit der Teilnehmer', (results[1] / number_participants) * 100)
            print('Durchschnittlicher Gewinn oder Verlust der Teilnehmer beträgt', (results[2] / number_participants))


ergebnisse_dict = {'mindestreichweite_sofort': mindestreichweite_sofort_list,
                   'mindestreichweite_spaeter': mindestreichweite_spaeter_list,
                   'standdauer': standdauer_list,
                   'gewinn_prozent': gewinn_prozent_list,
                   'verlust_prozent': verlust_prozent_list,
                   'avg_profig': avg_profit_list}

ergebnisse = pd.DataFrame(ergebnisse_dict)

print(ergebnisse.head())
ergebnisse.to_csv('C:\\Users\\Martin Wolff\\Downloads\\MonteCarloVerbessert.csv')