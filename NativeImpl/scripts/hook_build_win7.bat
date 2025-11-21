set https_proxy=http://127.0.0.1:7897
cmake --build ..\VHook\build\x86_win7_1 --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
cmake --build ..\VHook\build\x64_win7_1 --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
cmake --build ..\VHook\build\x86_win7_2 --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
cmake --build ..\VHook\build\x64_win7_2 --config Release --target ALL_BUILD -j %NUMBER_OF_PROCESSORS%
robocopy ..\VHook\builds\Release_win7 ..\..\..\files\VHook