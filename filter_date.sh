#!/bin/bash
# Take input in AWS whats new feed format and remove entries from a given date
DATE=$1
FILTER_CMD="{ \"items\": [ .items[] | select(.item.additionalFields.postDateTime | contains (\"$DATE\") | not)] }"
jq -c "$FILTER_CMD"