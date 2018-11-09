#!/usr/bin/env bash
#1. Get a live cd, for example, Ubuntu. For this article, I use Ubuntu 6.06 (I cannot find any latest version of ubuntu at my place)
#2. Boot using the live cd. Search for these tools: lvm2. If the cd do not have it, install it.
# $ apt-get install lvm2
#mkdir /mnt/HardDrive && # already done
#3. To make sure the harddisk is recognised, you can use fdisk
fdisk -lu &&
#4. Once installed, run pvscan to scan all disks for physical volume. this to make sure your LVM harddisk is detected by Ubuntu
pvscan &&
# PV /dev/sda2 VG VolGroup00 lvm2 [74.41 GB / 32.00 MB free]
# Total: 1 [74.41 GB] / in use: 1 [74.41 GB] / in no VG: 0 [0 ]
#5. After that run vgscan to scan disks for volume groups.
vgscan &&
# Reading all physical volumes. This may take a while...
# Found volume group "VolGroup00" using metadata type lvm2
#6. Activate all volume groups available.
vgchange -a y &&
# 2 logical volume(s) in volume group "VolGroup00" now active
#7. Run lvscan to scan all disks for logical volume. You can see partitions inside the hard disk now active.
lvscan &&
# ACTIVE '/dev/VolGroup00/LogVol00' [72.44 GB] inherit
# ACTIVE '/dev/VolGroup00/LogVol01' [1.94 GB] inherit
#8. Mount the partition to any directory you want, usually to /mnt
mount /dev/ubuntu-vg/root /mnt/HardDrive
#9. You can access the partition in the /mnt directory and can backup your data
