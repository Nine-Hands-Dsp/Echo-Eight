#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"

using namespace juce;

namespace
{
const Colour kSilk    (0xffe6ecf1);   // serigraphie blanche
const Colour kIce     (0xff96d2ff);   // bleu glace (liseré de la pastille, numero de memoire)
const Colour kX2Lit   (0xffd7eeff);   // X2 allume
const Colour kModeSel (0xffacd6fa);   // nom du mode choisi (bleu un peu plus marque que la serigraphie)
const Colour kPanel   (0xff090e13);   // face de la pastille
const Colour kMenuAccent (0xff8fd0ff);

// index des valeurs suivies pour la ligne d'etat
const char* const kWatch[] = { "elevel", "mix", "feedback", "time", "mode", "long", "sync", "footswitch", "tap" };
constexpr int kNumWatch = 9;

String fr (const char* utf8) { return String (CharPointer_UTF8 (utf8)); }
}

// =============================================================================
PedalView::PedalView (EightEchoProcessor& p) : proc (p)
{
    auto img = [] (const void* d, int n) { return ImageCache::getFromMemory (d, n); };
    bg         = img (BinaryData::background_png, BinaryData::background_pngSize);
    footswitch = img (BinaryData::footswitch_png, BinaryData::footswitch_pngSize);
    pipeOn     = img (BinaryData::pipe_on_png, BinaryData::pipe_on_pngSize);
    ledIce     = img (BinaryData::led_ice_png, BinaryData::led_ice_pngSize);
    ledRed     = img (BinaryData::led_red_png, BinaryData::led_red_pngSize);
    ledGreen   = img (BinaryData::led_green_png, BinaryData::led_green_pngSize);
    ledOrange  = img (BinaryData::led_orange_png, BinaryData::led_orange_pngSize);
    syncOn     = img (BinaryData::sync_on_png, BinaryData::sync_on_pngSize);
    glowTempo  = img (BinaryData::glow_tempo_png, BinaryData::glow_tempo_pngSize);
    glowRed    = img (BinaryData::glow_check_red_png, BinaryData::glow_check_red_pngSize);
    glowGreen  = img (BinaryData::glow_check_green_png, BinaryData::glow_check_green_pngSize);
    glowOrange = img (BinaryData::glow_check_orange_png, BinaryData::glow_check_orange_pngSize);
    glowSync   = img (BinaryData::glow_sync_png, BinaryData::glow_sync_pngSize);
    glowX2     = img (BinaryData::glow_x2_png, BinaryData::glow_x2_pngSize);
    glowSlot[0] = img (BinaryData::glow_slot1_png, BinaryData::glow_slot1_pngSize);
    glowSlot[1] = img (BinaryData::glow_slot2_png, BinaryData::glow_slot2_pngSize);
    glowSlot[2] = img (BinaryData::glow_slot3_png, BinaryData::glow_slot3_pngSize);
    glowSlot[3] = img (BinaryData::glow_slot4_png, BinaryData::glow_slot4_pngSize);
    glowSlot[4] = img (BinaryData::glow_slot5_png, BinaryData::glow_slot5_pngSize);
    glowSlot[5] = img (BinaryData::glow_slot6_png, BinaryData::glow_slot6_pngSize);
    glowSlot[6] = img (BinaryData::glow_slot7_png, BinaryData::glow_slot7_pngSize);

    sansFace = Typeface::createSystemTypefaceFor (BinaryData::LiberationSansBold_ttf, BinaryData::LiberationSansBold_ttfSize);
    monoFace = Typeface::createSystemTypefaceFor (BinaryData::LiberationMonoBold_ttf, BinaryData::LiberationMonoBold_ttfSize);
    popMed   = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    auto svg = [] (const char* d, int n) -> std::unique_ptr<Drawable>
    {
        if (auto xml = XmlDocument::parse (String::fromUTF8 (d, n))) return Drawable::createFromSVG (*xml);
        return nullptr;
    };
    logo  = svg (BinaryData::NineHandsLogo_svg, BinaryData::NineHandsLogo_svgSize);
    motif = svg (BinaryData::eight_echo_motif_svg, BinaryData::eight_echo_motif_svgSize);
    title = svg (BinaryData::eight_echo_title_svg, BinaryData::eight_echo_title_svgSize);
    buildPrint();
    setInterceptsMouseClicks (true, false);

    const char* ids[5] = { "elevel", "mix", "feedback", "time", "mode" };
    for (int k = 0; k < 5; ++k)
        knobs.push_back ({ ids[k], layout::knobPos[k], layout::knobR, k == 4, nullptr, 0.5f, 0.5 });
    for (size_t k = 0; k < knobs.size(); ++k)
    {
        auto* par = proc.apvts.getParameter (knobs[k].id);
        knobs[k].def = par->getDefaultValue();
        knobs[k].att = std::make_unique<ParameterAttachment> (*par, [this, k] (float v)
        {
            knobs[k].value = v;
            const auto c = knobs[k].c; const float r = knobs[k].r + 4.0f;
            repaint (Rectangle<float> (c.x - r, c.y - r, r * 2, r * 2).getSmallestIntegerContainer());
            if (knobs[k].isMode) repaint (Rectangle<float> (c.x - 150, c.y - 110, 300, 200).getSmallestIntegerContainer());
        });
        knobs[k].att->sendInitialUpdate();
    }
    longAtt = std::make_unique<ParameterAttachment> (*proc.apvts.getParameter ("long"), [this] (float v)
        { longOn = v > 0.5f; repaint (layout::glow_x2.getSmallestIntegerContainer().expanded (4)); });
    longAtt->sendInitialUpdate();
    syncAtt = std::make_unique<ParameterAttachment> (*proc.apvts.getParameter ("sync"), [this] (float v)
        { syncParam = v > 0.5f; repaint (layout::glow_sync.getSmallestIntegerContainer().expanded (4)); });
    syncAtt->sendInitialUpdate();
    for (int i = 0; i < kNumWatch; ++i) lastVals[(size_t) i] = proc.apvts.getRawParameterValue (kWatch[i])->load();
    lastLooper = proc.looperState.load();
    startTimerHz (30);
}

PedalView::~PedalView() { stopTimer(); }

void PedalView::setParam (const char* id, float v)
{
    if (auto* par = proc.apvts.getParameter (id))
    {
        par->beginChangeGesture(); par->setValueNotifyingHost (par->convertTo0to1 (v)); par->endChangeGesture();
    }
}

void PedalView::showStatus (double ms) { statusUntil = Time::getMillisecondCounterHiRes() + ms; }

// ----------------------------------------------------------------------------
//  Serigraphie vectorielle (unites du plugin) : construite une fois
// ----------------------------------------------------------------------------
static Path textPath (const Typeface::Ptr& face, const layout::Txt& t)
{
    const Font font (FontOptions (face).withPointHeight (t.em));
    const String s (t.s);
    float total = 0.0f;
    for (int i = 0; i < s.length(); ++i)
        total += GlyphArrangement::getStringWidth (font, String::charToString (s[i])) + (i > 0 ? t.track : 0.0f);
    const float base = (font.getAscent() - font.getDescent()) * 0.5f;     // centre vertical entre ascendante et descendante
    GlyphArrangement ga;
    float x = -total * 0.5f;
    for (int i = 0; i < s.length(); ++i)
    {
        const String ch = String::charToString (s[i]);
        ga.addLineOfText (font, ch, x, base);
        x += GlyphArrangement::getStringWidth (font, ch) + t.track;
    }
    Path p; ga.createPath (p);
    p.applyTransform (AffineTransform::rotation (-t.rot * MathConstants<float>::pi / 180.0f).translated (t.x, t.y));
    return p;
}

