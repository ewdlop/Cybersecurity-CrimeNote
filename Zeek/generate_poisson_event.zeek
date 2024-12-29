# poisson-events.zeek

@load base/frameworks/notice
@load base/protocols/http
@load base/utils/enum

module PoissonEvents;

export {
    redef enum Notice::Type += {
        Poisson_Event
    };
}

const lambda = 2.0; # Average rate of events per interval (e.g., per minute)
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
        NOTICE([$note=Poisson_Event, $msg=fmt("Simulated event %d of %d", i+1, event_count)]);
    }

    schedule interval { generate_poisson_event(interval, remaining_time - interval) };
}
