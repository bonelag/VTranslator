#pragma once

// texthook/defs.h
// 8/23/2013 jichi

// Pipes

constexpr auto HOOK_PIPE = L"\\\\.\\pipe\\V_HOOK";
constexpr auto HOST_PIPE = L"\\\\.\\pipe\\V_HOST";

// Sections

constexpr auto EMBED_SHARED_MEM = L"EMBED_SHARED_MEM"; // _%d
constexpr auto HOOK_SEARCH_SHARED_MEM = L"HOOK_SEARCH_SHARED_MEM";

// Mutexes

constexpr auto ITH_HOOKMAN_MUTEX_ = L"V_VNR_HOOKMAN_"; // ITH_HOOKMAN_%d
constexpr auto CONNECTING_MUTEX = L"V_CONNECTING_PIPES";

// Events
constexpr auto V_EMBED_notify_event = "V_NOTIFY.%d.%llu";

constexpr auto PIPE_AVAILABLE_EVENT = L"V_PIPE_AVAILABLE";

// Files
constexpr auto V_HOOK_DLL_64 = L"VHook64";
constexpr auto V_HOOK_DLL_32 = L"VHook32";

#ifdef _WIN64
constexpr auto V_HOOK_DLL = V_HOOK_DLL_64; // .dll but LoadLibrary automatically adds that
#else
constexpr auto V_HOOK_DLL = V_HOOK_DLL_32; // .dll but LoadLibrary automatically adds that
#endif

extern WORD V_VERSION[4];

struct DECLSPEC_UUID("692d51d9-65bd-4981-90d1-44cc319a5b8d") _COMPATIBLE_HELPER; // 如果发生不兼容的修改，再修改这个，而不是只要版本号不同就不行，使条件更加宽松。
inline const GUID &compatible_sig = __uuidof(_COMPATIBLE_HELPER);
// EOF
