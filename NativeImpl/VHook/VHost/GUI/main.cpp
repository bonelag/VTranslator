#include "VHost.h"
int main()
{
    SetProcessDPIAware();
    VHost _vhost;
    _vhost.show();
    mainwindow::run();
}
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    main();
}