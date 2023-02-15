
#ifndef portal_def
#define portal_def

#include <WiFiManager.h>


class Portal{
    public:
        char *hostname;
        WiFiManager wifiManager = WiFiManager();
        void autoConnect(const String label);
        void reset();
    private:
};







#endif