# Outil hors plugin : compile le processeur + la fenetre d'Eight Echo sous Linux et exporte des captures PNG (apercu, notice)
cmake_minimum_required(VERSION 3.22)
project(EightEchoRender VERSION 2.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(EightEchoRenderData SOURCES
  ${W}/background.png ${W}/footswitch.png ${W}/pipe_on.png ${W}/sync_on.png
  ${W}/led_ice.png ${W}/led_red.png ${W}/led_green.png ${W}/led_orange.png
  ${W}/glow_tempo.png ${W}/glow_check_red.png ${W}/glow_check_green.png ${W}/glow_check_orange.png ${W}/glow_sync.png ${W}/glow_x2.png
  ${W}/glow_slot1.png ${W}/glow_slot2.png ${W}/glow_slot3.png ${W}/glow_slot4.png ${W}/glow_slot5.png ${W}/glow_slot6.png ${W}/glow_slot7.png
  ${W}/NineHandsLogo.svg ${W}/assets/eight_echo_title.svg ${W}/assets/eight_echo_motif.svg
  ${W}/assets/fonts/LiberationSans-Bold.ttf ${W}/assets/fonts/LiberationMono-Bold.ttf
  ${W}/assets/fonts/Poppins-Regular.ttf ${W}/assets/fonts/Poppins-Medium.ttf ${W}/assets/fonts/Poppins-Bold.ttf)
juce_add_console_app(EightEchoRender PRODUCT_NAME "EightEchoRender")
target_sources(EightEchoRender PRIVATE main.cpp ${W}/PluginProcessor.cpp ${W}/PluginEditor.cpp)
target_include_directories(EightEchoRender PRIVATE ${W})
target_compile_definitions(EightEchoRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JUCE_USE_XRENDER=0
  JucePlugin_Name="Eight Echo" JucePlugin_Build_VST3=0 JucePlugin_VersionString="2.0.0"
  JucePlugin_IsSynth=0 JucePlugin_WantsMidiInput=1 JucePlugin_ProducesMidiOutput=0 JucePlugin_IsMidiEffect=0
  JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(EightEchoRender PRIVATE EightEchoRenderData juce::juce_audio_utils juce::juce_dsp juce::juce_recommended_config_flags)
