# dns-log.zeek
@load base/protocols/dns

event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
{
    print fmt("DNS query for %s from %s", query, c$id$orig_h);
}
