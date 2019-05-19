#ifndef _JSONPARSE_H
#define _JSONPARSE_H

class JsonParse{
    public:
    int speed;
    int angle;
    char request[10];
    JsonParse();
    ~JsonParse();
    char* GetJson();
};

#endif
