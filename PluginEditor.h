#pragma once
#include <juce_audio_processors/juce_audio_processors.h>
#include "PluginProcessor.h"
#include "Layout.h"
#include "NineHandsMenu.h"
#include <array>

// =============================================================================
//  Interface Eight Echo v2 (NINE HANDS | DSP) : pedale plein cadre (fond 1235 x 1800 px).
//  Repere de dessin = repere du plugin (Layout.h, 617,5 x 900 unites), mis a l'echelle de la fenetre.
//  Fond (boitier, potards, jacks, LED eteintes) en image ; serigraphie (textes, graduations, titre, X2, motif
//  d'anneaux qui s'arrete autour des inscriptions, logo) dessinee en vectoriel dans un cache a la resolution de l'ecran ;
//  lumieres (tubes des memoires, LED, SYNC, X2) en calques alpha precalcules ; pastille presets / ligne d'etat.
// =============================================================================

class PedalView : public juce::Component, private juce::Timer
{
public:
    explicit PedalView (EightEchoProcessor&);
    ~PedalView() override;

    static constexpr float imgW = layout::frameW, imgH = layout::frameH;

    void paint (juce::Graphics&) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseDoubleClick (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;
    void saveToSlot (int i);
    int  learnIndexAt (juce::Point<float>) const;   // commande apprenable sous la souris (-1 = aucune)
    void rebuildCaches (float pixelsPerUnit);       // appele par le timer de l'editeur seulement (anti-gel)
    bool cachesValid() const { return bgCache.isValid(); }
    void showStatus (double ms = 2500.0);
    juce::String presetLine() const;

    std::function<void (const juce::MouseEvent&)> onBackgroundRightClick;
    std::function<void()> onPresetMenu;
    std::function<void()> onTimerTick;      // appele a chaque tic du timer de l'interface (anti-gel Windows)
    std::function<void()> onRepaintStuck;   // chien de garde (anti-gel v2) : un redessin demande n'est pas arrive

private:
    struct Knob
    {
        juce::String id; juce::Point<float> c; float r; bool isMode;
        std::unique_ptr<juce::ParameterAttachment> att; float value = 0.5f; double def = 0.5;
    };

    EightEchoProcessor& proc;
    juce::Image bg, footswitch, pipeOn, ledIce, ledRed, ledGreen, ledOrange, syncOn;
    juce::Image glowTempo, glowRed, glowGreen, glowOrange, glowSync, glowX2;
    std::array<juce::Image, 7> glowSlot;
    juce::Typeface::Ptr sansFace, monoFace, popMed;
    std::unique_ptr<juce::Drawable> logo, motif, title;
    juce::Path printPath, x2Path, knockPath;
    juce::Image bgCache, printCache;               // caches a la resolution de l'ecran (refaits par le timer)
    float cachePpu = 0.0f;

    std::vector<Knob> knobs;
    std::unique_ptr<juce::ParameterAttachment> longAtt, syncAtt;
    bool longOn = false, syncParam = false;

    // etat souris
    int dragKnob = -1; float dragStartY = 0, dragStartVal = 0; int dragStartIndex = 0;
    enum Pressed { NONE, TAPFS, BYPASSFS };
    Pressed pressed = NONE; double tapPressTime = 0; bool twistSent = false;
    // memoires : clic court = rappel, clic maintenu 1 s = sauvegarde
    int slotPress = -1; double slotPressTime = 0; bool slotSaved = false;
    int flashSlot = -1; float flashStart = 0;
    float anim = 0;
    int hoverZone = 0, drawnHover = -1;            // pastille : 1 fleche gauche, 2 nom, 3 fleche droite

    // pastille : barre de presets au repos, ligne d'etat pendant un reglage
    juce::String statusText, drawnStatusText { "\x01" }, presetText, drawnPreset { "\x01" };
    double statusUntil = 0.0;
    float statusAlpha = 0.0f, drawnStatusAlpha = -1.0f;
    std::array<float, 9> lastVals {};
    int lastChanged = -1, lastLooper = -1;
    juce::String learnedText; double learnedUntil = 0.0;

    // dernier etat reellement dessine : on ne redessine une zone que si elle a change
    std::array<float, 7> drawnLed { -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f };
    float drawnSync = -1.0f, drawnTempo = -1.0f;
    juce::uint32 drawnCheck = 0x12345678;
    // anti-gel v2 : suivi des redessins demandes par le timer (chien de garde)
    double lastPaintMs = 0.0, repaintAskedMs = 0.0;
    void askRepaint (juce::Rectangle<float> r);

    void timerCallback() override;
    void buildPrint();
    int  knobAt (juce::Point<float>) const;
    int  modeLabelAt (juce::Point<float>) const;
    int  slotAt (juce::Point<float>) const;
    int  presetZoneAt (juce::Point<float>) const;
    juce::Rectangle<float> modeLabelRect (int i, juce::Justification& just) const;
    static float modeAngle (int i) { return juce::degreesToRadians (-135.0f + 27.0f * (float) i); }
    bool onFootswitch (juce::Point<float> p, juce::Point<float> c) const { return p.getDistanceFrom (c) < layout::footR * 1.35f; }

    void setParam (const char* id, float v);
    void drawKnobPointer (juce::Graphics&, const Knob&);
    void drawPill (juce::Graphics&);
    juce::String buildStatus() const;
    juce::Colour checkColour() const;
    float ledBrightness (int slot, int cur) const;
    float beatFlash() const;
    float syncAlpha() const;
    float tempoAmount() const;
};

// Contrainte de taille stricte : jamais plus petit que la taille par defaut, proportions bloquees.
class StrictMinConstrainer : public juce::ComponentBoundsConstrainer
{
public:
    void checkBounds (juce::Rectangle<int>& b, const juce::Rectangle<int>& prev, const juce::Rectangle<int>& limits,
                      bool top, bool left, bool bottom, bool right) override
    {
        juce::ComponentBoundsConstrainer::checkBounds (b, prev, limits, top, left, bottom, right);
        const int mw = getMinimumWidth(), mh = getMinimumHeight();
        if (b.getWidth() < mw || b.getHeight() < mh)
        {
            if (left) b.setLeft (b.getRight() - mw); else b.setWidth (mw);
            if (top)  b.setTop (b.getBottom() - mh); else b.setHeight (mh);
        }
        const int w = juce::roundToInt ((double) b.getHeight() * (double) layout::frameW / (double) layout::frameH);
        if (left) b.setLeft (b.getRight() - w); else b.setWidth (w);
    }
};

class EightEchoEditor : public juce::AudioProcessorEditor
{
public:
    explicit EightEchoEditor (EightEchoProcessor&);
    ~EightEchoEditor() override;
    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;
    void visibilityChanged() override;

