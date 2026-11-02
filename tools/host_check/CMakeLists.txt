# Charge le VST3 compile comme un hote (REAPER simule) : memoire 1 au lancement, queue du delay apres
# toutes les operations qu'un hote peut faire (desactivation, bypass, etat, programme, tailles de bloc, NaN...)
cmake_minimum_required(VERSION 3.22)
project(EightEchoHostCheck VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
juce_add_console_app(EightEchoHostCheck PRODUCT_NAME "EightEchoHostCheck")
target_sources(EightEchoHostCheck PRIVATE main.cpp)
target_compile_definitions(EightEchoHostCheck PRIVATE JUCE_PLUGINHOST_VST3=1 JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_STANDALONE_APPLICATION=1
  JUCE_ALSA=0 JUCE_JACK=0 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(EightEchoHostCheck PRIVATE juce::juce_audio_utils juce::juce_recommended_config_flags)
