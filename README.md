# C9 Kernel — Tulip 4.19 A15 (LineageOS Bouquet, Dynamic)

Custom kernel **KernelSU-Next** untuk Xiaomi Redmi Note 6 Pro (codename **tulip**) di ROM **LineageOS 22.1 Bouquet (Android 15, dynamic partition, FBE v2)**.

- **Codename build:** BKZ
- **Base source:** `Bouquet-Dynamic-Development/kernel_nope_sdm660` @ `staging-mlgru` (kernel DuckG asli ROM ini — sudah punya patch dynamic/FBE-v2/A15)
- **Defconfig:** `vendor/bouquet_defconfig`
- **SU:** KernelSU-Next legacy (inject hook, source belum punya KSU)
- **Toolchain:** Neutron Clang + LLD
- **Target:** Android 15 / LineageOS 22.1 Bouquet (tulip + whyred unified)

## Kenapa custom?
ROM Bouquet bawa KSU-Next Manager tapi **driver KSU belum ke-integrate di kernel** (Manager: "Unsupported | Not integrated — Non-GKI kernels are not supported"). Build ini meng-inject driver KSU-Next legacy ke kernel DuckG.

## Catatan dynamic A15
- AnyKernel cuma swap zImage — ramdisk + dtb dari boot.img ROM dipertahankan (WAJIB untuk dynamic+FBE v2).
- TIDAK ada stitch DTB stock / patch fstab / force permissive (itu khusus device non-dynamic).

## Flash
Backup boot dulu. Flash zip AnyKernel3 via recovery ROM Bouquet (gunakan recovery yang disediakan ROM).
