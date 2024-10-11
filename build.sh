#!/usr/bin/env bash
#
# Simple build script for py-sqlshell. Run as:
#
# ./build.sh target ...
#
# Valid targets: build, clean

usage() {
  echo "Usage: $0 target ..." >&2
  echo "       $0 -h" >&2
  echo "Valid targets: build, clean, docker >&2" >&2
  echo "Default: clean build"
  exit 1
}

run() {
  echo "+ $1"
  eval $1
  rc=$?
  if [ $rc != 0 ]
  then
    echo "--- Failed: $rc" >&2
    return 1
  fi
}

case $# in
  0)
    targets="clean build"
    ;;
  1)
    if [ "$1" = "-h" ]
    then  
      usage
    fi
    targets="$1"
    ;;
  *)
    targets="$*"
    ;;
esac

# Validate targets
for t in $targets
do
  case $t in
    build|clean|docker)
      ;;
    *)
      usage
      ;;
  esac
done

# Run targets
for t in $targets
do
  case $t in
    clean)
      run "rm -rf *.egg-info" || exit 1
      run "rm -rf dist" || exit 1
      run "rm -rf __pycache__" || exit 1
      run "rm -rf sqlshell/__pycache__" || exit 1
      ;;

    build)
      run "python -m build" || exit 1
      ;;

    docker)
      cd docker
      run "docker build -t bclapper/py-sqlshell-test ." || exit 1
      cd ..
      ;;
  esac
done
