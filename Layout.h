// genere par tools/make_art.py - ne pas modifier a la main (repere 617.5 x 900.0 = fond 1235 x 1800 px / 2)
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 617.50f, frameH = 900.00f;   // pedale plein cadre (jacks aux bords gauche / droit)
    // ordre : elevel, mix, feedback, time, mode
    const juce::Point<float> knobPos[5] = { { 214.65f, 135.83f }, { 425.54f, 135.83f }, { 214.65f, 303.80f }, { 425.54f, 303.80f }, { 427.76f, 496.66f } };
    const float knobR = 52.58f, modeLabelR = 67.75f, modeFont = 12.64f;
    const juce::Point<float> slotPos[7] = { { 46.38f, 109.91f }, { 46.38f, 162.79f }, { 46.38f, 217.74f }, { 46.38f, 270.62f }, { 46.38f, 324.54f }, { 46.38f, 378.46f }, { 46.38f, 432.37f } };
    const float slotS = 18.96f;
    const juce::Point<float> ledTempo { 148.78f, 625.23f }, ledCheck { 469.49f, 624.19f }; const float ledS = 27.81f;
    const juce::Point<float> syncPos { 214.65f, 490.96f }; const float syncR = 28.31f, syncS = 82.11f;
    const juce::Point<float> fsTap { 147.12f, 784.91f }, fsBypass { 473.70f, 784.91f }; const float footR = 37.54f, fsS = 188.29f;
    const juce::Point<float> x2Pos { 308.75f, 786.93f };
    const juce::Point<float> triUp { 144.91f, 685.37f }, triDown { 471.48f, 683.29f };
    const juce::Rectangle<float> glow_tempo { 47.66f, 524.11f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_check_red { 368.37f, 523.07f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_check_green { 368.37f, 523.07f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_check_orange { 368.37f, 523.07f, 202.25f, 202.25f };
    const juce::Rectangle<float> glow_slot0 { -0.13f, 63.39f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_slot1 { -0.13f, 116.27f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_slot2 { -0.13f, 171.23f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_slot3 { -0.13f, 224.11f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_slot4 { -0.13f, 278.02f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_slot5 { -0.13f, 331.94f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_slot6 { -0.13f, 385.86f, 93.03f, 93.03f };
    const juce::Rectangle<float> glow_sync { 133.75f, 410.06f, 161.80f, 161.80f };
    const juce::Rectangle<float> glow_x2 { 237.96f, 716.14f, 141.57f, 141.57f };
    const juce::Rectangle<float> statusRect { 76.27f, 24.88f, 464.95f, 30.34f }; const float statusFont = 19.21f;
    const juce::Rectangle<float> boxRect { 18.71f, 0.00f, 580.08f, 900.00f };   // boitier
    // serigraphie vectorielle : texte, police (0 medium, 1 bold, 2 light), taille em, espacement, centre, rotation (degres)
    struct Txt { const char* s; int font; float em, track, x, y, rot; };
    const Txt texts[] = {
        { "E.LEVEL", 0, 17.19f, 2.22f, 214.65f, 218.75f, 0.00f },
        { "MIX", 0, 17.19f, 2.22f, 425.54f, 218.75f, 0.00f },
        { "FEEDBACK", 0, 17.19f, 2.22f, 214.65f, 386.72f, 0.00f },
        { "TIME", 0, 17.19f, 2.22f, 425.54f, 386.72f, 0.00f },
        { "MODE", 0, 17.19f, 2.22f, 427.76f, 579.58f, 0.00f },
        { "SYNC", 0, 17.19f, 2.22f, 214.65f, 579.58f, 0.00f },
        { "1", 0, 17.19f, 0.00f, 84.02f, 109.91f, 0.00f },
        { "2", 0, 17.19f, 0.00f, 84.02f, 162.79f, 0.00f },
        { "3", 0, 17.19f, 0.00f, 84.02f, 217.74f, 0.00f },
        { "4", 0, 17.19f, 0.00f, 84.02f, 270.62f, 0.00f },
        { "5", 0, 17.19f, 0.00f, 84.02f, 324.54f, 0.00f },
        { "6", 0, 17.19f, 0.00f, 84.02f, 378.46f, 0.00f },
        { "7", 0, 17.19f, 0.00f, 84.02f, 432.37f, 0.00f },
        { "EIGHT", 1, 36.40f, 6.07f, 308.75f, 614.86f, 0.00f },
        { "ECHO", 1, 36.40f, 6.07f, 308.75f, 653.23f, 0.00f },
        { "TAP", 0, 17.19f, 2.22f, 147.12f, 873.04f, 0.00f },
        { "BYPASS", 0, 17.19f, 2.22f, 473.70f, 873.04f, 0.00f },
        { "X2", 1, 34.38f, 2.02f, 308.75f, 786.93f, 0.00f },
        { "OUT A", 0, 14.16f, 1.62f, 39.94f, 479.03f, 90.00f },
        { "IN A", 0, 14.16f, 1.62f, 577.56f, 479.03f, 90.00f },
        { "OUT B", 0, 14.16f, 1.62f, 39.94f, 626.27f, 90.00f },
        { "IN B", 0, 14.16f, 1.62f, 577.56f, 626.27f, 90.00f }
    };
    struct Dot { float x, y, r; };
    const Dot dots[] = { { 170.32f, 180.16f, 1.72f }, { 155.02f, 155.20f, 1.72f }, { 152.73f, 126.02f, 1.72f }, { 163.93f, 98.98f, 1.72f }, { 186.19f, 79.97f, 1.72f }, { 214.65f, 73.13f, 1.72f }, { 243.12f, 79.97f, 1.72f }, { 265.37f, 98.98f, 1.72f }, { 276.58f, 126.02f, 1.72f }, { 274.28f, 155.20f, 1.72f }, { 258.99f, 180.16f, 1.72f }, { 381.21f, 180.16f, 1.72f }, { 365.91f, 155.20f, 1.72f }, { 363.62f, 126.02f, 1.72f }, { 374.82f, 98.98f, 1.72f }, { 397.08f, 79.97f, 1.72f }, { 425.54f, 73.13f, 1.72f }, { 454.01f, 79.97f, 1.72f }, { 476.26f, 98.98f, 1.72f }, { 487.47f, 126.02f, 1.72f }, { 485.17f, 155.20f, 1.72f }, { 469.87f, 180.16f, 1.72f }, { 170.32f, 348.14f, 1.72f }, { 155.02f, 323.18f, 1.72f }, { 152.73f, 293.99f, 1.72f }, { 163.93f, 266.95f, 1.72f }, { 186.19f, 247.94f, 1.72f }, { 214.65f, 241.11f, 1.72f }, { 243.12f, 247.94f, 1.72f }, { 265.37f, 266.95f, 1.72f }, { 276.58f, 293.99f, 1.72f }, { 274.28f, 323.18f, 1.72f }, { 258.99f, 348.14f, 1.72f }, { 381.21f, 348.14f, 1.72f }, { 365.91f, 323.18f, 1.72f }, { 363.62f, 293.99f, 1.72f }, { 374.82f, 266.95f, 1.72f }, { 397.08f, 247.94f, 1.72f }, { 425.54f, 241.11f, 1.72f }, { 454.01f, 247.94f, 1.72f }, { 476.26f, 266.95f, 1.72f }, { 487.47f, 293.99f, 1.72f }, { 485.17f, 323.18f, 1.72f }, { 469.87f, 348.14f, 1.72f } };
    struct Line { float x0, y0, x1, y1, w; };
    const Line lines[] = { { 387.71f, 536.70f, 383.42f, 540.99f, 2.02f }, { 373.90f, 514.16f, 368.13f, 516.03f, 2.02f }, { 371.82f, 487.80f, 365.83f, 486.85f, 2.02f }, { 381.94f, 463.37f, 377.03f, 459.81f, 2.02f }, { 402.05f, 446.20f, 399.29f, 440.80f, 2.02f }, { 427.76f, 440.03f, 427.76f, 433.96f, 2.02f }, { 453.46f, 446.20f, 456.22f, 440.80f, 2.02f }, { 473.57f, 463.37f, 478.48f, 459.81f, 2.02f }, { 483.69f, 487.80f, 489.68f, 486.85f, 2.02f }, { 481.61f, 514.16f, 487.38f, 516.03f, 2.02f }, { 467.80f, 536.70f, 472.09f, 540.99f, 2.02f }, { 278.41f, 786.93f, 258.19f, 786.93f, 2.63f }, { 339.09f, 786.93f, 359.31f, 786.93f, 2.63f } };
    struct Tri { float x0, y0, x1, y1, x2, y2; };
    const Tri tris[] = { { 132.77f, 690.47f, 157.04f, 690.47f, 144.91f, 677.85f }, { 459.35f, 678.20f, 483.62f, 678.20f, 471.48f, 690.82f } };
    const float triStroke = 1.82f;
    // motif d'anneaux (eight_echo_motif.svg, repere 4096) : point gauche du SVG -> footswitch TAP, echelle
    const juce::Point<float> motifSvgLeft { 875.429f, 2048.000f }; const float motifScale = 0.139256f;
    const juce::Point<float> logoPos { 308.75f, 874.08f }; const float logoW = 188.09f;
    const juce::Rectangle<float> motifGaps[] = { { 242.25f, 635.71f, 133.00f, 35.03f }, { 122.88f, 862.64f, 48.49f, 20.81f }, { 429.96f, 862.64f, 87.47f, 20.81f }, { 249.23f, 768.14f, 119.05f, 37.58f }, { 125.70f, 670.77f, 38.43f, 26.78f }, { 452.27f, 671.12f, 38.43f, 26.78f }, { 206.62f, 859.19f, 204.27f, 29.77f } };
}
