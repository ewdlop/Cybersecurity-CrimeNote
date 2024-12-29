# http-log.zeek
@load base/protocols/http

event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string)
{
    print fmt("HTTP request from %s to %s", c$id$orig_h, unescaped_URI);
}
