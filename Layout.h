// genere par tools/make_art.py - ne pas modifier a la main (repere 617.5 x 900.0 = fond 1235 x 1800 px / 2)
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 617.50f, frameH = 900.00f;   // pedale plein cadre (jacks aux bords gauche / droit)
    // ordre : elevel, mix, feedback, time, mode
    const juce::Point<float> knobPos[5] = { { 204.00f, 147.50f }, { 414.00f, 147.50f }, { 204.00f, 305.00f }, { 414.00f, 305.00f }, { 414.19f, 496.66f } };
    const float knobR = 52.58f, modeLabelR = 67.75f, modeFont = 12.64f;
    // tubes de lumiere des memoires 1-7 : centre (zone de clic), coin du sprite allume, calques de lumiere
    const juce::Point<float> slotPos[7] = { { 45.57f, 77.28f }, { 45.57f, 130.78f }, { 45.57f, 184.28f }, { 45.57f, 237.78f }, { 45.57f, 291.28f }, { 45.57f, 344.78f }, { 45.57f, 398.28f } };
    const juce::Point<float> pipeOrigin[7] = { { 15.74f, 49.55f }, { 15.74f, 103.15f }, { 15.74f, 156.49f }, { 15.74f, 210.08f }, { 15.74f, 263.43f }, { 15.74f, 317.02f }, { 15.74f, 370.62f } };
    const float pipeW = 68.45f, pipeH = 56.14f;
    const juce::Rectangle<float> glowSlot[7] = { { 12.64f, 24.69f, 131.46f, 105.17f }, { 12.64f, 78.19f, 131.46f, 105.17f }, { 12.64f, 131.69f, 131.46f, 105.17f }, { 12.64f, 185.19f, 131.46f, 105.17f }, { 12.64f, 238.69f, 131.46f, 105.17f }, { 12.64f, 292.19f, 131.46f, 105.17f }, { 12.64f, 345.69f, 131.46f, 105.17f } };
    const juce::Point<float> ledTempo { 145.46f, 625.23f }, ledCheck { 472.04f, 625.23f }; const float ledS = 27.81f;
    const juce::Point<float> syncPos { 203.31f, 490.96f }; const float syncR = 29.33f, syncS = 85.04f;
    const juce::Point<float> fsTap { 145.46f, 784.91f }, fsBypass { 472.04f, 784.91f }; const float footR = 37.54f, fsS = 188.29f;
    const juce::Point<float> x2Pos { 308.75f, 786.93f };
    const juce::Point<float> triUp { 145.46f, 685.37f }, triDown { 472.04f, 683.29f };
    const juce::Rectangle<float> glow_tempo { 44.34f, 524.11f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_check_red { 370.91f, 524.11f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_check_green { 370.91f, 524.11f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_check_orange { 370.91f, 524.11f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_sync { 120.38f, 408.03f, 165.84f, 165.84f };
    const juce::Rectangle<float> glow_x2 { 212.68f, 741.42f, 192.13f, 91.01f };
    const juce::Rectangle<float> statusRect { 142.95f, 26.61f, 332.11f, 40.45f }; const float statusFont = 21.24f;
    const juce::Rectangle<float> boxRect { 18.71f, 0.00f, 580.08f, 900.00f };   // boitier
    // serigraphie vectorielle : texte, police (0 Liberation Sans Bold, 1 Liberation Mono Bold), taille em, espacement, centre, rotation (degres)
    struct Txt { const char* s; int font; float em, track, x, y, rot; };
    const Txt texts[] = {
        { "E.LEVEL", 0, 17.70f, 0.61f, 204.00f, 228.40f, 0.00f },
        { "MIX", 0, 17.70f, 0.61f, 414.00f, 228.40f, 0.00f },
        { "FEEDBACK", 0, 17.70f, 0.61f, 204.00f, 385.90f, 0.00f },
        { "TIME", 0, 17.70f, 0.61f, 414.00f, 385.90f, 0.00f },
        { "MODE", 0, 17.70f, 0.61f, 414.19f, 577.56f, 0.00f },
        { "SYNC", 0, 17.70f, 0.61f, 203.31f, 577.56f, 0.00f },
        { "1", 0, 28.00f, 0.00f, 96.20f, 59.10f, 0.00f },
        { "2", 0, 28.00f, 0.00f, 96.20f, 111.98f, 0.00f },
        { "3", 0, 28.00f, 0.00f, 96.20f, 165.90f, 0.00f },
        { "4", 0, 28.00f, 0.00f, 96.20f, 218.78f, 0.00f },
        { "5", 0, 28.00f, 0.00f, 96.20f, 272.70f, 0.00f },
        { "6", 0, 28.00f, 0.00f, 96.20f, 326.61f, 0.00f },
        { "7", 0, 28.00f, 0.00f, 96.20f, 379.49f, 0.00f },
        { "TAP", 0, 17.70f, 0.61f, 145.46f, 873.04f, 0.00f },
        { "BYPASS", 0, 17.70f, 0.61f, 472.04f, 873.04f, 0.00f },
        { "OUT A", 0, 14.66f, 0.81f, 39.94f, 479.03f, 90.00f },
        { "IN A", 0, 14.66f, 0.81f, 577.56f, 479.03f, 90.00f },
        { "OUT B", 0, 14.66f, 0.81f, 39.94f, 626.27f, 90.00f },
        { "IN B", 0, 14.66f, 0.81f, 577.56f, 626.27f, 90.00f }
    };
    struct Dot { float x, y, r; };
    const Dot dots[] = { { 159.67f, 191.83f, 1.72f }, { 144.37f, 166.87f, 1.72f }, { 142.08f, 137.69f, 1.72f }, { 153.28f, 110.65f, 1.72f }, { 175.54f, 91.64f, 1.72f }, { 204.00f, 84.80f, 1.72f }, { 232.46f, 91.64f, 1.72f }, { 254.72f, 110.65f, 1.72f }, { 265.92f, 137.69f, 1.72f }, { 263.63f, 166.87f, 1.72f }, { 248.33f, 191.83f, 1.72f }, { 369.67f, 191.83f, 1.72f }, { 354.37f, 166.87f, 1.72f }, { 352.08f, 137.69f, 1.72f }, { 363.28f, 110.65f, 1.72f }, { 385.54f, 91.64f, 1.72f }, { 414.00f, 84.80f, 1.72f }, { 442.46f, 91.64f, 1.72f }, { 464.72f, 110.65f, 1.72f }, { 475.92f, 137.69f, 1.72f }, { 473.63f, 166.87f, 1.72f }, { 458.33f, 191.83f, 1.72f }, { 159.67f, 349.33f, 1.72f }, { 144.37f, 324.37f, 1.72f }, { 142.08f, 295.19f, 1.72f }, { 153.28f, 268.15f, 1.72f }, { 175.54f, 249.14f, 1.72f }, { 204.00f, 242.30f, 1.72f }, { 232.46f, 249.14f, 1.72f }, { 254.72f, 268.15f, 1.72f }, { 265.92f, 295.19f, 1.72f }, { 263.63f, 324.37f, 1.72f }, { 248.33f, 349.33f, 1.72f }, { 369.67f, 349.33f, 1.72f }, { 354.37f, 324.37f, 1.72f }, { 352.08f, 295.19f, 1.72f }, { 363.28f, 268.15f, 1.72f }, { 385.54f, 249.14f, 1.72f }, { 414.00f, 242.30f, 1.72f }, { 442.46f, 249.14f, 1.72f }, { 464.72f, 268.15f, 1.72f }, { 475.92f, 295.19f, 1.72f }, { 473.63f, 324.37f, 1.72f }, { 458.33f, 349.33f, 1.72f } };
    struct Line { float x0, y0, x1, y1, w; };   // les 2 derniers : traits de X2 (allumes avec X2)
    const Line lines[] = { { 374.15f, 536.70f, 369.86f, 540.99f, 2.02f }, { 360.34f, 514.16f, 354.57f, 516.03f, 2.02f }, { 358.26f, 487.80f, 352.27f, 486.85f, 2.02f }, { 368.38f, 463.37f, 363.47f, 459.81f, 2.02f }, { 388.49f, 446.20f, 385.73f, 440.80f, 2.02f }, { 414.19f, 440.03f, 414.19f, 433.96f, 2.02f }, { 439.90f, 446.20f, 442.66f, 440.80f, 2.02f }, { 460.01f, 463.37f, 464.92f, 459.81f, 2.02f }, { 470.13f, 487.80f, 476.12f, 486.85f, 2.02f }, { 468.05f, 514.16f, 473.82f, 516.03f, 2.02f }, { 454.24f, 536.70f, 458.53f, 540.99f, 2.02f }, { 260.17f, 786.93f, 239.94f, 786.93f, 2.63f }, { 357.33f, 786.93f, 377.56f, 786.93f, 2.63f } };
    struct Tri { float x0, y0, x1, y1, x2, y2; };
    const Tri tris[] = { { 133.33f, 690.47f, 157.60f, 690.47f, 145.46f, 677.85f }, { 459.90f, 678.20f, 484.17f, 678.20f, 472.04f, 690.82f } };
    const float triStroke = 1.82f;
    // lettrage d'origine (traits, extremites droites) : titre EIGHT ECHO et X2
    const juce::Rectangle<float> titleRect { 224.25f, 606.57f, 169.01f, 71.54f };   // logo EIGHT ECHO (eight_echo_title.svg)
    const float x2Pts[] = { 270.43f, 769.22f, 304.10f, 804.64f, 304.10f, 769.22f, 270.43f, 804.64f, 312.81f, 772.99f, 336.91f, 772.99f, 338.18f, 773.09f, 339.42f, 773.39f, 340.60f, 773.88f, 341.69f, 774.55f, 342.66f, 775.38f, 343.49f, 776.35f, 344.15f, 777.43f, 344.64f, 778.61f, 344.94f, 779.85f, 345.04f, 781.12f, 345.04f, 778.80f, 344.94f, 780.07f, 344.64f, 781.31f, 344.15f, 782.49f, 343.49f, 783.58f, 342.66f, 784.55f, 341.69f, 785.38f, 340.60f, 786.04f, 339.42f, 786.53f, 338.18f, 786.83f, 336.91f, 786.93f, 324.72f, 786.93f, 323.45f, 787.03f, 322.21f, 787.33f, 321.03f, 787.82f, 319.94f, 788.48f, 318.97f, 789.31f, 318.14f, 790.28f, 317.47f, 791.37f, 316.99f, 792.55f, 316.69f, 793.79f, 316.59f, 795.06f, 316.59f, 800.87f, 348.81f, 800.87f };
    const int x2Lens[] = { 2, 2, 36 };
    const float x2Stroke = 7.55f;
    // motif d'anneaux (eight_echo_motif.svg, repere 4096) : point gauche du SVG -> footswitch TAP, echelle
    const juce::Point<float> motifSvgLeft { 875.429f, 2048.000f }; const float motifScale = 0.139256f;
    const juce::Point<float> logoPos { 308.75f, 874.08f }; const float logoW = 188.09f;
    // le motif s'arrete a cette distance du contour de chaque inscription (8 px de l'image 1800 = 4 unites)
    const float knockMargin = 4.00f;
}
