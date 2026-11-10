# Eight Echo (NINE HANDS | DSP)

Plugin VST3 (Windows / macOS, + AU sur Mac) reproduisant le fonctionnement d'un delay compact
11 modes de type DD-8 : mêmes plages, mêmes commandes, mêmes interactions.

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Echo-Eight/releases/latest/download/EightEcho-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Echo-Eight/releases/latest/download/EightEcho-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Echo-Eight/releases/latest/download/EightEcho-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Echo-Eight/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Echo-Eight?label=derni%C3%A8re%20version&color=566774"></a>
</p>

## Installation
Les boutons ci-dessus téléchargent toujours la dernière version. Windows : copier `Eight Echo.vst3` dans
`C:\Program Files\Common Files\VST3`. macOS : `~/Library/Audio/Plug-Ins/VST3` (et `Eight Echo.component` dans `~/Library/Audio/Plug-Ins/Components`).

## Compilation (GitHub)
Tous les fichiers sont à la racine. Le workflow `.github/workflows/build.yml` compile sous `windows-2022` (VST3) et macOS (VST3 + AU)
et publie la Release (fichiers à nom fixe, notice comprise) à chaque push sur `main`.

## Commandes (visuel Eight Echo)
| Élément | Rôle |
|---|---|
| E.LEVEL | Niveau d'effet. Vers 3 h = même niveau que le son direct. REVERSE au maximum : effet seul. LOOP : volume de la boucle |
| MIX | Équilibre direct/effet. **À midi = comme la DD-8** (direct + effet pleins). À gauche : le direct seul ; à droite : l'effet seul (« Direct Mute ») |
| FEEDBACK | Répétitions (auto-oscillation possible tout en haut). En GLT : profondeur |
| TIME | Temps (plage selon le mode). Tourner TIME annule le tempo tapé |
| MODE | 11 positions, étiquetées autour du potard : clic sur une étiquette, glisser ou molette |
| BYPASS (footswitch droit) | Le footswitch de la DD-8 : clic = on/off ; maintien 2 s = mode TEMPO ; en WARP/GLT maintien = effet ; en LOOP : rec → lecture → overdub, double appui = stop, maintien 2 s = effacer |
| TAP (footswitch gauche) | Tap tempo ; **maintenu = TWIST** ; en LOOP : appui = stop, maintien 2 s = effacer |
| LED gauche | Bat la mesure : calée sur la mesure du DAW quand SYNC est actif et que le DAW joue (1er temps plus fort) ; relancée exactement à chaque tap (1er tap = temps 1) ; sinon au temps de retard. Scintille pendant le Twist |
| LED droite | Le témoin CHECK de la DD-8 : rouge = effet actif, vert = mode tempo / lecture loop, orange = overdub, clignotements = enregistrement / tap |
| X2 | Temps doublé (sortie « Long » de la DD-8). S'illumine quand actif |
| Tubes 1 à 7 | Mémoires (tubes de lumière qui traversent la tranche gauche) : clic = rappel, **maintien 1 s = sauvegarde** (le tube clignote pour confirmer). Tube plein = réglage identique à la mémoire, tube adouci = mémoire modifiée |
| SYNC | Cale le delay sur le tempo du DAW (avec la division du tap). Bouton allumé bleu glace qui respire au tempo ; ligne d'état « SYNC 120 BPM » (« SYNC · PAS DE TEMPO DU DAW » sinon). Re-clic = retour à TIME / tap |
| △ / ▽ | Mémoire précédente / suivante |
| Pastille du haut | Au repos : barre de presets (mémoire en cours · nom du preset, * = modifiée ; ◀ ▶ = preset d'usine précédent / suivant ; clic sur le nom = menu des presets). Pendant un réglage : ligne d'état (E.LEVEL 64 %, TIME 420 ms, MODE TAPE…), puis retour en fondu |

**Clic droit** (réglages cachés de la DD-8) : presets d'usine (chargés dans la mémoire en cours), mode stéréo
(Independent / Wide / Panning), division du tap, sauvegarde en mémoire 1-7, carryover, SYNC, affectation de la pédale d'expression
(paramètre EXP), Plugin size (60 % / 75 % / 100 %, comme Textural et Freeze Shimmer ; « (default) » marque la taille par défaut choisie). Plugin size > Default size (new windows) : taille d'ouverture des nouvelles fenêtres (toutes les instances, comme dans Octopus), appliquée aussi tout de suite à la fenêtre ouverte ; une taille changée sur une instance est sauvegardée avec le projet et reprise à sa réouverture. La fenêtre (pédale plein cadre) ne peut jamais être réduite sous 60 % ; elle va jusqu'à 150 %.

Tout est automatisable / assignable en MIDI dans Reaper (footswitch, tap, twist compris).

## Plages de temps (ms)
| Mode | Normal | Long |
|---|---|---|
| ANALOG, STANDARD, TAPE, WARM, +RV, MOD, WARP | 20–800 | 40–1600 |
| REVERSE | 300–5000 | 600–10000 |
| SHIM | 200–800 | 400–1600 |
| GLT | 10–400 | 20–800 |
| Tap tempo | 67–10000 | |
| LOOP | 40 s | |

## Ce qui a été mesuré sur les vidéos (et appliqué)
- **TWIST** (vidéo officielle, TAPE/TWIST) : la hauteur monte d'environ 2,7 octaves en ~4 s,
  le feedback part en auto-oscillation, puis tout retombe au relâchement. Ajout d'une rotation stéréo.
- **Auto-oscillation TAPE** : le niveau plafonne (pas d'emballement) et le son s'éclaircit / se salit
  avec le temps → saturation + limiteur doux dans la boucle.
- **MOD** : LFO ≈ 1,5 Hz, ≈ ±15 cents (~1 ms), voies gauche/droite en opposition de phase.
- **TAPE** : modulation légère (quelques cents), wow lent + flutter.
- **GLT** : tranches répétées et hachées (voir v1.1).
- **+RV** : TIME agit aussi sur la durée de la reverb ; même au minimum de feedback il reste une répétition.
- **Wide stereo** : léger balancement gauche/droite (moins dur que le ping-pong).
- **ANALOG / TAPE** : tourner TIME fait glisser la hauteur ; les modes numériques changent de temps par fondu.

## Version 1.1 – ajustements d'après les manuels Boss et les tests
- **Couleur dès la 1re répétition** : WARM, MOD, WARP, +RV… sortaient brillants au premier écho, ils ont maintenant leur couleur tout de suite.
- **WARM** : « un STANDARD moins brillant », rond et moderne (Delay Dude, Bonedo) → moins sombre qu'avant.
- **TAPE** : percussif et pas « usé » (Bonedo) → moins de saturation, de souffle et de perte d'aigus. Modèle de base type RE-201 (famille Boss).
- **SHIM** : octave plus discrète, comme décrite par Bonedo ; architecture Boss (balance octave / son direct envoyée dans le delay + feedback).
- **GLT** : la même séquence courte boucle tant que le pied est maintenu, sa longueur suit TIME/tempo ; la profondeur (FEEDBACK) va d'un bégaiement doux à des coupures franches.
- **MOD** : modulation « bi-phase » (gauche/droite en opposition), comme le mode BI-PHASE des delays Boss.
- **TWIST** : montée puis retombée de la rotation (logique RISE → FALL des multi-effets Boss).
- **REVERSE au maximum** : effet seul au même niveau que l'entrée (avant, un peu plus fort).
- **Direct Mute** actif aussi en LOOP.

## Presets d'usine (clic droit → Factory presets, ou menu de presets du DAW)
Classiques : Clean Slapback, Rockabilly Tape, Doubler, Bread & Butter, Dotted 8th Arena, Ping Pong Eighths  
Vintage : BBD Crunch Lead, Dark BBD Wash, Floating Tape Solo, Long Tape Ambience  
Doux / modernes : Soft Ballad, Jazz Room, Lush Chorus Echo, 80s Stereo Lead  
Espace : Echo Hall, Cathedral, Heaven Swell, Octave Haze, Dream Swell (hold), Space Freeze (hold)  
À l'envers / glitch : Backwards Solo, Backwards Pad, Machine Gun (hold), Stutter Groove (hold), Granular Buzz (hold)  
Looper : Looper

« (hold) » = maintenir le footswitch BYPASS.

## Version 1.3 – visuel à l'identique
- Potards : ce sont ceux de l'image (moletage, reflet conique, ombre). Seul le repère blanc, découpé sur l'image, tourne : l'éclairage reste fixe comme sur une vraie pédale.
- LED 1 à 7 : tubes de lumière d'origine avec leur diffusion sur la plaque ; version éteinte en acrylique dépoli de même forme.
- LED rondes : lentilles d'origine allumées en bleu glace / rouge / vert / orange, avec la lumière qui déborde sur la bague et la plaque.
- Fond : motifs d'anneaux de la pédale en transparence autour d'elle.
- « NINE HANDS | DSP » en gris-noir, légèrement gravé, entre les deux footswitchs.

## Version 1.3.1
- LED CHECK (rouge / vert / orange) refaite comme la LED bleue : même profil de lumière, cœur pastel lumineux et même halo.

## Version 1.3.2
- Logo NINE HANDS | DSP (cercles orange/blanc + texte) a la place du texte, entre TAP et BYPASS.


## Version 1.3.4
- Lumiere autour des LED bleue et CHECK : halo rond qui s eteint en douceur (plus de bord carre).

## Version 1.4.0
- Logo NINE HANDS | DSP integre a la plaque (fixe, ne clignote plus quand on appuie sur un footswitch), detoure en gris-noir pour mieux ressortir.
- Potard MODE : cranté exactement sur chacun des 11 modes inscrits (le repere pointait a cote auparavant).
- X2 : c'est la serigraphie X2 elle-meme qui s'illumine (meme forme, meme taille).
- Looper : une boucle enregistree continue de tourner quand on choisit un autre mode ; on joue par-dessus avec cet effet, la boucle reste seche (elle ne passe jamais dans le delay). Son volume est celui regle avec E.LEVEL en mode LOOP. Pour l'arreter : revenir sur LOOP (double appui / maintien 2 s pour effacer). La ligne d'etat affiche « +LOOP » quand une boucle tourne sous l'effet.
- Ligne d'etat agrandie ; DC 9V remonte pour lui laisser la place.

## Version 1.4.1
- Preset « Runaway Tape (Twist) » supprime (26 presets d'usine).
- Presets « (hold) » et effets maintenus (WARP, GLT, TWIST) : niveau securise. Limiteur automatique : pendant le maintien, l'effet ne depasse jamais environ +2 dB du niveau d'avant l'appui. WARP monte en nappe sans emballement, GLT au niveau du delay. Presets hold avec E.LEVEL reduit.

## Version 1.4.2
- Redimensionnement : impossible de reduire la fenetre sous sa taille par defaut (380 x 493), que ce soit par le coin, par un bord, par l hote ou a la reouverture du projet. Le rapport largeur/hauteur reste fixe ; agrandissement jusqu a 200 %.

## Version 1.5.0
- Bouton SAVE remplacé par **SYNC** (sérigraphie refaite dans la police de la pédale) : un clic cale le delay sur le tempo du DAW. Le capuchon s'éclaire en bleu glace et respire au tempo.
- Mémoires : maintien 1 s sur une LED 1-7 = sauvegarde (ou clic droit › Save current settings to memory).
- LED de tempo vérifiée et corrigée : elle tournait sur une horloge libre, décalée des taps et des temps du DAW. Elle est maintenant calée sur la position du DAW (temps de la mesure, signature rythmique comprise, 1er temps accentué) et repart exactement sur chaque tap.
- Fenêtre et pédale calées sur Freeze Shimmer : 390 x 494 par défaut (minimum), boîtier haut de 465 px, tailles Default / 60% / 75% / 100% (2000 px de haut).
- Aspect : éclairage doux derrière la pédale, ombre portée sous le boîtier, vignettage, ligne d'état ombrée pour la lisibilité, motifs d'anneaux replacés.

## Version 1.5.1
- Inscription « DC 9V » retirée du haut de la plaque ; la ligne d'état remonte légèrement.

## Version 1.5.2
- Ligne d'état discrète : elle n'apparaît que lorsqu'une information change (potard, mode, mémoire, tap, SYNC, looper…), reste affichée environ 2 s puis s'efface en fondu.

## Version 1.5.3
- Correctif anti-gel de la fenêtre sous Windows (Reaper notamment) : l'interface est dessinée avec le moteur logiciel au lieu de Direct2D, qui pouvait figer la fenêtre avec certains pilotes graphiques.
- L'interface ne redessine plus que ce qui change réellement (LED, ligne d'état, SYNC) : aucun travail au repos.
- Redimensionnement : tolérance de 2 px pour éviter une boucle avec l'hôte quand Windows est à 125 / 150 %.

## Version 1.6.0
- v1.6.0 : anti-gel v2 (JUCE 8.0.15, caches refaits par le timer, chien de garde, aucun appel à l'hôte depuis le thread audio)

## Version 1.7.1
- v1.7.1 : LED des mémoires 1 à 7 et LED SYNC d'un bleu glacier plus marqué (seule la lumière est teintée, la plaque ne change pas)

## Version 1.7.0
- v1.7.0 : MIDI Learn sur toutes les commandes (clic droit sur une commande ou menu MIDI), assignations sauvegardées avec le projet
- CC par défaut : E.LEVEL 20, MIX 21, FEEDBACK 22, TIME 23, MODE 24, X2 25, SYNC 26, EXP 27, BYPASS 80, TAP 81, PREV MEMORY 82, NEXT MEMORY 83.

- v1.7.2 : menu de taille de fenêtre : « 60 % (default) », 75 %, 100 % (plus de taille en pixels)

## Version 1.8.0
- v1.8.0 : clic droit > Plugin size > Default size (new windows) : taille par défaut des nouvelles fenêtres au choix, comme dans Octopus

## Version 1.8.1
- v1.8.1 : au lancement, la mémoire 1 est chargée (potards, mode, X2 = mémoire 1, LED 1 pleine ; programme affiché par l'hôte : Bread & Butter).
- v1.8.1 : le delay ne peut plus disparaître pour de bon. Un seul échantillon NaN / infini (reconstruction de la chaîne par REAPER ou Octopus, plugin précédent…) tournait indéfiniment dans la boucle de répétitions : delay muet même en coupant / rallumant la pédale. Entrée filtrée (NaN / infini → 0, crête limitée à +24 dBFS) ; si une valeur invalide apparaît dans le moteur, remise en état complète automatique (répétitions, reverb, pitch, glitch, limiteur, boucle du looper nettoyée) et le bloc sort le son direct. `reset()` de l'hôte pris en charge.
- `tools/host_check` : charge le VST3 compilé comme un hôte et vérifie la mémoire 1 au lancement et la présence du delay après désactivation, bypass, état relu, presets lus par Octopus, tailles de bloc, changement de fréquence, NaN, entrée énorme, Program Change, pédale coupée / rallumée, et dans chaque mode.

## Version 1.8.2
- v1.8.2 : bypass par l'hôte (REAPER, footswitch STOMP d'Octopus) corrigé. Le `reset()` ajouté en 1.8.1 (appelé par VST3 `setProcessing(false)` à chaque bypass, éventuellement depuis le thread d'interface) faisait tout le nettoyage du moteur hors du thread audio : ~15 ms et accès concurrent au moteur pendant que le son tournait. Désormais `reset()` ne fait que lever un drapeau ; le thread audio remet les répétitions à zéro au bloc suivant (reprise en fondu). `prepareToPlay` à la même fréquence ne réalloue plus rien (réactivation < 1 ms, boucle du looper gardée) et le thread audio laisse passer le son direct si une préparation est en cours sur un autre thread.
- `tools/host_check` : 40 bypass STOMP (setProcessing false/true + paramètre Bypass) pendant que le son tourne sur un autre thread, fenêtre ouverte : temps de bypass, sortie valide, pédale qui répond, delay présent ensuite.

## Version 1.8.3
- v1.8.3 : plus aucune assignation MIDI par défaut (les CC 20-27 et 80-83 entraient en conflit avec le contrôleur qui pilote Octopus sur la même piste : son footswitch actionnait aussi BYPASS d'Eight Echo). Une commande ne réagit au MIDI qu'après un MIDI Learn, fait par clic droit sur la commande (EXP : Clic droit › Expression pedal › MIDI Learn: EXP). Un projet d'une version plus ancienne s'ouvre sans aucune assignation. Sous-menu MIDI et « Reset MIDI to defaults » retirés ; « Cancel MIDI learn » en tête du menu pendant l'attente, « Clear all MIDI assignments » dès qu'une commande est assignée.

## Version 2.0.0 – nouveau visuel
- Pédale plein cadre (image 1235 x 1800, boîtier rendu en 4K, aluminium brossé bleu-gris, bevel rond de 17 px, lumière en haut à gauche à 45°) ; fenêtre 60 % / 75 % / 100 %, jusqu'à 150 %.
- Mémoires 1 à 7 : tubes de lumière intégrés à la tranche gauche (bevel droit, aplat sous l'acrylique), lumière qui déborde et éclaire la plaque.
- Pièces photo NINE HANDS | DSP : potards, footswitchs, jacks, LED et bouton SYNC ; sérigraphie, titre EIGHT ECHO, X2, motif d'anneaux (qui s'écarte des inscriptions) et logo en vectoriel, nets à toutes les tailles.
- Barre de presets et ligne d'état dans la même pastille (Poppins, taille de référence) ; textes d'état en français ; nom du preset gardé dans chaque mémoire.
- Menus clic droit au design d'Octopus, ouverts là où l'on clique (en-tête de la pédale ou de la commande avec son CC MIDI).
- Nom du mode choisi en bleu ; X2 et ses traits s'allument avec une lueur sur la plaque.
- `tools/render` : captures de la vraie fenêtre (aperçu, notice).

## Notice
- `docs/EightEcho_Notice_FR_v2.0.0.pdf` (français). Générateur : `python3 tools/manual.py <captures tools/render> <sortie.pdf>` (textes dans `tools/manual_text.py`, schémas dans `tools/manual/`, illustrations tirées des captures du plugin).
