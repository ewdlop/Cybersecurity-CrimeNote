@load base/frameworks/notice
@load base/protocols/conn

module DDoSDetection;

export {
    redef enum Notice::Type += {
        DDoS_Attack
    };

    const connection_threshold = 100;  # Threshold for number of connections
    const time_window = 60secs;        # Time window for counting connections
}

global ip_connections: table[addr] of count &default=0;
global ip_connection_timers: table[addr] of time &default=0secs;

event connection_established(c: connection) {
    local dest_ip = c$id$resp_h;

    # Increment the connection count for the destination IP
    ip_connections[dest_ip] += 1;

    # Initialize or update the connection timer
    if (ip_connection_timers[dest_ip] == 0secs) {
        ip_connection_timers[dest_ip] = network_time();
    }

    # Check if the time window has elapsed
    if (network_time() - ip_connection_timers[dest_ip] >= time_window) {
        if (ip_connections[dest_ip] > connection_threshold) {
            NOTICE([$note=DDoS_Attack, $msg=fmt("Potential DDoS attack detected on %s with %d connections", dest_ip, ip_connections[dest_ip]), $conn=c]);
        }
        # Reset the counter and timer for the next window
        ip_connections[dest_ip] = 0;
        ip_connection_timers[dest_ip] = network_time();
    }
}
