# File: set-separator.zeek

@load base/frameworks/logging

redef Log::default_writer = Log::WRITER_ASCII;
redef LogAscii::separator = ",";  # Change separator to comma
