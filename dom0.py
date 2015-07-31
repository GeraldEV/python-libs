#!/usr/bin/env python

"""
Copyright (c) 2013, Citrix Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re

def default_memory(host_mem_kib):
    """Return the default for the amount of dom0 memory for the
    specified amount of host memory."""

    #
    # The host memory reported by Xen is a bit less than the physical
    # RAM installed in the machine since it doesn't include the memory
    # used by Xen etc.
    #
    # Add a bit extra to account for this.
    #
    gb = (host_mem_kib + 256 * 1024) / 1024 / 1024

    if gb < 24:
        return 752 * 1024
    elif gb < 48:
        return 2 * 1024 * 1024
    elif gb < 64:
        return 3 * 1024 * 1024
    else:
        return 4 * 1024 * 1024

_size_and_unit_re = re.compile("^(-?\d+)([bkmg]?)$", re.IGNORECASE)

def _parse_size_and_unit(s):
    m = _size_and_unit_re.match(s)
    if not m:
        return None

    val = int(m.group(1))
    unit = m.group(2).lower()

    if unit == "g":
        val *= 1024*1024*1024
    elif unit == "m":
        val *= 1024*1024
    elif unit == "k" or unit == "": # default to KiB
        val *= 1024

    return val

def parse_mem(arg):
    """Parse Xen's dom0_mem command line option.

    Return tuple of (amount, min, max) memory in bytes from a string
    in the following format:

        dom0_mem=[min:<min_amt>,][max:<max_amt>,][<amt>]

    See also Xen's docs/txt/misc/xen-command-line.txt."""

    t = arg.split("=")
    if len(t) < 2 or t[0] != "dom0_mem":
        return (None, None, None)

    dom0_mem = None
    dom0_mem_min = None
    dom0_mem_max = None

    #
    # This is an equivalent to the parse_dom0_mem() call in
    # xen/arch/x86/domain_build.c
    #
    for s in t[1].split(","):
        if s.startswith("min:"):
            dom0_mem_min = _parse_size_and_unit(s[4:])
        elif s.startswith("max:"):
            dom0_mem_max = _parse_size_and_unit(s[4:])
        else:
            dom0_mem = _parse_size_and_unit(s)

    return (dom0_mem, dom0_mem_min, dom0_mem_max)

def default_vcpus(host_pcpus):
    """Return the default number of dom0 vcpus for the specified number
    of host pcpus."""

    # Special case (minimum)
    if host_pcpus == 0:
        return 1

    # vCPUs = host_pcpus for host pcpus <= 16
    if host_pcpus <= 16:
        return host_pcpus

    # 16 for anything greater than 16
    return 16
