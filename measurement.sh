#!/bin/bash
TARGET=8.8.8.8
PROBES=60812,17889,1011163,1001130,1007645,61435,1009606,26201,22802,60929,64532,1008318,51593,60323,1000295,32686,1010025,51475,54866,1007637
PROBE_COUNT=$(echo $PROBES | tr ',' '\n' | wc -l)
START_TIME=$(date -d '2025-06-30 21:59:00' +%s%3N) # Start time in milliseconds
STOP_TIME=$(date -d '2025-07-07 21:59:00' +%s%3N)  # Stop time in milliseconds
BILL_TO=example@mail.com
API_KEY=your_api_key_here

curl -H "Authorization: Key $API_KEY" \
     -H "Content-Type: application/json" \
     -X POST \
     -d "$(cat <<EOF
{
  "definitions": [
    {
      "type": "traceroute",
      "af": 4,
      "resolve_on_probe": true,
      "description": "Traceroute measurement to $TARGET",
      "response_timeout": 4000,
      "protocol": "UDP",
      "packets": 3,
      "size": 48,
      "first_hop": 1,
      "max_hops": 32,
      "paris": 16,
      "destination_option_size": 0,
      "hop_by_hop_option_size": 0,
      "dont_fragment": false,
      "skip_dns_check": false,
      "target": "$TARGET",
      "interval": 900
    }
  ],
  "probes": [
    {
      "type": "probes",
      "value": "$PROBES",
      "requested": $PROBE_COUNT
    }
  ],
  "is_oneoff": false,
  "bill_to": "$BILL_TO",
  "start_time": $START_TIME,
  "stop_time": $STOP_TIME
}
EOF
)" https://atlas.ripe.net/api/v2/measurements/