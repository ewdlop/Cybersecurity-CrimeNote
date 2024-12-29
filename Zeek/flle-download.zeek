# File: http-file-extraction.zeek

@load base/protocols/http
@load base/files/extract

module HTTPFileExtraction;

export {
    redef FileExtract::prefix = "extracted_files/";  # Directory to save extracted files
}

event file_new(f: fa_file) {
    if (f$source == "HTTP") {
        print fmt("New file detected from HTTP: %s", f$id);
    }
}

event file_sniff(f: fa_file, meta: fa_metadata) {
    if (f$source == "HTTP") {
        print fmt("File metadata: %s", meta);
    }
}

event file_state_remove(f: fa_file) {
    if (f$source == "HTTP") {
        local extract_path = fmt("%s%s", FileExtract::prefix, f$id);
        print fmt("File completed: %s, saved to %s", f$id, extract_path);
    }
}

event file_over_new_connection(c: connection, f: fa_file) {
    if (f$source == "HTTP") {
        print fmt("File %s is being transferred over connection %s -> %s", f$id, c$id$orig_h, c$id$resp_h);
    }
}
