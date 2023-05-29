#!/bin/sh

download_requests() {
  host=$1
  name=$2
  ssh $host -t "psql -c \"\copy requests to '${name}.csv' csv  header\" nfs"
  ssh $host -t "cat ${name}.csv | gzip > ${name}.csv.gz"
  scp $host:$name.csv.gz ./recordings/$name.csv.gz
  gzip -cdk ./recordings/$name.csv.gz > ./recordings/$name.csv
  python process_recording.py transform $name
}


worker() {
  python3 worker.py
}


sim() {
  cd simulation && python serve.py "$1"
}

black() {
  python -m black --extend-exclude migrations --skip-string-normalization .
}

compile_reqs() {
  pip-compile requirements.in --resolver=backtracking > requirements.txt
}


"$@"