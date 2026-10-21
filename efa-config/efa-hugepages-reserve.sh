#!/usr/bin/sh
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

has_efa=$(lspci -n | grep 1d0f:efa | wc -l)

# RHEL 8.3 on ARM has a different huge page configuration than other
# OSes and defaulted to 512 MB huge page size. This might
# 1. massively over-reserve huge pages, thus run the machine effectively OOM
# 2. not reserve sufficient pages for a process per core worth of huge pages
# To deal with this issue, set huge page size threshold as 16 MB (16384 KB).
# If the default huge page size is larger than the threshold, do NOT use huge pages.
huge_page_size_threshold=16384
huge_pages_size=$(grep "^Hugepagesize:" /proc/meminfo  | awk '{print $2}')
if [ ${huge_pages_size} -gt ${huge_page_size_threshold} ]; then
    cat << EOF
Skipping reserving huge pages, as the default huge page size is ${huge_pages_size} KiB, which is larger than our configured threshold of ${huge_page_size_threshold} KiB.
This is not an error and EFA will continue to function normally.
EOF
    exit 0
fi

huge_pages_file="/sys/kernel/mm/hugepages/hugepages-${huge_pages_size}kB/nr_hugepages"

if [ $(id -u) -ne 0 ]; then
    echo "$0 must be run as root." >&2
    exit 1
fi

if [ ${has_efa} -eq 0 ]; then
    exit 0
fi

if ! [ -f ${huge_pages_file} ]; then
    exit 1
fi

# For each end point, the libfabric EFA provider will create two packet pools,
# which is backed by huge page memory. The two packet pools will use 110 MB of
# memory
efa_ep_huge_pages_memory=$((110 * 1024)) # convert to kB
number_of_cores=$(lscpu -e=ONLINE | grep -ci yes)

# Open MPI (4.1.0 and above) will open two libfabric end points (for libfabric 1.12
# and above). One is used by mtl/ofi compoent, the other is used by the btl/ofi
# component. Thus we multiply by 2 here.
efa_total_huge_pages_memory=$(($efa_ep_huge_pages_memory * $number_of_cores * 2))
efa_number_of_huge_pages=$(($efa_total_huge_pages_memory / $huge_pages_size + 1))
cur_number_of_huge_pages=$(cat $huge_pages_file)

if [ $cur_number_of_huge_pages -lt $efa_number_of_huge_pages ]; then
    echo $efa_number_of_huge_pages > ${huge_pages_file}
fi
