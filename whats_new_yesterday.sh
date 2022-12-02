#!/bin/bash
# download the previous day's what's new items, and format them

if [ $# -eq 0 ]; then
    FROM="yesterday"
else
    FROM=$1
fi

DATE=`date -d $FROM +'%F'`
URL="https://aws.amazon.com/api/dirs/items/search?item.directoryId=whats-new&sort_by=item.additionalFields.postDateTime&sort_order=desc&size=500&item.locale=en_US&page=0"
FILTER_CMD="{ \"items\": [ .items[] | select(.item.additionalFields.postDateTime | contains (\"$DATE\"))] }"
FORMAT_CMD=".items[] | .item + ([(.tags[] | { \"key\" : (.tagNamespaceId | sub(\"#\"; \"_\")), \"value\": .name})] | from_entries) | . + .additionalFields | del(.additionalFields)"
OUT="${DATE}_whats_new.json"
curl -s $URL | jq "$FILTER_CMD" | jq -c "$FORMAT_CMD" > $OUT