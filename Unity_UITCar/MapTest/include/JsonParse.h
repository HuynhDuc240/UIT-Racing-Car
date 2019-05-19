#ifndef _JSONPARSE_H
#define _JSONPARSE_H

class JsonParse{
    public:
    int speed;
    int angle;
    JsonParse();
    ~JsonParse();
    char* GetJson();
};

#endif