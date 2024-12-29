@load base/frameworks/notice
@load base/protocols/conn

module GravitationalNetworkEvents;

export {
    redef enum Notice::Type += {
        Gravitational_Influence
    };

    const data_threshold = 1000000;  # 1 MB threshold for data transfer
    const connection_threshold = 10;  # 10 connections threshold for frequency
}

# Function to log significant events
function log_gravitational_influence(c: connection, reason: string) {
    NOTICE([$note=Gravitational_Influence, 
            $msg=fmt("Gravitational influence detected: %s, %s -> %s", reason, c$id$orig_h, c$id$resp_h),
            $conn=c]);
}

event zeek_init() {
    print "Monitoring network for gravitational influences...";
}

event connection_established(c: connection) {
    if (c$resp$size > data_threshold) {
        log_gravitational_influence(c, "High data transfer");
    }
}

event connection_attempt(c: connection) {
    local freq_count = connection_attempts[c$id$orig_h] += 1;
    if (freq_count > connection_threshold) {
        log_gravitational_influence(c, "High frequency connections");
    }
}

global connection_attempts: table[addr] of count = table();

event connection_state_remove(c: connection) {
    if (c$id$orig_h in connection_attempts) {
        delete connection_attempts[c$id$orig_h];
    }
}