void PedalView::buildPrint()
{
    printPath.clear(); x2Path.clear(); knockPath.clear();
    for (const auto& t : layout::texts) printPath.addPath (textPath (t.font == 1 ? monoFace : sansFace, t));
    for (const auto& d : layout::dots) printPath.addEllipse (d.x - d.r, d.y - d.r, d.r * 2.0f, d.r * 2.0f);
    const int nLines = (int) (sizeof (layout::lines) / sizeof (layout::lines[0]));
    for (int i = 0; i < nLines; ++i)
    {
        const auto& l = layout::lines[i];
        Path seg; seg.startNewSubPath (l.x0, l.y0); seg.lineTo (l.x1, l.y1);
        Path out; PathStrokeType (l.w, PathStrokeType::mitered, PathStrokeType::butt).createStrokedPath (out, seg);
        (i >= nLines - 2 ? x2Path : printPath).addPath (out);          // les 2 derniers traits s'allument avec X2
    }
    for (const auto& t : layout::tris)
    {
        Path tri; tri.addTriangle (t.x0, t.y0, t.x1, t.y1, t.x2, t.y2);
        Path out; PathStrokeType (layout::triStroke, PathStrokeType::curved, PathStrokeType::rounded).createStrokedPath (out, tri);
        printPath.addPath (out);
    }
    // X2 : lettrage d'origine en traits (extremites droites)
    {
        int k = 0;
        for (int n : layout::x2Lens)
        {
            Path s;
            for (int i = 0; i < n; ++i, ++k)
            {
                const float x = layout::x2Pts[2 * k], y = layout::x2Pts[2 * k + 1];
                if (i == 0) s.startNewSubPath (x, y); else s.lineTo (x, y);
            }
            Path out; PathStrokeType (layout::x2Stroke, PathStrokeType::curved, PathStrokeType::butt).createStrokedPath (out, s);
            x2Path.addPath (out);
        }
    }
    // titre EIGHT ECHO (SVG fourni) cale dans son cadre
    if (title != nullptr)
    {
        auto tp = title->getOutlineAsPath();
        const auto b = tp.getBounds();
        if (! b.isEmpty())
            tp.applyTransform (RectanglePlacement (RectanglePlacement::stretchToFit).getTransformToFit (b, layout::titleRect));
        printPath.addPath (tp);
    }
    // zones que le motif d'anneaux evite : chaque inscription (texte, triangle, titre, X2, logo, nom des modes)
    knockPath.addPath (printPath);
    knockPath.addPath (x2Path);
    if (logo != nullptr)
    {
        auto lp = logo->getOutlineAsPath();
        const auto vb = lp.getBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        lp.applyTransform (RectanglePlacement (RectanglePlacement::centred).getTransformToFit (
            vb, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }));
        knockPath.addPath (lp);
    }
}

// ----------------------------------------------------------------------------
//  Caches (timer seulement, anti-gel) : fond et serigraphie a la resolution de l'ecran
// ----------------------------------------------------------------------------
void PedalView::rebuildCaches (float ppu)
{
    ppu = jlimit (0.3f, 8.0f, ppu);
    if (bgCache.isValid() && std::abs (ppu - cachePpu) < 0.002f) return;
    cachePpu = ppu;
    const int W = roundToInt (imgW * ppu), H = roundToInt (imgH * ppu);
    bgCache = (W >= bg.getWidth()) ? bg : bg.rescaled (W, H, Graphics::highResamplingQuality);

    const auto toPx = AffineTransform::scale ((float) W / imgW, (float) H / imgH);
    // motif d'anneaux, interrompu a knockMargin du contour de chaque inscription
    Image mot (Image::ARGB, W, H, true);
    if (motif != nullptr)
    {
        Graphics mg (mot);
        motif->draw (mg, 0.95f, AffineTransform::translation (-layout::motifSvgLeft.x, -layout::motifSvgLeft.y)
                                    .scaled (layout::motifScale)
                                    .translated (layout::fsTap.x, layout::fsTap.y)
                                    .followedBy (toPx));
    }
    {
        Image mask (Image::SingleChannel, W, H, true);
        {
            Graphics kg (mask);
            kg.setColour (Colours::white);
            kg.fillPath (knockPath, toPx);
            kg.strokePath (knockPath, PathStrokeType (layout::knockMargin * 2.0f, PathStrokeType::curved, PathStrokeType::rounded), toPx);
        }
        Image::BitmapData md (mot, Image::BitmapData::readWrite), kd (mask, Image::BitmapData::readOnly);
        for (int y = 0; y < H; ++y)
        {
            auto* mp = md.getLinePointer (y);
            const auto* kp = kd.getLinePointer (y);
            for (int x = 0; x < W; ++x)
            {
                const int k = kp[x * kd.pixelStride];
                if (k == 0) continue;
                auto* px = mp + x * md.pixelStride;
                const int keep = 255 - k;
                for (int c = 0; c < 4; ++c) px[c] = (uint8) ((px[c] * keep + 127) / 255);
            }
        }
    }
    Image pr (Image::ARGB, W, H, true);
    {
        Graphics pg (pr);
        pg.drawImageAt (mot, 0, 0);
        pg.addTransform (toPx);
        pg.setColour (kSilk);
        pg.fillPath (printPath);
        pg.fillPath (x2Path);                          // X2 eteint : serigraphie blanche
        if (logo != nullptr)
        {
            const auto vb = logo->getDrawableBounds();
            const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
            logo->drawWithin (pg, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 0.94f);
        }
    }
    printCache = pr;
    repaint();
}

// ----------------------------------------------------------------------------
Rectangle<float> PedalView::modeLabelRect (int i, Justification& just) const
{
    const auto c = knobs[4].c;
    const float a = modeAngle (i), s = std::sin (a);
    const Point<float> p (c.x + layout::modeLabelR * s, c.y - layout::modeLabelR * std::cos (a));
    const float w = 80.0f, h = layout::modeFont * 1.5f;
    if (s > 0.3f)  { just = Justification::centredLeft;  return { p.x, p.y - h * 0.5f, w, h }; }
    if (s < -0.3f) { just = Justification::centredRight; return { p.x - w, p.y - h * 0.5f, w, h }; }
    just = Justification::centred;
    return { p.x - w * 0.5f, p.y - layout::modeFont * 0.45f - h * 0.5f, w, h };
}

int PedalView::knobAt (Point<float> p) const
{
    for (size_t k = 0; k < knobs.size(); ++k)
        if (p.getDistanceFrom (knobs[k].c) <= knobs[k].r) return (int) k;
    return -1;
}

