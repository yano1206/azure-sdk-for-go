# Tête animée – Spine 2D (cible **Spine 4.2**)

## Contenu
| Chemin | Rôle |
|---|---|
| `images/` (= `export/images/`) | 49 PNG transparents découpés : `base_`, `hair_`, `eyeA_/eyeB_`, `lidA_/lidB_`, `browA_/browB_`, `nose_`, `mouthC_` (fermée), `mouthO_` (ouverte) × vues `PG` (profil gauche), `TG` (3/4 gauche), `F` (face), `TD` (3/4 droit), `PD` (profil droit). `A` = élément à gauche de l'image, `B` = à droite. |
| `export/head.json` | Squelette + animation `head_turn` (JSON Spine 4.2, `"spine": "4.2.43"`, 30 fps, 8 s). |
| `export/head.atlas` + `export/head.png` | Atlas pour les runtimes (format texte Spine 4). |
| `preview/head_turn.mp4`, `preview/head_turn.gif` | Aperçu 480×480 (GIF 360 px), 240 images, 8 s. |
| `extract.py`, `register*.py`, `layout.py`, `overrides.json`, `build_spine.py` | Pipeline de découpe / placement / génération. |
| `verify_runtime.mjs`, `render_preview.py` | Vérification avec le runtime officiel + rendu de l'aperçu. |

Pas de fichier `.spine` : Spine (l'éditeur) n'est pas installé ici, il n'a donc pas été créé.

## Rig
```
root
└─ neck (pivot = base du cou, commun aux 5 vues)
   └─ head (haut du cou : inclinaison, squash léger)
      ├─ face (glissement des traits pendant les changements de vue)
      │  ├─ eyes   (slots eyeA, lidA, eyeB, lidB)
      │  ├─ brows  (slots browA, browB)
      │  ├─ nose
      │  └─ mouth  (mouthC_* / mouthO_*)
      └─ hair (pivot au sommet du crâne, mouvement secondaire)
```
Ordre de dessin : base → eyeA → lidA → eyeB → lidB → browA → browB → nose → mouth → hair.
En profil, le slot de l'œil éloigné est vide (attachment `null`). Le clignement remplace l'œil par la paupière (pas de fondu).

## Animation `head_turn` (8 s @ 30 fps)
| Images | Action |
|---|---|
| 0–30 | Face (clignement f21) |
| 30–44 | Tourne à gauche : 3/4 G à f36, profil G à f44 |
| 44–78 | Profil gauche (clignement f64) |
| 78–92 | Retour : 3/4 G f84, face f92 |
| 92–120 | Face (clignement f108) |
| 120–134 | Tourne à droite : 3/4 D f126, profil D f134 |
| 134–165 | Profil droit (clignement f152) |
| 165–179 | Retour : 3/4 D f171, face f179 |
| 192–218 | Sourire bouche ouverte (pop d'échelle de la bouche, sourcils levés, rebond de tête) |
| 218–240 | Retour pose initiale (clignement f226), boucle |

Chaque changement de dessin est un échange d'attachment instantané (aucun mix alpha) accompagné d'un léger squash (scaleX 0.965), d'un glissement des traits de 3–4 px, d'une dérive et d'une inclinaison de tête (±4°) avec anticipation/dépassement, et d'un retard des cheveux (±3.5°). Courbes Bézier ease-in/out.

## Import dans Spine
1. Spine 4.2 → **Spine menu › Import Data…** → choisir `export/head.json`.
2. Le chemin des images est `./images/` (relatif au JSON) : garder `export/images/` à côté du JSON (sinon régler **Images** dans l'arbre sur le dossier `images`).
3. Animations › `head_turn` → Play (boucle). Les FPS du dopesheet sont à 30.

## Runtime
```js
// spine-player / spine-webgl / spine-ts 4.2
new spine.SpinePlayer("el", { jsonUrl: "head.json", atlasUrl: "head.atlas", animation: "head_turn" });
```

## Ce qui a été vérifié
- `export/head.json` + `head.atlas` chargés avec le **runtime officiel `@esotericsoftware/spine-core` 4.2.120** (Node) sans erreur : 9 os, 10 slots, animation `head_turn` de durée 8.0 s.
- Les 240 images de l'aperçu sont calculées par ce runtime (`AnimationState` + `updateWorldTransform` + `RegionAttachment.computeWorldVertices`) puis rastérisées en Python : l'aperçu reflète donc les transformations réelles du runtime.
- **Non vérifié** : l'import dans l'éditeur Spine (non disponible ici).

## Limites connues
- Les pièces séparées sont dessinées plus grandes que dans les têtes de référence : yeux, sourcils, nez et bouches sont mis à l'échelle 0.62 (échelle d'attachment, PNG intacts) et placés d'après la ligne « Aperçu » (correspondance automatique + retouches dans `overrides.json`).
- Paupières et bouche ouverte n'existent pas dans la référence : placées sur l'œil / la bouche fermée correspondante.
- Pas de vraie rotation 3D : transitions courtes par échange de dessins.
