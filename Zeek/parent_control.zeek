# Load required Zeek scripts
@load base/frameworks/notice
@load base/protocols/http
@load base/protocols/dns
@load base/protocols/smtp
@load base/files/hash
@load policy/frameworks/intel/seen

module SocialEngineering;

export {
    redef enum Notice::Type += {
        Suspicious_URL,
        Suspicious_Domain,
        Suspicious_Email,
        Suspicious_File_Download,
        Suspicious_User_Agent,
        Multiple_Failed_Logins
    };

    # Configuration
    const suspicious_tlds: set[string] = {
        ".xyz", ".top", ".pw", ".cc", ".tk", ".ml", ".ga", ".cf"
    } &redef;

    const suspicious_keywords: pattern = /password|login|account|bank|verify|security|update|confirm/ &redef;
    
    const max_failed_logins = 5 &redef;
    
    # Track failed login attempts
    global failed_logins: table[addr] of count &create_expire=1hrs;
}

# Function to check domain entropy (detect potential DGA)
function calculate_domain_entropy(domain: string): double
{
    local char_freq: table[string] of count;
    local length = |domain|;
    local entropy = 0.0;

    for (c in domain) {
        if (c !in char_freq)
            char_freq[c] = 0;
        char_freq[c] += 1;
    }

    for (c in char_freq) {
        local freq = char_freq[c] / length;
        entropy += freq * log10(freq) / log10(2.0);
    }

    return -entropy;
}

# HTTP Analysis
event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string)
{
    local client = c$id$orig_h;
    local host = c$http$host;

    # Check for suspicious URLs
    if (suspicious_keywords in original_URI) {
        NOTICE([
            $note=Suspicious_URL,
            $conn=c,
            $msg=fmt("Suspicious URL accessed: %s", original_URI),
            $identifier=cat(client, original_URI)
        ]);
    }

    # Check User-Agent
    if (c$http?$user_agent) {
        local ua = to_lower(c$http$user_agent);
        if (/curl|wget|python|powershell/ in ua) {
            NOTICE([
                $note=Suspicious_User_Agent,
                $conn=c,
                $msg=fmt("Suspicious User-Agent detected: %s", ua),
                $identifier=cat(client, ua)
            ]);
        }
    }
}

# DNS Analysis
event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
{
    local entropy = calculate_domain_entropy(query);
    
    # Check for high entropy domains (possible DGA)
    if (entropy > 4.0) {
        NOTICE([
            $note=Suspicious_Domain,
            $conn=c,
            $msg=fmt("High entropy domain detected: %s (entropy: %.2f)", query, entropy),
            $identifier=cat(c$id$orig_h, query)
        ]);
    }

    # Check for suspicious TLDs
    for (tld in suspicious_tlds) {
        if (tld in query) {
            NOTICE([
                $note=Suspicious_Domain,
                $conn=c,
                $msg=fmt("Suspicious TLD detected: %s", query),
                $identifier=cat(c$id$orig_h, query)
            ]);
        }
    }
}

# SMTP Analysis
event mime_entity_data(c: connection, length: count, data: string)
{
    if (! c$smtp?$mailfrom || ! c$smtp?$rcptto)
        return;

    # Check email content for suspicious patterns
    if (suspicious_keywords in data) {
        NOTICE([
            $note=Suspicious_Email,
            $conn=c,
            $msg="Suspicious content detected in email",
            $identifier=cat(c$id$orig_h, c$smtp$mailfrom)
        ]);
    }
}

# File Analysis
event file_new(f: fa_file)
{
    Files::add_analyzer(f, Files::ANALYZER_MD5);
    Files::add_analyzer(f, Files::ANALYZER_SHA1);
}

event file_hash(f: fa_file, kind: string, hash: string)
{
    if (kind == "md5" || kind == "sha1") {
        # Here you could check against known malicious file hashes
        # For example, integrate with VirusTotal API
        if (|hash| > 0) {
            NOTICE([
                $note=Suspicious_File_Download,
                $msg=fmt("File download with hash: %s", hash),
                $identifier=hash
            ]);
        }
    }
}

# Track failed login attempts (example for HTTP POST)
event http_reply(c: connection, version: string, code: count, reason: string)
{
    if (code == 401 || code == 403) {
        local client = c$id$orig_h;
        if (client !in failed_logins)
            failed_logins[client] = 0;
        failed_logins[client] += 1;

        if (failed_logins[client] >= max_failed_logins) {
            NOTICE([
                $note=Multiple_Failed_Logins,
                $conn=c,
                $msg=fmt("Multiple failed login attempts from %s", client),
                $identifier=cat(client)
            ]);
        }
    }
}

# Log all notices
hook Notice::policy(n: Notice::Info)
{
    add n$actions[Notice::ACTION_LOG];
    if (n$note == Suspicious_URL || n$note == Suspicious_Domain)
        add n$actions[Notice::ACTION_EMAIL];
}
