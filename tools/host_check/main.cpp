// Test hote d'Eight Echo : charge le VST3 compile comme REAPER et verifie
//  1. qu'au lancement la memoire 1 est chargee (potards = memoire 1, LED pleine)
//  2. que la queue du delay est toujours la apres chaque operation d'hote
#include <juce_audio_utils/juce_audio_utils.h>
#include <thread>
#include <atomic>
#include <juce_audio_processors_headless/format_types/VST3_SDK/pluginterfaces/vst/ivstaudioprocessor.h>
#include <juce_audio_processors_headless/format_types/VST3_SDK/pluginterfaces/vst/ivstcomponent.h>
using namespace juce;
static int failures = 0;
static void check (bool ok, const String& w) { std::printf ("%s %s\n", ok ? "  OK  " : "  FAIL", w.toRawUTF8()); if (! ok) ++failures; }

static const double SR = 48000.0;
static Random rng (1234);

static AudioProcessorParameter* findParam (AudioPluginInstance& p, const String& name)
{
    for (auto* q : p.getParameters()) if (q->getName (64) == name) return q;
    return nullptr;
}

// envoie un coup de bruit de 50 ms puis du silence ; renvoie l'energie RMS de la sortie entre 150 et 600 ms
// (le son direct est fini : ce qui reste, ce sont les repetitions du delay)
static float tailRms (AudioPluginInstance& p, int block, bool variable = false, double winEnd = 0.6)
{
    const int total = (int) (SR * (winEnd + 0.2));
    AudioBuffer<float> b (2, 4096); MidiBuffer m;
    double acc = 0; int cnt = 0;
    for (int pos = 0; pos < total; )
    {
        int n = variable ? jlimit (1, block, 1 + rng.nextInt (block)) : block;   // jamais plus que la taille annoncee (regle VST3)
        n = jmin (n, total - pos);
        b.setSize (2, n, false, false, true);
        for (int i = 0; i < n; ++i)
        {
            const float x = (pos + i) < (int) (SR * 0.05) ? (rng.nextFloat() * 2 - 1) * 0.5f : 0.0f;
            b.setSample (0, i, x); b.setSample (1, i, x);
        }
        m.clear();
        p.processBlock (b, m);
        for (int i = 0; i < n; ++i)
            if (pos + i > (int) (SR * 0.15) && pos + i < (int) (SR * winEnd))
            { const float l = b.getSample (0, i), r = b.getSample (1, i); acc += l * l + r * r; ++cnt; }
        pos += n;
    }
    return cnt > 0 ? (float) std::sqrt (acc / cnt) : 0.0f;
}

static void silence (AudioPluginInstance& p, double seconds, int block = 512)
{
    AudioBuffer<float> b (2, block); MidiBuffer m;
    for (int k = 0; k < (int) (seconds * SR / block); ++k) { b.clear(); m.clear(); p.processBlock (b, m); }
}

