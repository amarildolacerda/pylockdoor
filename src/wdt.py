wdt = None
if not wdt:
        from machine import WDT
        wdt = WDT()
wdt.feed()
