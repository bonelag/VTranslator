

class VSoft : public ENGINE
{
public:
    VSoft()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Pac\\*.pac";
    };
    bool attach_function();
};