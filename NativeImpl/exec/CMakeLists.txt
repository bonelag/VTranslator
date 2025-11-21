
project(V)

option(PYSTAND_CONSOLE "Build PyStand as a console application." OFF)


include(FetchContent)

file(DOWNLOAD
    https://image.vtranslator.org/v.ico
    ${CMAKE_BINARY_DIR}/v.ico
)

file(WRITE ${CMAKE_BINARY_DIR}/v.rc "IDI_ICON1 ICON DISCARDABLE \"v.ico\"")

set(sources PyStand.cpp ${CMAKE_BINARY_DIR}/v.rc ${versioninfo})

#add_executable(VTranslator_debug ${sources})
#target_compile_definitions(VTranslator_debug PRIVATE PYSTAND_CONSOLE)
add_executable(VTranslator WIN32 ${sources})
if(NOT WINXP)
add_executable(VTranslator_admin WIN32 ${sources})
endif()
set_target_properties(VTranslator PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
if(NOT WINXP)
set_target_properties(VTranslator_admin PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
endif()
if(MSVC)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 4)
    set_target_properties(VTranslator PROPERTIES LINK_FLAGS "/LARGEADDRESSAWARE")
    #set_target_properties(VTranslator_debug PROPERTIES LINK_FLAGS "/LARGEADDRESSAWARE")
    if(NOT WINXP)
        set_target_properties(VTranslator_admin PROPERTIES LINK_FLAGS "/LARGEADDRESSAWARE /MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\"")
    endif()
else()
    set_target_properties(VTranslator_admin PROPERTIES LINK_FLAGS "/MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\"")
endif()
endif()