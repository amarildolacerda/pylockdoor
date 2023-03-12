// ignore_for_file: avoid_print

import "package:upnp2/upnp.dart";

class Discovery {
  Future<List<Device> process() async {
    List<Device> clients = [];
    final disc = DeviceDiscoverer();
    await disc.start(ipv6: false);
    disc.quickDiscoverClients().listen((client) async {
      try {
        final Device? dev = await client.getDevice();
        if (dev != null) clients.add(dev);
      } catch (e, stack) {
        print('ERROR: $e - ${client.location}');
        print(stack);
      }
    });
  }
}
