# poisson-icmp-tracking.zeek

@load base/frameworks/notice
@load base/protocols/icmp
@load base/utils/enum

module PoissonICMPTracking;

export {
    redef enum Notice::Type += {
        Poisson_ICMP_Event
    };
}

const lambda = 2.0; # Average rate of events per interval (events per minute)
const sim_duration = 3600.0; # Total simulation duration in seconds (e.g., 1 hour)

event zeek_init() {
    local interval = 60.0; # Interval in seconds
    schedule interval { generate_poisson_event(interval, sim_duration) };
}

function generate_poisson_event(interval: interval, remaining_time: interval) {
    if (remaining_time <= 0.0) {
        print "Simulation ended";
        return;
    }

    local event_count = math::poisson(lambda);
    print fmt("Generated %d events in the past %f seconds", event_count, interval);

    for (local i in event_count) {
        NOTICE([$note=Poisson_ICMP_Event, $msg=fmt("Simulated ICMP event %d of %d", i+1, event_count)]);
    }

    schedule interval { generate_poisson_event(interval, remaining_time - interval) };
}

event icmp_echo_request(c: connection, icmp: icmp_conn, id: count, seq: count, payload: string) {
    print fmt("ICMP Echo Request from %s to %s", c$id$orig_h, c$id$resp_h);
}

event icmp_echo_reply(c: connection, icmp: icmp_conn, id: count, seq: count, payload: string) {
    print fmt("ICMP Echo Reply from %s to %s", c$id$orig_h, c$id$resp_h);
}

event icmp_unreachable(c: connection, icmp: icmp_conn, id: count, seq: count, payload: string) {
    print fmt("ICMP Unreachable from %s to %s", c$id$orig_h, c$id$resp_h);
}
