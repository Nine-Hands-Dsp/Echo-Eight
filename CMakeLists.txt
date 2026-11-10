cmake_minimum_required(VERSION 3.22)
project(EightEcho VERSION 2.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.13" CACHE STRING "Minimum macOS version")

# JUCE : soit un dossier local passe avec -DJUCE_DIR=..., soit telechargement automatique
if(DEFINED JUCE_DIR)
    add_subdirectory(${JUCE_DIR} JUCE)
else()
    include(FetchContent)
    FetchContent_Declare(JUCE
        GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
        GIT_TAG 8.0.15
        GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(JUCE)
endif()

set(FORMATS VST3)
if(APPLE)
    list(APPEND FORMATS AU)
endif()

juce_add_plugin(EightEcho
    COMPANY_NAME "NINE HANDS | DSP"
    PRODUCT_NAME "Eight Echo"
    PLUGIN_MANUFACTURER_CODE Wiga
    PLUGIN_CODE Wg8e
    FORMATS ${FORMATS}
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD FALSE
    VST3_CATEGORIES "Fx" "Delay"
    AU_MAIN_TYPE kAudioUnitType_MusicEffect)

juce_add_binary_data(EightEchoData SOURCES
    background.png footswitch.png pipe_on.png sync_on.png
    led_ice.png led_red.png led_green.png led_orange.png
    glow_tempo.png glow_check_red.png glow_check_green.png glow_check_orange.png glow_sync.png glow_x2.png
    glow_slot1.png glow_slot2.png glow_slot3.png glow_slot4.png glow_slot5.png glow_slot6.png glow_slot7.png
    NineHandsLogo.svg assets/eight_echo_title.svg assets/eight_echo_motif.svg
    assets/fonts/LiberationSans-Bold.ttf assets/fonts/LiberationMono-Bold.ttf
    assets/fonts/Poppins-Regular.ttf assets/fonts/Poppins-Medium.ttf assets/fonts/Poppins-Bold.ttf)

target_sources(EightEcho PRIVATE
    PluginProcessor.cpp
    PluginEditor.cpp)

target_compile_definitions(EightEcho PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    JUCE_DISPLAY_SPLASH_SCREEN=0)

target_link_libraries(EightEcho
    PRIVATE
        EightEchoData
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)
