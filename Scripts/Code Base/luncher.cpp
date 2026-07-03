#include <windows.h>
#include <string>

BOOL WINAPI CtrlHandler(DWORD ctrlType)
{
    if (ctrlType == CTRL_C_EVENT)
    {
        // Ignore Ctrl+C in launcher
        return TRUE;
    }
    return FALSE;
}

int main(int argc, char* argv[])
{
    SetConsoleCtrlHandler(CtrlHandler, TRUE);
    char exePath[MAX_PATH];
    GetModuleFileNameA(NULL, exePath, MAX_PATH);

    std::string fullPath = exePath;

    size_t slash = fullPath.find_last_of("\\/");
    std::string dir = fullPath.substr(0, slash + 1);

    std::string exeName = fullPath.substr(slash + 1);
    size_t dot = exeName.find_last_of('.');
    std::string name = exeName.substr(0, dot);

    std::string script = dir + "Scripts\\" + name + ".py";

    std::string cmd = "python \"" + script + "\"";

    for (int i = 1; i < argc; i++){
    std::string arg = argv[i];

    // escape trailing backslashes
    size_t backslashes = 0;
    for (size_t j = arg.size(); j > 0 && arg[j-1] == '\\'; j--)
        backslashes++;

    if (backslashes > 0)
        arg.append(backslashes, '\\');

    cmd += " \"";
    cmd += arg;
    cmd += "\"";
    }

    STARTUPINFOA si{};
    PROCESS_INFORMATION pi{};
    si.cb = sizeof(si);

    if (!CreateProcessA(
        NULL,
        cmd.data(),
        NULL,
        NULL,
        TRUE,
        0,
        NULL,
        NULL,
        &si,
        &pi))
    {
        return 1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    DWORD exitCode = 0;
    GetExitCodeProcess(pi.hProcess, &exitCode);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return exitCode;
}