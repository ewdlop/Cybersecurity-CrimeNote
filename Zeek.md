In Zeek, events are a core part of the scripting language and framework. They are used to handle different types of network activity and trigger custom scripts or actions based on specific conditions. Zeek uses an event-driven model, where various network activities generate events that can be captured and processed by event handlers.

### Common Zeek Events

Here are some commonly used events in Zeek:

1. **Connection Events**
   - `new_connection(c: connection)`: Triggered when a new connection is detected.
   - `connection_established(c: connection)`: Triggered when a connection is successfully established.
   - `connection_state_remove(c: connection)`: Triggered when a connection is removed from the state table.

2. **HTTP Events**
   - `http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string)`: Triggered when an HTTP request is detected.
   - `http_reply(c: connection, version: string, status_code: count, reason_phrase: string, orig_mime_types: mime_types, resp_mime_types: mime_types)`: Triggered when an HTTP reply is detected.

3. **DNS Events**
   - `dns_request(c: connection, msg: dns_msg)`: Triggered when a DNS request is detected.
   - `dns_response(c: connection, msg: dns_msg)`: Triggered when a DNS response is detected.

4. **SSL/TLS Events**
   - `ssl_established(c: connection)`: Triggered when an SSL/TLS connection is successfully established.
   - `ssl_server_hello(c: connection, version: string, server_name: string)`: Triggered when an SSL/TLS server hello message is detected.

5. **File Analysis Events**
   - `file_new(f: fa_file)`: Triggered when a new file is detected.
   - `file_hash(f: fa_file, kind: string, hash: string)`: Triggered when a file hash is calculated.

### Writing Event Handlers

To handle events in Zeek, you write event handlers in Zeek scripts. Here's an example of how to write event handlers for some of the common events:

#### Example: HTTP Request Event Handler

```zeek
event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string) {
    print fmt("HTTP request detected: %s %s", method, unescaped_URI);
}
```

#### Example: DNS Request and Response Handlers

```zeek
event dns_request(c: connection, msg: dns_msg) {
    print fmt("DNS request detected from %s for %s", c$id$orig_h, msg$q$queries[0]$qname);
}

event dns_response(c: connection, msg: dns_msg) {
    print fmt("DNS response detected from %s for %s", c$id$resp_h, msg$q$queries[0]$qname);
}
```

#### Example: New Connection Event Handler

```zeek
event new_connection(c: connection) {
    print fmt("New connection detected from %s to %s", c$id$orig_h, c$id$resp_h);
}
```

### Using Event Handlers in a Zeek Script

To use these event handlers in a Zeek script, you need to create a script file (e.g., `events.zeek`) and include your event handler definitions. Here’s how you can do it:

1. **Create the Script File:**

    ```bash
    nano events.zeek
    ```

2. **Add Your Event Handlers:**

    ```zeek
    event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string) {
        print fmt("HTTP request detected: %s %s", method, unescaped_URI);
    }

    event dns_request(c: connection, msg: dns_msg) {
        print fmt("DNS request detected from %s for %s", c$id$orig_h, msg$q$queries[0]$qname);
    }

    event dns_response(c: connection, msg: dns_msg) {
        print fmt("DNS response detected from %s for %s", c$id$resp_h, msg$q$queries[0]$qname);
    }

    event new_connection(c: connection) {
        print fmt("New connection detected from %s to %s", c$id$orig_h, c$id$resp_h);
    }
    ```

3. **Run the Script with Zeek:**

    ```bash
    sudo zeek -i <interface> events.zeek
    ```

Replace `<interface>` with the network interface you want to monitor (e.g., `eth0`).

### Resources

- [Zeek Documentation](https://docs.zeek.org/en/stable/)
- [Zeek Scripting](https://docs.zeek.org/en/stable/scripting/index.html)
- [Zeek GitHub Repository](https://github.com/zeek/zeek)

By writing and customizing event handlers, you can tailor Zeek to monitor and respond to specific network activities, enhancing your network security monitoring capabilities.
