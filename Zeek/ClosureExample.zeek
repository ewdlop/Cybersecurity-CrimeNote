# File: closure-example.zeek

module ClosureExample;

export {
    type Counter: function(ip: addr): count;
}

# Function to create a closure that counts occurrences of IP addresses
function create_counter(): Counter {
    local counts: table[addr] of count = table();

    return function(ip: addr): count {
        if (ip !in counts) {
            counts[ip] = 0;
        }
        counts[ip] += 1;
        return counts[ip];
    };
}

# Global counter for IP addresses
global ip_counter: Counter;

event zeek_init() {
    # Initialize the counter
    ip_counter = create_counter();
    print "IP counter initialized.";
}

event new_connection(c: connection) {
    # Use the counter closure to count occurrences of source IP addresses
    local src_ip = c$id$orig_h;
    local count = ip_counter(src_ip);
    print fmt("IP %s has been seen %d times", src_ip, count);
}