int PedalView::modeLabelAt (Point<float> p) const
{
    const Font f (FontOptions (sansFace).withPointHeight (layout::modeFont));
    for (int i = 0; i < wiga::kNumModes; ++i)
    {
        Justification j (Justification::centred);
        auto r = modeLabelRect (i, j);
        const float tw = GlyphArrangement::getStringWidth (f, wiga::modeName (i));
        if (j == Justification::centredLeft) r.setWidth (tw);
        else if (j == Justification::centredRight) r.setLeft (r.getRight() - tw);
        else r = r.withSizeKeepingCentre (tw, r.getHeight());
        if (r.expanded (3, 2).contains (p) && p.getDistanceFrom (knobs[4].c) > knobs[4].r) return i;
    }
    return -1;
}

int PedalView::slotAt (Point<float> p) const
{
    for (int i = 0; i < EightEchoProcessor::kNumSlots; ++i)
        if (p.x > layout::boxRect.getX() && p.x < 112.0f && std::abs (p.y - layout::slotPos[i].y) < 24.0f) return i;
    return -1;
}

int PedalView::presetZoneAt (Point<float> p) const
{
    const auto r = layout::statusRect;
    if (! r.contains (p)) return 0;
    if (p.x < r.getX() + 34.0f) return 1;
    if (p.x > r.getRight() - 34.0f) return 3;
    return 2;
}

// ----------------------------------------------------------------------------
void PedalView::mouseMove (const MouseEvent& e)
{
    const auto p = e.position;
    hoverZone = presetZoneAt (p);
    if (hoverZone != drawnHover) { drawnHover = hoverZone; repaint (layout::statusRect.getSmallestIntegerContainer().expanded (3)); }
    const bool hot = hoverZone != 0 || knobAt (p) >= 0 || modeLabelAt (p) >= 0 || slotAt (p) >= 0
                  || p.getDistanceFrom (layout::syncPos) < layout::syncR || p.getDistanceFrom (layout::x2Pos) < 36
                  || p.getDistanceFrom (layout::triUp) < 16 || p.getDistanceFrom (layout::triDown) < 16
                  || onFootswitch (p, layout::fsTap) || onFootswitch (p, layout::fsBypass);
    setMouseCursor (hot ? MouseCursor::PointingHandCursor : MouseCursor::NormalCursor);
}

void PedalView::mouseExit (const MouseEvent&)
{
    hoverZone = 0;
    if (drawnHover != 0) { drawnHover = 0; repaint (layout::statusRect.getSmallestIntegerContainer().expanded (3)); }
}

// commande apprenable en MIDI sous la souris (memes zones que les clics)
int PedalView::learnIndexAt (Point<float> p) const
{
    auto idx = [] (const char* id) { return EightEchoProcessor::learnIndexOf (id); };
    if (onFootswitch (p, layout::fsBypass)) return idx ("footswitch");
    if (onFootswitch (p, layout::fsTap))    return idx ("tap");
    if (p.getDistanceFrom (layout::x2Pos) < 36)          return idx ("long");
    if (p.getDistanceFrom (layout::syncPos) < layout::syncR) return idx ("sync");
    if (p.getDistanceFrom (layout::triUp) < 16)   return idx ("prev");
    if (p.getDistanceFrom (layout::triDown) < 16) return idx ("next");
    if (modeLabelAt (p) >= 0 && knobAt (p) < 0) return idx ("mode");
    if (int k = knobAt (p); k >= 0) return EightEchoProcessor::learnIndexOf (knobs[(size_t) k].id);
    return -1;
}

void PedalView::mouseDown (const MouseEvent& e)
{
    const auto p = e.position;
    if (e.mods.isPopupMenu()) { if (onBackgroundRightClick) onBackgroundRightClick (e); return; }

    if (int z = presetZoneAt (p); z != 0)
    {
        statusUntil = 0.0; learnedUntil = 0.0;            // la ligne d'etat ne bloque pas : la barre de presets revient
        if (z == 2) { if (onPresetMenu) onPresetMenu(); }
        else
        {
            const int n = proc.getNumPrograms();
            const int cur = proc.getCurrentProgram();
            proc.setCurrentProgram (((cur + (z == 1 ? -1 : 1)) % n + n) % n);
        }
        return;
    }
    if (onFootswitch (p, layout::fsBypass))
    {
        pressed = BYPASSFS;
        if (auto* par = proc.apvts.getParameter ("footswitch")) { par->beginChangeGesture(); par->setValueNotifyingHost (1.0f); }
        repaint(); return;
    }
    if (onFootswitch (p, layout::fsTap))
    {
        pressed = TAPFS; tapPressTime = Time::getMillisecondCounterHiRes(); twistSent = false;
        if (auto* par = proc.apvts.getParameter ("tap")) { par->beginChangeGesture(); par->setValueNotifyingHost (1.0f); }
        repaint(); return;
    }
    if (p.getDistanceFrom (layout::x2Pos) < 36) { setParam ("long", longOn ? 0.0f : 1.0f); return; }
    // SYNC : cale le delay sur le tempo du DAW (re-clic = retour au TIME / tap)
    if (p.getDistanceFrom (layout::syncPos) < layout::syncR) { syncAtt->setValueAsCompleteGesture (syncParam ? 0.0f : 1.0f); return; }
    if (p.getDistanceFrom (layout::triUp) < 16 || p.getDistanceFrom (layout::triDown) < 16)
    {
        const int n = EightEchoProcessor::kNumSlots, cur = proc.getCurrentSlot();
        proc.loadSlot (p.getDistanceFrom (layout::triUp) < 16 ? (cur + n - 1) % n : (cur + 1) % n);
        repaint(); return;
    }
    if (int s = slotAt (p); s >= 0)
    {
        slotPress = s; slotPressTime = Time::getMillisecondCounterHiRes(); slotSaved = false;
        repaint(); return;
    }
    if (int m = modeLabelAt (p); m >= 0 && knobAt (p) < 0) { setParam ("mode", (float) m); return; }
    if (int k = knobAt (p); k >= 0)
    {
        dragKnob = k; dragStartY = p.y; dragStartVal = knobs[(size_t) k].value;
        dragStartIndex = roundToInt (knobs[(size_t) k].value);
        knobs[(size_t) k].att->beginGesture();
    }
}

void PedalView::mouseDrag (const MouseEvent& e)
{
    if (dragKnob < 0) return;
    auto& k = knobs[(size_t) dragKnob];
    const float dy = dragStartY - e.position.y;
    if (k.isMode)
    {
        const int idx = jlimit (0, wiga::kNumModes - 1, dragStartIndex + (int) std::floor (dy / 18.0f + 0.5f));
        k.att->setValueAsPartOfGesture ((float) idx);
    }
    else
    {
        const float sens = e.mods.isShiftDown() ? 900.0f : 260.0f;   // Maj = reglage fin
        auto* par = proc.apvts.getParameter (k.id);
        const float v = jlimit (0.0f, 1.0f, dragStartVal + dy / sens);
        k.att->setValueAsPartOfGesture (par->convertFrom0to1 (v));
    }
}

