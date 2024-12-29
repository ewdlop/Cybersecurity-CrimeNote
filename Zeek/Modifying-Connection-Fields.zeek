# File: modify-connection.zeek

@load base/protocols/conn

event connection_established(c: connection) {
    print fmt("Original connection: %s -> %s", c$id$orig_h, c$id$resp_h);
    
    # Modifying the destination IP address
    c$id$resp_h = 192.168.0.1;

    print fmt("Modified connection: %s -> %s", c$id$orig_h, c$id$resp_h);
}

event connection_state_remove(c: connection) {
    print fmt("Final connection state: %s -> %s", c$id$orig_h, c$id$resp_h);
}
