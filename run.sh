#!/bin/sh

download_requests() {
  host=$1
  name=$2
  ssh $host -t "psql -c \"\copy requests to '${name}.csv' csv  header\" nfs"
  ssh $host -t "cat ${name}.csv | gzip > ${name}.csv.gz"
  scp $host:$name.csv.gz ./recordings/$name.csv.gz
  gzip -cdk ./recordings/$name.csv.gz > ./recordings/$name.csv
  rm ./recordings/$name.csv.gz
}


"$@"