void PedalView::mouseUp (const MouseEvent&)
{
    if (dragKnob >= 0) { knobs[(size_t) dragKnob].att->endGesture(); dragKnob = -1; }
    if (pressed == BYPASSFS)
        if (auto* par = proc.apvts.getParameter ("footswitch")) { par->setValueNotifyingHost (0.0f); par->endChangeGesture(); }
    if (pressed == TAPFS)
    {
        if (auto* par = proc.apvts.getParameter ("tap")) { par->setValueNotifyingHost (0.0f); par->endChangeGesture(); }
        if (twistSent) setParam ("twist", 0.0f);
    }
    if (slotPress >= 0 && ! slotSaved) proc.loadSlot (slotPress);    // clic court = rappel
    slotPress = -1; slotSaved = false;
    pressed = NONE; twistSent = false;
    repaint();
}

void PedalView::saveToSlot (int i)
{
    proc.saveSlot (i);
    flashSlot = i; flashStart = anim;
    showStatus (1500.0);
    repaint();
}

void PedalView::mouseDoubleClick (const MouseEvent& e)
{
    if (int k = knobAt (e.position); k >= 0 && ! knobs[(size_t) k].isMode)
    {
        auto* par = proc.apvts.getParameter (knobs[(size_t) k].id);
        knobs[(size_t) k].att->setValueAsCompleteGesture (par->convertFrom0to1 ((float) knobs[(size_t) k].def));
    }
}

void PedalView::mouseWheelMove (const MouseEvent& e, const MouseWheelDetails& w)
{
    if (int k = knobAt (e.position); k >= 0)
    {
        auto& kn = knobs[(size_t) k];
        auto* par = proc.apvts.getParameter (kn.id);
        if (kn.isMode)
            kn.att->setValueAsCompleteGesture ((float) jlimit (0, wiga::kNumModes - 1, roundToInt (kn.value) + (w.deltaY > 0 ? 1 : -1)));
        else
            kn.att->setValueAsCompleteGesture (par->convertFrom0to1 (jlimit (0.0f, 1.0f, par->getValue() + w.deltaY * 0.08f)));
    }
}

void PedalView::askRepaint (Rectangle<float> r)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (r.getSmallestIntegerContainer().expanded (2));
}

// ----------------------------------------------------------------------------
//  Textes de la pastille
// ----------------------------------------------------------------------------
String PedalView::presetLine() const
{
    const int slot = proc.getCurrentSlot();
    return String (slot + 1) + fr (" \xc2\xb7 ") + proc.getCurrentName() + (proc.slotMatchesCurrent (slot) ? "" : " *");
}

String PedalView::buildStatus() const
{
    const double now = Time::getMillisecondCounterHiRes();
    if (const int lt = proc.learnTarget.load(); lt >= 0)
        return fr ("MIDI LEARN \xc2\xb7 ") + EightEchoProcessor::learnable (lt).name;
    if (now < learnedUntil) return learnedText;
    if (flashSlot >= 0) return fr ("SAUV\xc3\x89 EN M\xc3\x89MOIRE ") + String (flashSlot + 1);
    if (slotPress >= 0 && ! slotSaved && now - slotPressTime > 250.0)
        return fr ("MAINTENIR POUR SAUVER EN M\xc3\x89MOIRE ") + String (slotPress + 1);

    auto& s = proc.apvts;
    const int mode = (int) s.getRawParameterValue ("mode")->load();
    auto pc = [&] (const char* id) { return String (roundToInt (s.getRawParameterValue (id)->load() * 100.0f)) + " %"; };
    auto ms = [this] { return String (roundToInt (proc.effectiveDelayMs.load())) + " ms"; };
    const char* loopSt[] = { "VIDE", "ENREGISTREMENT", "LECTURE", "OVERDUB", "" };
    auto looper = [&]
    {
        const int st = jlimit (0, 4, proc.looperState.load());
        return String ("LOOP ") + (st == 4 ? fr ("ARR\xc3\x8aT") : String (loopSt[st])) + "  " + String (proc.loopSeconds.load(), 1).replaceCharacter ('.', ',') + " s / 40 s";
    };
    switch (lastChanged)
    {
        case 0: return (mode == wiga::LOOP ? String ("VOLUME LOOP  ") : String ("E.LEVEL  ")) + pc ("elevel");
        case 1: return "MIX  " + pc ("mix");
        case 2: return (mode == wiga::GLT ? String ("DEPTH  ") : String ("FEEDBACK  ")) + pc ("feedback");
        case 3: return "TIME  " + ms() + (proc.hostLocked.load() ? fr ("  \xc2\xb7  SYNC ") + String (roundToInt (proc.hostBpm.load())) + " BPM" : String());
        case 4: return String ("MODE  ") + wiga::modeName (mode);
        case 5: return longOn ? fr ("X2  ACTIV\xc3\x89") : fr ("X2  D\xc3\x89SACTIV\xc3\x89");
        case 6: return ! syncParam ? fr ("SYNC  D\xc3\x89SACTIV\xc3\x89")
                     : proc.hostLocked.load() ? "SYNC  " + String (roundToInt (proc.hostBpm.load())) + " BPM  " + fr ("\xc2\xb7  ") + ms()
                                              : fr ("SYNC  \xc2\xb7  PAS DE TEMPO DU DAW");
        case 7:
        {
            if (mode == wiga::LOOP) return looper();
            const int ls = proc.ledState.load();
            return (ls == EightEchoProcessor::LED_RED || ls == EightEchoProcessor::LED_REDGREEN_BLINK) ? String ("EFFET ACTIF") : String ("BYPASS");
        }
        case 8:
            if (mode == wiga::LOOP) return looper();
            if (proc.twistAmount.load() > 0.05f) return "TWIST";
            return "TAP  " + ms();
        case 9: return looper();
        default: return {};
    }
}