int main (int argc, char** argv)
{
    std::setvbuf (stdout, nullptr, _IONBF, 0);
    ScopedJuceInitialiser_GUI init;
    AudioPluginFormatManager fm; fm.addFormat (std::make_unique<VST3PluginFormat>());
    OwnedArray<PluginDescription> found; VST3PluginFormat vst3;
    vst3.findAllTypesForFile (found, argv[1]);
    check (found.size() == 1, "VST3 trouve : " + (found.isEmpty() ? String() : found[0]->name + " / " + found[0]->manufacturerName));
    if (found.isEmpty()) return 1;
    String err;
    auto inst = fm.createPluginInstance (*found[0], SR, 512, err);
    check (inst != nullptr, "instance creee " + err);
    if (! inst) return 1;
    auto& p = *inst;

    // ---------- 1. lancement : memoire 1 (Bread & Butter : STANDARD, E.LEVEL 45 %, FEEDBACK 38 %, TIME 60 %)
    auto txt = [&] (const char* n) { auto* q = findParam (p, n); return q ? q->getCurrentValueAsText() : String ("?"); };
    auto val = [&] (const char* n) { auto* q = findParam (p, n); return q ? q->getValue() : -1.0f; };
    std::printf ("  au lancement : Mode=%s  E.Level=%s  Feedback=%s  Time=%s  programme=%d (%s)\n",
                 txt ("Mode").toRawUTF8(), txt ("E.Level").toRawUTF8(), txt ("Feedback").toRawUTF8(), txt ("Time").toRawUTF8(),
                 p.getCurrentProgram(), p.getProgramName (p.getCurrentProgram()).toRawUTF8());
    check (txt ("Mode") == "STANDARD" && std::abs (val ("E.Level") - 0.45f) < 0.002f && std::abs (val ("Feedback") - 0.38f) < 0.002f
           && std::abs (val ("Time") - 0.60f) < 0.002f, "memoire 1 (Bread & Butter) chargee au lancement");
    check (p.getProgramName (p.getCurrentProgram()) == "Bread & Butter", "programme affiche par l'hote = Bread & Butter");

    p.prepareToPlay (SR, 512);
    const float ref = tailRms (p, 512);
    std::printf ("  queue de reference : %.4f\n", ref);
    check (ref > 0.01f, "le delay repete (reference)");
    auto still = [&] (const String& what, int block = 512, bool variable = false)
    {
        silence (p, 1.0, jmax (1, block));
        const float t = tailRms (p, block, variable);
        check (t > ref * 0.5f, what + " : delay toujours present (" + String (t, 4) + ")");
    };

    // ---------- 2. operations d'hote (ce que REAPER fait quand on ajoute un effet, bypass, recalcul PDC...)
    p.releaseResources(); p.prepareToPlay (SR, 512);                      still ("desactivation / reactivation");
    p.releaseResources(); p.prepareToPlay (SR, 1024);                     still ("nouvelle taille de bloc 1024", 1024);
    still ("blocs de taille variable", 1024, true);
    p.releaseResources(); p.prepareToPlay (SR, 4096);                     still ("blocs de 4096", 4096);
    p.releaseResources(); p.prepareToPlay (SR, 512);
    p.releaseResources(); p.prepareToPlay (44100.0, 256); p.releaseResources(); p.prepareToPlay (SR, 512); still ("changement de frequence");
    {
        AudioBuffer<float> b (2, 512); MidiBuffer m;
        for (int k = 0; k < 200; ++k) { b.clear(); m.clear(); p.processBlockBypassed (b, m); }
        still ("bypass de l'hote puis retour");
    }
    if (auto* bp = p.getBypassParameter())
    {
        bp->setValueNotifyingHost (1.0f); silence (p, 1.0); bp->setValueNotifyingHost (0.0f);
        still ("parametre Bypass de l'hote");
    }
    { MemoryBlock st; p.getStateInformation (st); p.setStateInformation (st.getData(), (int) st.getSize()); still ("etat relu (vst_chunk)"); }
    p.reset();                                                             still ("reset() de l'hote");
    p.setNonRealtime (true); p.setNonRealtime (false);                     still ("rendu hors temps reel");
    {
        AudioBuffer<float> b (2, 512); MidiBuffer m; b.clear();
        b.setSample (0, 10, std::numeric_limits<float>::quiet_NaN()); b.setSample (1, 20, std::numeric_limits<float>::infinity());
        p.processBlock (b, m);
        still ("echantillon NaN / infini en entree");
    }
    {
        AudioBuffer<float> b (2, 512); MidiBuffer m;
        for (int k = 0; k < 20; ++k) { for (int i = 0; i < 512; ++i) { b.setSample (0, i, 40.0f); b.setSample (1, i, -40.0f); } m.clear(); p.processBlock (b, m); }
        still ("entree enorme (+32 dB)");
    }
    {   // Program Change MIDI qui traverse Octopus
        AudioBuffer<float> b (2, 512); MidiBuffer m; b.clear();
        m.addEvent (MidiMessage::programChange (1, 0), 0); p.processBlock (b, m);
        still ("Program Change MIDI recu");
    }
    {   // le footswitch BYPASS de la pedale : off puis on
        auto* on = findParam (p, "Effect On");
        if (on) { on->setValueNotifyingHost (0.0f); silence (p, 1.0); on->setValueNotifyingHost (1.0f); still ("pedale coupee puis rallumee"); }
    }
    {   // changement de disposition (mono -> stereo) comme quand REAPER recalcule la chaine
        p.releaseResources();
        auto layout = p.getBusesLayout();
        auto mono = layout; mono.inputBuses.getReference (0) = AudioChannelSet::mono();
        p.setBusesLayout (mono); p.prepareToPlay (SR, 512); silence (p, 0.2);
        p.releaseResources(); p.setBusesLayout (layout); p.prepareToPlay (SR, 512);
        still ("disposition mono puis stereo");
    }
    // preset de l'hote (TrackFX_SetPresetByIndex) puis etat rendu (Octopus lit les noms de presets)
    {
        MemoryBlock st; p.getStateInformation (st);
        for (int i = 0; i < p.getNumPrograms(); ++i) p.setCurrentProgram (i);
        p.setStateInformation (st.getData(), (int) st.getSize());
        still ("lecture des presets par Octopus puis etat rendu");
    }

    // chaque mode : entree enorme puis NaN, la sortie doit rester valide et le delay revenir
    if (auto* mp = findParam (p, "Mode"))
    {
        const int nm = mp->getNumSteps();
        for (int m = 0; m < nm; ++m)
        {
            mp->setValueNotifyingHost ((float) m / (float) (nm - 1));
            if (mp->getCurrentValueAsText() == "LOOP") continue;
            AudioBuffer<float> b (2, 512); MidiBuffer mm; bool finite = true;
            for (int k = 0; k < 40; ++k)
            {
                for (int i = 0; i < 512; ++i) { const float x = (k == 20 && i == 7) ? std::numeric_limits<float>::quiet_NaN() : (rng.nextFloat() * 2 - 1) * 20.0f; b.setSample (0, i, x); b.setSample (1, i, -x); }
                mm.clear(); p.processBlock (b, mm);
                for (int i = 0; i < 512; ++i) finite = finite && std::isfinite (b.getSample (0, i)) && std::isfinite (b.getSample (1, i));
            }
            silence (p, 2.0);
            const float t = tailRms (p, 512, false, mp->getCurrentValueAsText() == "REVERSE" ? 4.5 : 0.6);   // REVERSE : repetitions longues
            check (finite && t > 0.002f, "mode " + mp->getCurrentValueAsText() + " : sortie valide, delay present (" + String (t, 4) + ")");
        }
    }

    // ---------- 3. bypass facon REAPER / Octopus STOMP pendant que le son tourne :
    //  thread audio qui traite en continu ; thread de messages qui fait setProcessing(false/true) (bypass VST3),
    //  le parametre Bypass, et la fenetre ouverte. Doit rester rapide, sans plantage, et le delay doit revenir.
    {
        Steinberg::Vst::IAudioProcessor* ap = nullptr;
        Steinberg::Vst::IComponent* comp = p.getVST3Client() != nullptr ? p.getVST3Client()->getIComponentPtr() : nullptr;
        if (comp != nullptr) comp->queryInterface (Steinberg::Vst::IAudioProcessor::iid, (void**) &ap);
        check (ap != nullptr, "interface VST3 IAudioProcessor");
        std::unique_ptr<AudioProcessorEditor> ed (p.createEditorIfNeeded());
        if (ed) ed->setVisible (true);
        std::atomic<bool> run { true }, processing { true }; std::atomic<int> blocks { 0 }; std::atomic<bool> bad { false };
        std::thread audio ([&]
        {
            AudioBuffer<float> b (2, 256); MidiBuffer m; Random r (7);
            while (run)
            {
                for (int i = 0; i < 256; ++i) { const float x = (r.nextFloat() * 2 - 1) * 0.3f; b.setSample (0, i, x); b.setSample (1, i, x); }
                m.clear();
                if (processing) p.processBlock (b, m);      // l'hote ne traite pas pendant le bypass
                for (int i = 0; i < 256; ++i) if (! std::isfinite (b.getSample (0, i))) bad = true;
                ++blocks;
                std::this_thread::sleep_for (std::chrono::microseconds (2000));
            }
        });
        double worst = 0;
        for (int k = 0; k < 40; ++k)
        {
            MessageManager::getInstance()->runDispatchLoopUntil (40);
            processing = false;
            const double t0 = Time::getMillisecondCounterHiRes();
            if (ap) ap->setProcessing (false);                  // REAPER : bypass (peut venir du thread d'interface)
            worst = jmax (worst, Time::getMillisecondCounterHiRes() - t0);
            MessageManager::getInstance()->runDispatchLoopUntil (40);
            if (ap) ap->setProcessing (true);
            processing = true;
            if (auto* bp = p.getBypassParameter()) { bp->setValueNotifyingHost (k % 2 ? 1.0f : 0.0f); }
        }
        if (auto* bp = p.getBypassParameter()) bp->setValueNotifyingHost (0.0f);
        MessageManager::getInstance()->runDispatchLoopUntil (200);
        run = false; audio.join();
        std::printf ("  setProcessing(false) le plus long : %.2f ms, %d blocs traites\n", worst, blocks.load());
        check (worst < 2.0, "bypass VST3 instantane (setProcessing leger : " + String (worst, 2) + " ms)");
        {   // desactivation / reactivation complete par l'hote (meme frequence) : rapide, sans reallocation
            processing = false;
            double w2 = 0;
            for (int k = 0; k < 5; ++k) { const double t0 = Time::getMillisecondCounterHiRes(); p.reset(); w2 = jmax (w2, Time::getMillisecondCounterHiRes() - t0); }
            processing = true;
            std::printf ("  reactivation complete la plus longue : %.2f ms\n", w2);
            check (w2 < 5.0, "reactivation par l'hote rapide (" + String (w2, 2) + " ms)");
        }
        check (! bad, "sortie toujours valide pendant les bypass");
        if (ed)
        {
            // la fenetre doit toujours repondre : un clic sur BYPASS (pied) coupe puis rallume l'effet
            auto* on = findParam (p, "Effect On");
            const float before = on ? on->getValue() : -1.0f;
            auto* fs = findParam (p, "Footswitch (hold)");
            if (fs) { fs->setValueNotifyingHost (1.0f); silence (p, 0.05, 256); fs->setValueNotifyingHost (0.0f); silence (p, 0.05, 256); }
            for (int i = 0; i < 10; ++i) MessageManager::getInstance()->runDispatchLoopUntil (20);
            check (on != nullptr && on->getValue() != before, "la pedale repond apres les bypass (BYPASS bascule l'effet)");
            if (fs) { fs->setValueNotifyingHost (1.0f); silence (p, 0.05, 256); fs->setValueNotifyingHost (0.0f); silence (p, 0.05, 256); }
            for (int i = 0; i < 10; ++i) MessageManager::getInstance()->runDispatchLoopUntil (20);
            ed.reset();
        }
        if (ap) ap->release();
        p.releaseResources(); p.prepareToPlay (SR, 512);
        still ("apres 40 bypass STOMP pendant la lecture");
    }

    p.releaseResources();
    inst.reset();
    std::printf ("%s\n", failures == 0 ? "TOUS LES TESTS OK" : "ECHEC(S)");
    return failures;
}
