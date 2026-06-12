### AnyKernel3 Ramdisk Mod Script
### tulip (Redmi Note 6 Pro / SDM636) - A15 LineageOS Bouquet (DYNAMIC, FBE v2)

properties() { '
kernel.string=C9 Custom Kernel for Redmi Note 6 Pro (tulip) - Bouquet A15
do.devicecheck=1
do.modules=0
do.systemless=1
do.cleanup=1
do.cleanuponabort=0
device.name1=tulip
device.name2=Tulip
device.name3=TULIP
device.name4=bouquet
device.name5=twolip
supported.versions=
supported.patchlevels=
'; } # end properties

# shell variables
block=/dev/block/bootdevice/by-name/boot;
is_slot_device=0;
ramdisk_compression=auto;
patch_vbmeta_flag=auto;

# Banner
ui_print " ";
ui_print "**************************************";
ui_print "*  C9 Custom Kernel for Tulip 4.19   *";
ui_print "*  Codename: BKZ                     *";
ui_print "*  Base: Bouquet DuckG 4.19 + KSUN   *";
ui_print "*  ROM: LineageOS 22.1 A15 (dynamic) *";
ui_print "*  Mode: SELinux enforcing           *";
ui_print "**************************************";
ui_print " ";

## AnyKernel install
. tools/ak3-core.sh;

# DYNAMIC + FBE v2 ROM: do NOT patch fstab, do NOT force permissive, do NOT
# stitch foreign dtb. Keep the ROM boot.img ramdisk + dtb intact; only swap
# the kernel Image. This is the safe path for dynamic-partition A15 builds.
split_boot;
flash_boot;
## end install