// ----------------------------------------------------------------------------
void PedalView::timerCallback()
{
    if (onTimerTick) onTimerTick();   // anti-gel Windows : l'editeur verifie le moteur de rendu et refait ses caches

    const double nowMs = Time::getMillisecondCounterHiRes();
    if (repaintAskedMs > 0.0 && isShowing() && nowMs - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0;
        if (onRepaintStuck) onRepaintStuck();
        repaint();
    }

    anim += 1.0f / 30.0f;
    if (const int learned = proc.lastLearned.exchange (-1); learned >= 0)
    {
        learnedText = String (EightEchoProcessor::learnable (learned).name) + " = CC " + String (proc.ccNum[learned].load());
        learnedUntil = nowMs + 2000.0;
        showStatus (2000.0);
    }
    if (proc.learnTarget.load() >= 0) showStatus (300.0);

    // TAP maintenu : TWIST (et, en LOOP, maintien 2 s = effacer)
    if (pressed == TAPFS && ! twistSent)
    {
        const double held = nowMs - tapPressTime;
        const bool loop = (int) proc.apvts.getRawParameterValue ("mode")->load() == wiga::LOOP;
        if ((! loop && held > 450.0) || (loop && held > 2000.0))
        {
            if (auto* par = proc.apvts.getParameter ("twist")) { par->beginChangeGesture(); par->setValueNotifyingHost (1.0f); par->endChangeGesture(); }
            twistSent = true;
        }
    }
    // memoire maintenue 1 s : sauvegarde du reglage en cours
    if (slotPress >= 0 && ! slotSaved && nowMs - slotPressTime > 1000.0) { saveToSlot (slotPress); slotSaved = true; }
    if (slotPress >= 0 && ! slotSaved && nowMs - slotPressTime > 250.0) showStatus (400.0);
    if (flashSlot >= 0 && anim - flashStart > 1.2f) flashSlot = -1;

    // quel reglage vient de bouger (souris, molette, automation, MIDI, tap, footswitch) : la ligne d'etat le montre
    for (int i = 0; i < kNumWatch; ++i)
    {
        const float v = proc.apvts.getRawParameterValue (kWatch[i])->load();
        if (std::abs (v - lastVals[(size_t) i]) > 1.0e-4f)
        {
            lastVals[(size_t) i] = v;
            if (i == 7 || i == 8) { if (v > 0.5f) { lastChanged = i; showStatus(); } }   // appui seulement
            else { lastChanged = i; showStatus(); }
        }
    }
    if (const int ls = proc.looperState.load(); ls != lastLooper)
    {
        lastLooper = ls;
        if ((int) proc.apvts.getRawParameterValue ("mode")->load() == wiga::LOOP) { lastChanged = 9; showStatus(); }
    }
    if (pressed != NONE || dragKnob >= 0) showStatus();
    if (lastChanged == 9 && (proc.looperState.load() == 1 || proc.looperState.load() == 3)) showStatus();   // enregistrement : compteur en direct

    // pastille : fondu croise (~120 ms a l'apparition, ~300 ms au retour de la barre de presets)
    const float target = nowMs < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (target - statusAlpha) * (target > statusAlpha ? 0.45f : 0.25f);
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;
    statusText = statusAlpha > 0.0f || target > 0.0f ? buildStatus() : statusText;
    presetText = presetLine();
    if (std::abs (statusAlpha - drawnStatusAlpha) > 0.003f || (statusAlpha > 0.0f && statusText != drawnStatusText) || presetText != drawnPreset)
    {
        drawnStatusAlpha = statusAlpha; drawnStatusText = statusText; drawnPreset = presetText;
        askRepaint (layout::statusRect.expanded (3.0f));
    }

    auto changed = [] (float& drawn, float now) { if (std::abs (drawn - now) < 0.002f) return false; drawn = now; return true; };

    // tubes des memoires 1 a 7
    const int cur = proc.getCurrentSlot();
    for (int i = 0; i < EightEchoProcessor::kNumSlots; ++i)
        if (changed (drawnLed[(size_t) i], ledBrightness (i, cur)))
            askRepaint (layout::glowSlot[i].getUnion ({ layout::pipeOrigin[i].x, layout::pipeOrigin[i].y, layout::pipeW, layout::pipeH }));

    if (changed (drawnSync, syncParam ? syncAlpha() : 0.0f)) askRepaint (layout::glow_sync);
    if (changed (drawnTempo, tempoAmount())) askRepaint (layout::glow_tempo);
    const auto argb = checkColour().getARGB();
    if (argb != drawnCheck) { drawnCheck = argb; askRepaint (layout::glow_check_red); }
}

// ----------------------------------------------------------------------------
//  Dessin
// ----------------------------------------------------------------------------
Colour PedalView::checkColour() const
{
    const bool on = std::fmod (anim * 2.5f, 1.0f) < 0.5f;
    const float ph = proc.tapBlinkPhase.load();
    const Colour red (0xffff3324), green (0xff3dff7a), orange (0xffffa424);
    switch (proc.ledState.load())
    {
        case EightEchoProcessor::LED_RED:    return red;
        case EightEchoProcessor::LED_GREEN:  return green;
        case EightEchoProcessor::LED_ORANGE: return orange;
        case EightEchoProcessor::LED_RED_BLINK: return proc.tapModeActive.load() ? (ph < 0.25f ? red : Colours::transparentBlack) : (on ? red : Colours::transparentBlack);
        case EightEchoProcessor::LED_GREEN_BLINK: return on ? green : Colours::transparentBlack;
        case EightEchoProcessor::LED_REDGREEN_BLINK: return ph < 0.25f ? red : green;
        default: return Colours::transparentBlack;
    }
}

float PedalView::ledBrightness (int i, int cur) const
{
    float b = 0.0f;
    if (i == flashSlot) b = std::fmod ((anim - flashStart) * 5.0f, 1.0f) < 0.5f ? 1.0f : 0.15f;   // confirmation
    else if (i == slotPress && ! slotSaved)
    {
        const float held = (float) ((Time::getMillisecondCounterHiRes() - slotPressTime) / 1000.0);
        b = held > 0.25f ? 0.3f + 0.7f * jlimit (0.0f, 1.0f, (held - 0.25f) / 0.75f) * (0.6f + 0.4f * std::sin (anim * 14.0f)) : 1.0f;
    }
    else if (i == cur) b = proc.slotMatchesCurrent (cur) ? 1.0f : 0.45f + 0.15f * std::sin (anim * 3.0f);   // memoire modifiee : adoucie
    return b;
}

float PedalView::beatFlash() const { return jlimit (0.0f, 1.0f, 1.0f - proc.tapBlinkPhase.load() * 4.0f); }

float PedalView::syncAlpha() const
{
    return proc.hostLocked.load() ? 0.86f + 0.14f * beatFlash()                // respire au tempo
                                  : 0.25f + 0.15f * std::sin (anim * 4.0f);   // pas de tempo du DAW
}

float PedalView::tempoAmount() const
{
    const bool twisting = proc.twistAmount.load() > 0.05f;
    const bool accent = proc.tapAccent.load();
    const float peak = (! accent || proc.tapBeat.load() == 0) ? 1.0f : 0.55f;
    return twisting ? (std::fmod (anim * 12.0f, 1.0f) < 0.5f ? 1.0f : 0.15f) : peak * beatFlash();
}

void PedalView::drawKnobPointer (Graphics& g, const Knob& k)
{
    // potard photo (dans le fond, reflets fixes) : seul le repere blanc tourne
    const float a = k.isMode ? modeAngle (jlimit (0, wiga::kNumModes - 1, roundToInt (k.value)))
                             : degreesToRadians (-135.0f + 270.0f * k.value);
    const float R = k.r;
    const Point<float> dir (std::sin (a), -std::cos (a));
    Path line; line.startNewSubPath (k.c + dir * (0.42f * R)); line.lineTo (k.c + dir * (0.88f * R));
    const float lw = 0.062f * R;
    g.setColour (Colours::black.withAlpha (0.43f));
    g.strokePath (line, PathStrokeType (lw * 1.15f, PathStrokeType::mitered, PathStrokeType::butt), AffineTransform::translation (0.5f, 0.7f));
    g.setColour (Colour (0xffecf0f3));
    g.strokePath (line, PathStrokeType (lw, PathStrokeType::mitered, PathStrokeType::butt));
}

static void drawAt (Graphics& g, const Image& img, Rectangle<float> r, float opacity)
{
    if (! img.isValid() || opacity <= 0.003f) return;
    g.setOpacity (jlimit (0.0f, 1.0f, opacity));
    g.drawImage (img, r);
    g.setOpacity (1.0f);
}

static Rectangle<float> sq (Point<float> c, float s) { return { c.x - s * 0.5f, c.y - s * 0.5f, s, s }; }

