
if(BUILD_GUI)
add_executable(VHost WIN32 confighelper.cpp controls.cpp main.cpp processlistwindow.cpp  VHost.cpp window.cpp ../../../exec/v.rc pluginmanager.cpp Plugin/extensionimpl.cpp Plugin/copyclipboard.cpp QtLoader_inline.cpp app.manifest ${versioninfo})
target_precompile_headers(VHost REUSE_FROM pch) 
set_target_properties(VHost PROPERTIES OUTPUT_NAME "VHost${bitappendix}")

FetchContent_Declare(json 
    URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz
    DOWNLOAD_EXTRACT_TIMESTAMP true
)
FetchContent_MakeAvailable(json)

target_link_libraries(VHost comctl32 winhttp pch host nlohmann_json::nlohmann_json ${YY_Thunks} lang_ui)
endif()
