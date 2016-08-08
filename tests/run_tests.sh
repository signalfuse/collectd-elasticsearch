#!/bin/bash
PYTHON="python"
if [ ! -z "$1" ]; then
  PYTHON="$1"
fi

PYTHON_VERSION=$(${PYTHON} -V 2>&1)

echo "Interpreter version: ${PYTHON_VERSION}"

tmpfile=$(mktemp /tmp/run_tests.sh.XXXXXX)
trap 'rm -f $tmpfile' 1 2 3 15
for scenario in `ls data`; do
  echo -n "testing against ES $scenario"

  ${PYTHON} ./simulate.py data/${scenario} &> /dev/null &
  pid="$!"
  ${PYTHON} ../elasticsearch_collectd.py > $tmpfile
  if [ $? != 0 ]; then
    echo " [FAILED] returned non 0 exit code"
  else
    grep '^WARN\|^ERROR' $tmpfile > /dev/null
    if [ $? == 1 ]; then
      echo " [OK]"
    else
      echo " [ERROR]"
      grep '^WARN\|^ERROR' $tmpfile
    fi
  fi
  kill $pid
  # wait for the process to avoid bash job termination messages
  wait $pid 2>/dev/null
done