// Pastille unique (regle NINE HANDS | DSP) : barre de presets au repos ; des qu'un reglage bouge, la ligne d'etat
// prend sa place en fondu croise (meme pastille, meme police Poppins Medium 23), puis s'efface ~2,5 s apres.
void PedalView::drawPill (Graphics& g)
{
    const auto r = layout::statusRect;
    const float rad = r.getHeight() * 0.5f;
    const float a = statusAlpha, pa = 1.0f - a;
    g.setColour (kPanel.withAlpha (0.92f));
    g.fillRoundedRectangle (r, rad);
    g.setColour (kIce.withAlpha (hoverZone != 0 && pa > 0.5f ? 0.65f : 0.45f));
    g.drawRoundedRectangle (r.reduced (0.75f), rad - 0.75f, 1.5f);

    const Font f (FontOptions (popMed).withPointHeight (23.0f));
    const float aw = 34.0f;
    if (pa > 0.0f)
    {
        auto arrow = [&] (bool left, bool hot)
        {
            const float cx = left ? r.getX() + aw * 0.5f + 3.0f : r.getRight() - aw * 0.5f - 3.0f, cy = r.getCentreY(), t = 5.5f;
            Path p;
            if (left) p.addTriangle (cx + t * 0.8f, cy - t, cx + t * 0.8f, cy + t, cx - t * 0.8f, cy);
            else      p.addTriangle (cx - t * 0.8f, cy - t, cx - t * 0.8f, cy + t, cx + t * 0.8f, cy);
            g.setColour (Colours::white.withAlpha ((hot ? 1.0f : 0.6f) * pa));
            g.fillPath (p);
        };
        arrow (true, hoverZone == 1);
        arrow (false, hoverZone == 3);
        // numero de memoire (bleu glace) · nom du preset (blanc), reduit au plus a 60 % puis tronque
        const int slot = proc.getCurrentSlot();
        const String num (slot + 1), sep (fr ("  \xc2\xb7  ")), name = presetText.fromFirstOccurrenceOf (fr (" \xc2\xb7 "), false, false);
        const float avail = r.getWidth() - 2.0f * aw;
        float k = 1.0f;
        auto width = [&] (float kk)
        {
            const Font ff = f.withHeight (f.getHeight() * kk);
            return GlyphArrangement::getStringWidth (ff, num) + GlyphArrangement::getStringWidth (ff, sep) + GlyphArrangement::getStringWidth (ff, name);
        };
        while (k > 0.6f && width (k) > avail) k -= 0.02f;
        const Font ff = f.withHeight (f.getHeight() * k);
        const float wn = GlyphArrangement::getStringWidth (ff, num), ws = GlyphArrangement::getStringWidth (ff, sep);
        const float wt = jmin (GlyphArrangement::getStringWidth (ff, name), avail - wn - ws);
        float x = r.getCentreX() - (wn + ws + wt) * 0.5f;
        g.setFont (ff);
        g.setColour (kIce.withAlpha (pa));
        g.drawText (num, Rectangle<float> (x, r.getY(), wn + 1.0f, r.getHeight()), Justification::centredLeft, false); x += wn;
        g.setColour (Colour (0xff96a0aa).withAlpha (pa));
        g.drawText (sep, Rectangle<float> (x, r.getY(), ws + 1.0f, r.getHeight()), Justification::centredLeft, false); x += ws;
        g.setColour (kSilk.withAlpha ((hoverZone == 2 ? 1.0f : 0.94f) * pa));
        g.drawText (name, Rectangle<float> (x, r.getY(), wt + 1.0f, r.getHeight()), Justification::centredLeft, true);
    }
    if (a > 0.0f)
    {
        g.setFont (f);
        g.setColour (kSilk.withAlpha (a));
        g.drawFittedText (statusText, r.reduced (rad, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
}

void PedalView::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    const Rectangle<float> frame (0.0f, 0.0f, imgW, imgH);

    // fond (cache a la resolution de l'ecran, ou image d'origine en attendant le timer)
    g.setImageResamplingQuality (bgCache.isValid() ? Graphics::lowResamplingQuality : Graphics::mediumResamplingQuality);
    g.drawImage (bgCache.isValid() ? bgCache : bg, frame);
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);

    // lumieres sur la facade (sous la serigraphie)
    const int cur = proc.getCurrentSlot();
    float led[7];
    const float gl = proc.glowLevel.load();     // menu Glow : intensite des halos sur la plaque
    for (int i = 0; i < 7; ++i) { led[i] = ledBrightness (i, cur); drawAt (g, glowSlot[(size_t) i], layout::glowSlot[i], led[i] * gl); }
    const float tempo = tempoAmount();
    drawAt (g, glowTempo, layout::glow_tempo, tempo * gl);
    const auto cc = checkColour();
    const bool green = cc == Colour (0xff3dff7a), orange = cc == Colour (0xffffa424);
    if (! cc.isTransparent()) drawAt (g, green ? glowGreen : orange ? glowOrange : glowRed, layout::glow_check_red, gl);
    const float sa = syncParam ? syncAlpha() : 0.0f;
    drawAt (g, glowSync, layout::glow_sync, sa * gl);
    if (longOn) drawAt (g, glowX2, layout::glow_x2, gl);

    // serigraphie (cache) ; en attendant le cache, les inscriptions seules
    g.setImageResamplingQuality (Graphics::lowResamplingQuality);
    if (printCache.isValid()) g.drawImage (printCache, frame);
    else { g.setColour (kSilk); g.fillPath (printPath); g.fillPath (x2Path); }
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    if (longOn) { g.setColour (kX2Lit); g.fillPath (x2Path); }

    // noms des modes autour du potard MODE (le mode choisi en bleu)
    {
        const int modeIdx = jlimit (0, wiga::kNumModes - 1, roundToInt (knobs[4].value));
        g.setFont (FontOptions (sansFace).withPointHeight (layout::modeFont));
        for (int i = 0; i < wiga::kNumModes; ++i)
        {
            Justification just (Justification::centred);
            const auto rr = modeLabelRect (i, just);
            g.setColour (i == modeIdx ? kModeSel : kSilk);
            g.drawText (wiga::modeName (i), rr, just, false);
        }
    }

    // footswitches (au-dessus du motif) ; enfonce : bouton assombri
    for (auto c : { layout::fsTap, layout::fsBypass }) g.drawImage (footswitch, sq (c, layout::fsS));
    if (pressed != NONE)
    {
        const auto c = pressed == TAPFS ? layout::fsTap : layout::fsBypass;
        const float r = layout::footR * 0.98f;
        g.setColour (Colours::black.withAlpha (0.25f));
        g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
    }

    // LED, tubes, SYNC
    drawAt (g, ledIce, sq (layout::ledTempo, layout::ledS), tempo);
    if (! cc.isTransparent()) drawAt (g, green ? ledGreen : orange ? ledOrange : ledRed, sq (layout::ledCheck, layout::ledS), 1.0f);
    for (int i = 0; i < 7; ++i) drawAt (g, pipeOn, { layout::pipeOrigin[i].x, layout::pipeOrigin[i].y, layout::pipeW, layout::pipeH }, led[i]);
    drawAt (g, syncOn, sq (layout::syncPos, layout::syncS), sa);

    for (auto& k : knobs) drawKnobPointer (g, k);
    drawPill (g);
}

// =============================================================================
EightEchoEditor::EightEchoEditor (EightEchoProcessor& p) : AudioProcessorEditor (&p), proc (p), pedal (p)
{
    popReg  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize);
    popMed  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    popBold = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    menuLnf.f = { popReg, popMed, popBold };
    proc.glowLevel = (float) NineHandsGlow::percent (JucePlugin_Name) / 100.0f;   // Glow intensity : commun a toutes les fenetres (settings.xml)
    setLookAndFeel (&menuLnf);

    addAndMakeVisible (pedal);
    pedal.onBackgroundRightClick = [this] (const MouseEvent& e) { showMenu (pedal.learnIndexAt (e.position)); };
    pedal.onPresetMenu = [this] { showPresetMenu(); };
    pedal.onTimerTick = [this] { tick(); };
    pedal.onRepaintStuck = [this] { lastPeer = nullptr; useSoftwareRenderer(); repaint(); };

    // l'ordre compte : setResizable() d'abord, puis la contrainte stricte (coin ET hote l'utilisent)
    setResizable (true, true);
    const int defW = roundToInt ((float) defaultH * layout::frameW / layout::frameH);
    constrainer.setMinimumSize (defW, defaultH);
    constrainer.setMaximumSize (roundToInt ((float) maxH * layout::frameW / layout::frameH), maxH);
    constrainer.setFixedAspectRatio ((double) layout::frameW / (double) layout::frameH);
    constrainer.setMinimumOnscreenAmounts (0x10000, 0x10000, 0x10000, 0x10000);
    setConstrainer (&constrainer);
    hostLock.setLimits (defW, defaultH, roundToInt ((float) maxH * layout::frameW / layout::frameH), maxH);
    setOpaque (true);                      // anti-gel : l'hote ne redessine jamais ce qui est derriere la fenetre
    // taille : celle du projet pour cette instance si elle existe, sinon celle choisie dans « Default size (new windows) »
    const int h = sizeHeight (NineHandsWindow::openIndex (JucePlugin_Name, proc.uiSizeIdx.load(), numSizes));
    setScaledHeight (h);
    rebuildCaches();
}

