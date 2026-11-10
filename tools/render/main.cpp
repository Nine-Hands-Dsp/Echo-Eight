// Captures PNG de la fenetre reelle d'Eight Echo (meme code que le plugin), pour l'apercu et la notice.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
using namespace juce;

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    const String out = argc > 1 ? argv[1] : ".";
    EightEchoProcessor proc;
    proc.prepareToPlay (48000.0, 256);
    std::unique_ptr<AudioProcessorEditor> ed (proc.createEditor());
    auto* eed = static_cast<EightEchoEditor*> (ed.get());
    std::printf ("taille par defaut : %d x %d\n", ed->getWidth(), ed->getHeight());

    auto pump = [] (int n) { for (int i = 0; i < n; ++i) MessageManager::getInstance()->runDispatchLoopUntil (35); };
    auto set = [&] (const char* id, float v) { if (auto* p = proc.apvts.getParameter (id)) p->setValueNotifyingHost (p->convertTo0to1 (v)); };
    auto process = [&] (int n) { AudioBuffer<float> b (2, 256); MidiBuffer m; for (int i = 0; i < n; ++i) { b.clear(); proc.processBlock (b, m); } };
    auto save = [&] (const String& name, float scale)
    {
        auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, scale);
        File f (out + "/" + name + ".png"); f.deleteFile();
        FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        std::printf ("%s (%d x %d)\n", f.getFullPathName().toRawUTF8(), img.getWidth(), img.getHeight());
    };

    // fenetre par defaut (« 60 % »), barre de presets au repos
    eed->forceRenderScale (2.0f);
    process (40); pump (140);
    save ("eight_echo_default", 2.0f);

    // pedale exacte 1800 px : memoire 1, effet actif, au repos
    eed->setScaledHeight (900);
    eed->forceRenderScale (2.0f);
    process (40); pump (140);
    save ("eight_echo_exact", 2.0f);

    // reglage en cours : la ligne d'etat remplace la barre de presets
    set ("elevel", 0.64f); process (4); pump (14);
    save ("eight_echo_status", 2.0f);

    // X2 et SYNC allumes, mode TAPE, memoire 3
    pump (120);
    proc.loadSlot (2); set ("long", 1.0f); set ("sync", 1.0f); set ("mode", 3.0f); process (20); pump (120);
    save ("eight_echo_x2_sync", 2.0f);
    // memoire 3 modifiee (tube adouci, astérisque dans la barre)
    set ("long", 0.0f); set ("sync", 0.0f); proc.loadSlot (2); process (4); pump (10);
    set ("feedback", 0.75f); process (4); pump (110);
    save ("eight_echo_mem_modified", 2.0f);
    return 0;
}
