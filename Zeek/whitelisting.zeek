# whitelisting.zeek

# Define the set of whitelisted IP addresses
redef Notice::policy += {
    [$note=Notice::ACTION, $priority=0] = {
        |n: Notice::Info|
        n$src in whitelist_ip_addrs
    }
};

redef Log::default_filters += {
    # Filter for excluding whitelisted IPs from certain logs
    ["whitelist"] = [
        $name = "whitelist",
        $pred = function (rec: Log::Info): bool {
            return rec$id$orig_h in whitelist_ip_addrs || rec$id$resp_h in whitelist_ip_addrs;
        }
    ]
};

# Define the set of whitelisted IP addresses
global whitelist_ip_addrs: set[addr] = {
    192.168.1.1,  # Example IP address
    10.0.0.1      # Another example IP address
};