EightEchoEditor::~EightEchoEditor()
{
    PopupMenu::dismissAllActiveMenus();
    setLookAndFeel (nullptr);
}

int EightEchoEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { defaultH, roundToInt (refH * 0.75f), refH };
    return h[jlimit (0, numSizes - 1, idx)];
}

void EightEchoEditor::setScaledHeight (int h)
{
    h = jlimit (defaultH, maxH, h);
    setSize (roundToInt ((float) h * layout::frameW / layout::frameH), h);
    hostLock.enforce();
}

//==============================================================================
// Anti-gel v2 (NINE HANDS | DSP) :
//  1. moteur de rendu logiciel force sur Windows, applique a chaque nouvelle fenetre hote (peer)
//     et reverifie toutes les secondes, jamais en boucle ;
//  2. aucun calcul lourd dans paint() : fond et serigraphie mis en cache par le timer seulement,
//     apres stabilisation de la taille ou quand l'echelle d'affichage change (au plus toutes les 250 ms) ;
//  3. chien de garde : redessin demande non servi en 1,5 s -> moteur de rendu reapplique, tout redessine ;
//  4. cote audio : aucun appel a l'hote depuis le thread audio (voir PluginProcessor).
void EightEchoEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw) peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void EightEchoEditor::parentHierarchyChanged() { useSoftwareRenderer(); hostLock.track (*this); }
void EightEchoEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

float EightEchoEditor::physicalScale() const
{
    if (forcedScale > 0.0f) return forcedScale;
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

void EightEchoEditor::tick()
{
    const double now = Time::getMillisecondCounterHiRes();
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }
    hostLock.track (*this);
    if (now - lastGlowReadMs > 3000.0)       // Glow intensity : commun a toutes les fenetres (jamais dans paint)
    {
        lastGlowReadMs = now;
        const float gl = (float) NineHandsGlow::percent (JucePlugin_Name) / 100.0f;
        if (std::abs (gl - proc.glowLevel.load()) > 0.001f) { proc.glowLevel = gl; pedal.repaint(); }
    }
    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }
}

void EightEchoEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    if (getHeight() <= 0) return;
    cacheScale = sc; cacheH = getHeight();
    pedal.rebuildCaches ((float) getHeight() / layout::frameH * sc);
}

void EightEchoEditor::resized()
{
    // anti-gel : jamais de setSize ici ; la contrainte stricte garde la taille minimale et les proportions
    const float s = (float) getHeight() / layout::frameH;
    pedal.setBounds (0, 0, (int) std::ceil (layout::frameW), (int) layout::frameH);
    pedal.setTransform (AffineTransform::scale (s));
    // seules les tailles choisies au menu sont enregistrees (pas celles tirees au coin)
    resizeSettle = 4;      // les caches seront refaits quand la taille sera stable
}

void EightEchoEditor::paint (Graphics& g)
{
    g.fillAll (Colour (0xff111112));     // autour des jacks : le fond de l'image est transparent
}

// ----------------------------------------------------------------------------
//  Menus (design d'Octopus, ouverts la ou l'on clique)
// ----------------------------------------------------------------------------
void EightEchoEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, kMenuAccent, "Presets", pedal.presetLine());
    m.addSectionHeader ("Factory presets > memory " + String (proc.getCurrentSlot() + 1));
    for (int i = 0; i < proc.getNumPrograms(); ++i)
        m.addItem (100 + i, proc.getProgramName (i), true, proc.getCurrentProgram() == i && proc.getCurrentName() == proc.getProgramName (i));
    m.addSeparator();
    PopupMenu load, save;
    for (int i = 0; i < EightEchoProcessor::kNumSlots; ++i)
    {
        load.addItem (600 + i, "Memory " + String (i + 1) + "  " + proc.getSlotName (i), true, proc.getCurrentSlot() == i);
        save.addItem (700 + i, "Memory " + String (i + 1) + "  (overwrite " + proc.getSlotName (i) + ")");
    }
    m.addSubMenu ("Load memory", load);
    m.addSubMenu ("Save current settings to memory", save);
    const auto bar = localAreaToGlobal (layout::statusRect.transformedBy (pedal.getTransform()).toNearestInt());
    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (bar),
        [safe = Component::SafePointer<EightEchoEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& pr = safe->proc;
            if (r >= 100 && r < 600) pr.setCurrentProgram (r - 100);
            else if (r >= 600 && r < 600 + EightEchoProcessor::kNumSlots) pr.loadSlot (r - 600);
            else if (r >= 700 && r < 700 + EightEchoProcessor::kNumSlots) safe->pedal.saveToSlot (r - 700);
        });
}

