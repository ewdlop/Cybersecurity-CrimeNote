To integrate **Zeek** logs with **Grafana** and visualize TCP congestion analysis, follow these steps:

---

### **1. Set Up Data Collection**
Zeek logs TCP congestion data into a log file (e.g., `tcp_congestion.log`). This file needs to be forwarded to a time-series database that Grafana can query.

#### **Choose a Database**
Grafana supports various backends. Common choices for Zeek logs are:
- **Elasticsearch** (for structured log storage and querying).
- **InfluxDB** (optimized for time-series data).
- **Prometheus** (if metrics-based).

---

### **2. Parse Zeek Logs**
Zeek logs are written in tab-separated value (TSV) format. Convert or ingest them into the database using:
- **Logstash** for Elasticsearch.
- **Telegraf** for InfluxDB.

#### **Example Parsing Zeek Logs with Logstash**
Create a Logstash configuration (`zeek_logstash.conf`) to parse `tcp_congestion.log`:

```conf
input {
  file {
    path => "/path/to/zeek/logs/tcp_congestion.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json_lines
  }
}

filter {
  grok {
    match => {
      "message" => "%{TIMESTAMP_ISO8601:timestamp}\t%{IP:orig_h}\t%{IP:resp_h}\t%{INT:orig_retrans}\t%{INT:resp_retrans}\t%{WORD:reset_flag}\t%{WORD:fin_flag}\t%{WORD:high_retrans}"
    }
  }
  mutate {
    convert => {
      "orig_retrans" => "integer"
      "resp_retrans" => "integer"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "zeek-tcp-congestion"
  }
  stdout { codec => rubydebug }
}
```

---

### **3. Send Logs to the Database**
- **Elasticsearch**: Run Logstash with the configuration above.
- **InfluxDB**: Use Telegraf’s `logparser` plugin.
- **Prometheus**: Transform logs into metrics using `Promtail` and `Loki`.

---

### **4. Configure Grafana**
#### **Connect Grafana to the Database**
1. Open Grafana → **Configuration** → **Data Sources** → **Add data source**.
2. Select the appropriate data source:
   - Elasticsearch: Enter the Elasticsearch host and index pattern (`zeek-tcp-congestion-*`).
   - InfluxDB: Provide the database and measurement name.
   - Prometheus: Use the Prometheus URL.

#### **Query Logs**
- **Elasticsearch Query**:
  ```json
  {
    "query": {
      "match_all": {}
    }
  }
  ```
- **InfluxDB Query**:
  ```sql
  SELECT * FROM "tcp_congestion"
  ```
- **Prometheus Query**:
  ```
  rate(zeek_tcp_retransmissions[5m])
  ```

---

### **5. Create Dashboards in Grafana**
#### **Example Panels**
1. **Time-Series Panel: Retransmissions**
   - Query: Plot `orig_retrans` and `resp_retrans` over time.
   - Visualization: Line Chart.
   - Metrics: Count retransmissions and detect spikes.

2. **Gauge Panel: High Retransmission Alerts**
   - Query: Filter `high_retrans == true`.
   - Visualization: Gauge.
   - Use thresholds for retransmissions (e.g., critical > 10).

3. **Heatmap: Congestion by Host**
   - Query: Group retransmissions by `orig_h` and `resp_h`.
   - Visualization: Heatmap.
   - Color-code congestion levels (low, medium, high).

4. **Table: Detailed Logs**
   - Query: Show raw logs (`timestamp`, `orig_h`, `resp_h`, `orig_retrans`, etc.).
   - Visualization: Table.

---

### **6. Set Alerts**
1. In Grafana, go to the **Alerting** tab in your dashboard.
2. Add conditions for critical events:
   - **High retransmissions**:
     - Query: `orig_retrans > 10 OR resp_retrans > 10`.
     - Notification: Email, Slack, or webhook.
   - **Frequent Resets**:
     - Query: Count of `reset_flag == true` in the last 5 minutes.

3. Configure notifications for your preferred channel.

---

### **7. Example Dashboard Visualization**
- **Panel 1**: Retransmission trends over time.
- **Panel 2**: Heatmap of congested hosts.
- **Panel 3**: Gauge for active high retransmission events.
- **Panel 4**: Table showing the latest events.

---

### **Next Steps**
- **Test Data Flow**: Use a sample `tcp_congestion.log` file to verify parsing and visualization.
- **Extend Analysis**: Add RTT metrics or sequence number deltas for deeper TCP congestion insights.

If you need further details on Grafana queries or setting up alerts, let me know!
