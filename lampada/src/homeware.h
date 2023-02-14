#ifndef homeware_def
#define homeware_def

#include <ArduinoJson.h>


class Homeware
{
public:
    static constexpr int SIZE_BUFFER = 1024;
    DynamicJsonDocument config = DynamicJsonDocument(SIZE_BUFFER);
};

#endif