PopupMenu EightEchoEditor::buildContextMenu (int learnTarget)
{
    using namespace NineHandsMenu;
    auto& s = proc.apvts;
    auto val = [&s] (const char* id) { return s.getRawParameterValue (id)->load(); };
    auto ccText = [this] (int i) { const int n = proc.ccNum[i].load(); return n >= 0 ? "CC " + String (n) : String ("not assigned"); };
    auto ctlName = [] (int i) { return String (EightEchoProcessor::learnable (i).name); };
    const int lt = proc.learnTarget.load();
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    if (learnTarget >= 0)      // menu d'une commande (tronc commun) : en-tete, MIDI Learn, Clear MIDI, Cancel MIDI learn
    {
        const int type = EightEchoProcessor::learnable (learnTarget).type;
        const int ico = (type == EightEchoProcessor::kContinuous || type == EightEchoProcessor::kSelector) ? icoKnob : icoSwitch;
        addHeader (m, menuLnf.f, ico, kMenuAccent, ctlName (learnTarget), "MIDI: " + ccText (learnTarget));
        m.addItem (800 + learnTarget, "MIDI Learn: " + ctlName (learnTarget), true, lt == learnTarget);
        m.addItem (850 + learnTarget, "Clear MIDI: " + ctlName (learnTarget), proc.ccNum[learnTarget].load() >= 0);
        m.addItem (898, "Cancel MIDI learn", lt >= 0);
        return m;
    }

    addHeader (m, menuLnf.f, icoPedal, kMenuAccent, "Eight Echo", "Digital delay  v" + String (JucePlugin_VersionString));
    // presets : usine (chargees dans la memoire en cours), memoires de la pedale = presets utilisateur
    PopupMenu presets, load, save;
    for (int i = 0; i < proc.getNumPrograms(); ++i)
        presets.addItem (100 + i, String (i + 1) + ". " + proc.getProgramName (i), true, proc.getCurrentProgram() == i && proc.getCurrentName() == proc.getProgramName (i));
    for (int i = 0; i < EightEchoProcessor::kNumSlots; ++i)
    {
        load.addItem (600 + i, "Memory " + String (i + 1) + " : " + proc.getSlotName (i), true, proc.getCurrentSlot() == i);
        save.addItem (700 + i, "Memory " + String (i + 1) + "  (overwrite " + proc.getSlotName (i) + ")");
    }
    m.addSubMenu ("Factory presets", presets);
    m.addSubMenu ("Load user preset", load);
    m.addSubMenu ("Save user preset", save);
    m.addSeparator();

    PopupMenu stereo, div;
    const char* st[] = { "Independent (default)", "Wide stereo", "Panning (ping-pong)" };
    for (int i = 0; i < 3; ++i) stereo.addItem (200 + i, st[i], true, (int) val ("stereo") == i);
    auto& dn = EightEchoProcessor::tapDivisionNames();
    for (int i = 0; i < dn.size(); ++i) div.addItem (300 + i, dn[i], true, (int) val ("division") == i);
    m.addSubMenu ("Stereo mode", stereo);
    m.addSubMenu ("Tap division", div);
    m.addItem (601, "Carryover (trails when bypassed)", true, val ("carryover") > 0.5f);
    m.addItem (602, "Sync delay to host tempo", true, val ("sync") > 0.5f);
    m.addSeparator();

    PopupMenu midi, exp;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < EightEchoProcessor::kNumLearn; ++i)
        midi.addItem (800 + i, "Learn: " + ctlName (i) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    midi.addItem (898, "Cancel MIDI learn", lt >= 0);
    midi.addItem (897, "Clear all MIDI assignments");
    midi.addSeparator();
    NineHandsWindow::addMidiFootswitchMode (midi, proc.midiFsLatching.load());
    exp.addItem (401, "Expression > E.LEVEL", true, val ("expLevel") > 0.5f);
    exp.addItem (402, "Expression > FEEDBACK", true, val ("expFeedback") > 0.5f);
    exp.addItem (403, "Expression > TIME", true, val ("expTime") > 0.5f);
    midi.addSubMenu ("Expression pedal (EXP parameter)", exp);
    midi.addSeparator();
    NineHandsWindow::addProgramChangeInfo (midi);
    m.addSubMenu ("MIDI", midi);
    m.addSeparator();

    const char* names[numSizes] = { "60 %", "75 %", "100 %" };
    const int heights[numSizes] = { sizeHeight (0), sizeHeight (1), sizeHeight (2) };
    m.addSubMenu ("Plugin size", NineHandsWindow::sizeMenu (JucePlugin_Name, numSizes, names, heights, getHeight()));
    m.addSubMenu ("Glow intensity", NineHandsWindow::glowMenu (roundToInt (proc.glowLevel.load() * 100.0f)));
    return m;
}

void EightEchoEditor::showMenu (int learnTarget)
{
    auto m = buildContextMenu (learnTarget);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),       // menu clic droit : toujours la ou l'on clique
        [safe = Component::SafePointer<EightEchoEditor> (this)] (int r)
    {
        if (safe == nullptr || r == 0) return;
        auto& ed = *safe;
        auto& pr = ed.proc;
        auto set = [&pr] (const char* id, float v)
        {
            if (auto* par = pr.apvts.getParameter (id)) { par->beginChangeGesture(); par->setValueNotifyingHost (par->convertTo0to1 (v)); par->endChangeGesture(); }
        };
        auto toggle = [&pr, &set] (const char* id) { set (id, pr.apvts.getRawParameterValue (id)->load() > 0.5f ? 0.0f : 1.0f); };
        int inst = pr.uiSizeIdx.load();
        const int sz = NineHandsWindow::handleSize (r, JucePlugin_Name, numSizes, inst);
        if (sz >= 0) { pr.uiSizeIdx = inst; ed.setScaledHeight (sizeHeight (sz)); return; }
        if (const int pc = NineHandsWindow::handleGlow (r, JucePlugin_Name)) { pr.glowLevel.store ((float) pc / 100.0f); ed.pedal.repaint(); return; }
        if (r >= 100 && r < 200) pr.setCurrentProgram (r - 100);
        else if (r >= 200 && r < 300) set ("stereo", (float) (r - 200));
        else if (r >= 300 && r < 400) set ("division", (float) (r - 300));
        else if (r == 401) toggle ("expLevel");
        else if (r == 402) toggle ("expFeedback");
        else if (r == 403) toggle ("expTime");
        else if (r >= 600 && r < 600 + EightEchoProcessor::kNumSlots) pr.loadSlot (r - 600);
        else if (r >= 700 && r < 700 + EightEchoProcessor::kNumSlots) ed.pedal.saveToSlot (r - 700);
        else if (r == 601) toggle ("carryover");
        else if (r == 602) toggle ("sync");
        else if (r == NineHandsWindow::idLatch || r == NineHandsWindow::idMomentary) pr.midiFsLatching = r == NineHandsWindow::idLatch;
        else if (r >= 800 && r < 800 + EightEchoProcessor::kNumLearn) pr.learnTarget.store (r - 800);
        else if (r >= 850 && r < 850 + EightEchoProcessor::kNumLearn)
        {
            pr.ccNum[r - 850].store (-1);
            if (pr.learnTarget.load() == r - 850) pr.learnTarget.store (-1);
        }
        else if (r == 898) pr.learnTarget.store (-1);
        else if (r == 897) { pr.learnTarget.store (-1); for (int i = 0; i < EightEchoProcessor::kNumLearn; ++i) pr.ccNum[i].store (-1); }
    });
}
