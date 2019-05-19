#include "JsonParse.h"
#include <string.h>
#include <stdio.h>

using namespace std;

JsonParse::JsonParse(){

}

JsonParse::~JsonParse(){

}

char* JsonParse::GetJson(){
    char* temp = new char[30];
    memset(temp, 0, sizeof(temp));
    char *speedStr = new char[4];
    char *angleStr = new char[4];
    
    sprintf(speedStr, "%d", this->speed);
    sprintf(angleStr, "%d", this->angle);

    strcat(temp, "{\"speed\":");
    strcat(temp, speedStr);
    strcat(temp, ",\"angle\":");
    strcat(temp, angleStr);
    strcat(temp, "}");
    printf("%s", temp); 

    return temp;
}