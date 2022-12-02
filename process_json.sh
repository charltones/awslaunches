#!/bin/bash
# Process AWS what's new JSON into a non-nested format

jq -c '.items[] | .item + ([(.tags[] | { "key" : (.tagNamespaceId | sub("#"; "_")), "value": .name})] | from_entries) | . + .additionalFields | del(.additionalFields)' < $1