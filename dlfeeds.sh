#!/bin/bash
# Get up to date with feeds by downloading historical data

for YEAR in 2022 2021 2020 2019 2018 2017 2016 2015 2014 2013 2012 2011 2010 2009 2008 2007 2006 2005 2004
do
    
    URL="https://aws.amazon.com/api/dirs/items/search?item.directoryId=whats-new&sort_by=item.additionalFields.postDateTime&sort_order=desc&size=2000&item.locale=en_US&page=0&tags.id=whats-new%23year%23$YEAR"
    echo $URL
    curl "$URL" -o raw/$YEAR-whats-new.json
done
for YEAR in 2021 2020
do
    
    URL="https://aws.amazon.com/api/dirs/items/search?item.directoryId=whats-new&sort_by=item.additionalFields.postDateTime&sort_order=desc&size=2000&item.locale=en_US&page=1&tags.id=whats-new%23year%23$YEAR"
    echo $URL
    curl "$URL" -o raw/$YEAR-whats-new-p2.json
done

#for FILE in 20*.json; do ./process_json.sh $FILE > processed/$FILE; done