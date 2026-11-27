"""Verify the target and ABI decisions emitted by the original Klish configure."""

import argparse
import hashlib
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('probe', type=Path)
    parser.add_argument('cpu', choices=['x86_64', 'aarch64'])
    args = parser.parse_args()
    configuration = args.probe / 'configuration'
    header = (configuration / 'config.h').read_text()
    log = (configuration / 'config.log').read_text()
    macros = dict(re.findall(r'^#define (\w+)(?: (.*))?$', header, re.M))
    assert macros['PACKAGE_VERSION'] == '"2.1.4"'
    assert macros['HAVE_LIB_LIBXML2'] == '/**/'
    assert [macros[name] for name in ['SIZEOF_INT', 'SIZEOF_LONG', 'SIZEOF_SIZE_T']] == ['4', '8', '8']
    assert f"host_cpu='{args.cpu}'" in log
    build_cpu = re.search(r"^build_cpu='([^']+)'$", log, re.M)[1]
    cross = "no" if build_cpu == args.cpu else "yes"
    stdout = (configuration / "configure.stdout").read_text()
    assert f"checking whether we are cross compiling... {cross}" in stdout
    assert 'checking for xmlNewDoc in -lxml2' in log and 'checking for libxml/tree.h' in log
    assert 'bazel-out/' not in header and 'execroot/' not in header
    directives = [line.strip() for line in header.splitlines()
                  if line.lstrip().startswith(('#', '/* #undef'))]
    print(json.dumps({'build_cpu': build_cpu, 'target': args.cpu, 'cross_compiling': cross,
                      'version': macros['PACKAGE_VERSION'],
                      'directives': len(directives), 'directives_sha256': hashlib.sha256(
                          '\n'.join(directives).encode()).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    main()
