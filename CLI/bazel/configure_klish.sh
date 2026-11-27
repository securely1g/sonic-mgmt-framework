#!/bin/sh
# Stage the declared Autotools inputs so autoreconf can generate files in the sandbox.
set -eu
src=${1#--srcdir=}
shift
case "$1" in
    --build=auto) shift ;;
    *) exit 2 ;;
esac
target=${1#--host=}
shift
work=$PWD
stage=$work/autotools-source
mkdir -p "$stage"
cd "$src"
cp --parents autogen.sh configure.ac Makefile.am clish/plugin_builtin.c.in libc/getopt.c m4/*.m4 "$stage"
find . -name module.am -exec cp --parents '{}' "$stage" \;
cd "$stage"
"$CONFIG_SHELL" ./autogen.sh
build=$("$CONFIG_SHELL" aux_scripts/config.guess)
host=$("$CONFIG_SHELL" aux_scripts/config.sub "$target")
cd "$work"
"$CONFIG_SHELL" "$stage/configure" --srcdir="$stage" --build="$build" --host="$host" "$@"
rm -rf "$stage"