    // Pedale simple NINE HANDS | DSP : fenetre = pedale plein cadre. Hauteurs : 493 (defaut, « 60 % ») / 719 / 958, jusqu'a 150 %.
    static constexpr int defaultH = 493, refH = 958, maxH = refH * 3 / 2;
    static constexpr int numSizes = 3;
    static int sizeHeight (int idx);
    void setScaledHeight (int h);
    void forceRenderScale (float sc) { forcedScale = sc; rebuildCaches (sc); }   // captures (outil de rendu)

private:
    EightEchoProcessor& proc;
    PedalView pedal;
    StrictMinConstrainer constrainer;
    NineHandsMenu::MenuLnf menuLnf;
    juce::Typeface::Ptr popReg, popMed, popBold;
    void useSoftwareRenderer();
    void tick();                                   // appele par le timer de la pedale (30 Hz)
    void rebuildCaches (float scale = 0.0f);
    float physicalScale() const;
    void showMenu (int learnTarget = -1);          // learnTarget >= 0 : clic droit sur une commande
    void showPresetMenu();
    float forcedScale = 0.0f, cacheScale = 0.0f;
    int cacheH = 0;
    int resizeSettle = 0;
    void* lastPeer = nullptr;
    double lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0;
    bool sizeFromProject = false;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (EightEchoEditor)
};
