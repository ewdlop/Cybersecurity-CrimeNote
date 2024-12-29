To treat event tracking in Zeek as stateless lambda functions, we can encapsulate the logic in functions that are called in response to specific events. This approach keeps the event handling stateless and modular.

Below is an example of how to create stateless lambda functions to track traceroute events and connections from Iran and China.

### Stateless Lambda Functions in Zeek

1. **Monitor ICMP Events for Traceroute Detection**: Use a function to handle ICMP time exceeded messages.
2. **Monitor Connections**: Use a function to handle new connections and filter them based on geolocation.

### Example Script

```zeek
@load base/frameworks/notice
@load base/protocols/conn
@load base/protocols/icmp
@load base/utils/enum
@load policy/protocols/conn/geoip

module StatelessTracking;

export {
    redef enum Notice::Type += {
        Traceroute_Event,
        Iran_Connection,
        China_Connection
    };
}

const countries_of_interest: set[string] = {"Iran", "China"};

event zeek_init() {
    print "Tracking traceroute and connections to/from Iran and China.";
}

# Stateless function to handle ICMP time exceeded events (traceroute detection)
function handle_icmp_time_exceeded(c: connection, icmp: icmp_conn, ttl: count) {
    local src_country = GeoLocation::lookup_location(c$id$orig_h)$country_code;
    local dst_country = GeoLocation::lookup_location(c$id$resp_h)$country_code;

    if (src_country in countries_of_interest || dst_country in countries_of_interest) {
        NOTICE([$note=Traceroute_Event, $msg=fmt("Traceroute detected: %s to %s (TTL %d)", c$id$orig_h, c$id$resp_h, ttl)]);
    }
}

# Stateless function to handle new connections
function handle_new_connection(c: connection) {
    local src_country = GeoLocation::lookup_location(c$id$orig_h)$country_code;
    local dst_country = GeoLocation::lookup_location(c$id$resp_h)$country_code;

    if (src_country in countries_of_interest) {
        NOTICE([$note=Iran_Connection, $msg=fmt("Connection from Iran: %s to %s", c$id$orig_h, c$id$resp_h)]) if src_country == "IR";
        NOTICE([$note=China_Connection, $msg=fmt("Connection from China: %s to %s", c$id$orig_h, c$id$resp_h)]) if src_country == "CN";
    } else if (dst_country in countries_of_interest) {
        NOTICE([$note=Iran_Connection, $msg=fmt("Connection to Iran: %s to %s", c$id$orig_h, c$id$resp_h)]) if dst_country == "IR";
        NOTICE([$note=China_Connection, $msg=fmt("Connection to China: %s to %s", c$id$orig_h, c$id$resp_h)]) if dst_country == "CN";
    }
}

# Event handler for ICMP time exceeded
event icmp_time_exceeded(c: connection, icmp: icmp_conn, ttl: count) {
    handle_icmp_time_exceeded(c, icmp, ttl);
}

# Event handler for new connections
event new_connection(c: connection) {
    handle_new_connection(c);
}
```

### Explanation

- **GeoIP Setup**: Ensure that the GeoIP database files are correctly referenced in your Zeek configuration. This script assumes GeoIP data is available and correctly set up.
- **Stateless Functions**: `handle_icmp_time_exceeded` and `handle_new_connection` are stateless functions that process ICMP time exceeded events and new connections, respectively.
- **Event Handlers**: The `icmp_time_exceeded` and `new_connection` events call the corresponding stateless functions.

### Running the Script

Save the script as `stateless-tracking.zeek` and run it with Zeek:

```sh
zeek -r <pcap_file> stateless-tracking.zeek
```

Replace `<pcap_file>` with the path to your pcap file containing network traffic.

### Summary

- **Stateless Functions**: Handle events without maintaining state within the functions.
- **Event Tracking**: Track traceroute events and connections from/to Iran and China.
- **Integration**: Combine ICMP and connection event tracking with GeoIP lookups for filtering.

This approach ensures that the event handling logic is modular, stateless, and easy to maintain. Adjust the script as needed to fit your specific requirements.
