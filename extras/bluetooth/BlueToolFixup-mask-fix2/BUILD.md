# BlueToolFixup Tahoe-mask-fix2 source

This snapshot is the exact BlueToolFixup.cpp archived with the deployed mask-fix2 build (2026-11-10). It inherits Acidanthera BrcmPatchRAM and crazyhulk's BlueToolFixup-FixA2DP-BLE work. Original copyright and GPL-2.0 notices remain. Only the BlueToolFixup target is supplied for this build; no Broadcom firmware products are distributed here.

Local changes: masked matching of three rel32-sensitive bluetoothd sequences, preservation of actual relative displacements, and normalization of Lilu's unmasked needle with `find & mask`. `patches/` preserves the two incremental patches for review; the source already contains them, so do not apply them again. The earlier fix1 alone had incorrect matcher semantics and is not the released binary.

Dependencies: Xcode, MacKernelSDK, and Lilu 1.7.2 DEBUG developer resources. Obtain the SDK from https://github.com/acidanthera/MacKernelSDK and the Lilu developer Kext from https://github.com/acidanthera/Lilu/releases/tag/1.7.2 . Put the SDK in `MacKernelSDK/` and the developer bundle in `Lilu.kext/` next to this project. The DEBUG Lilu bundle is a build dependency; the companion binary package supplies the RELEASE Lilu actually loaded on the test host. Do not install both.

```bash
xcodebuild -project BrcmPatchRAM.xcodeproj -target BlueToolFixup \
  -configuration Release ARCHS=x86_64 CODE_SIGNING_ALLOWED=NO \
  SYMROOT="$PWD/build/products" OBJROOT="$PWD/build/obj" build
codesign --force --sign - --timestamp=none build/products/Release/BlueToolFixup.kext
codesign --verify --strict build/products/Release/BlueToolFixup.kext
```

The original build used Xcode with the macOS26.5 SDK. Output paths and toolchain differences can alter UUID/hash; a successful build does not certify other bluetoothd builds or prove discovery stability. Install instructions and the tested binary hashes are in docs/AX211-BLUETOOTH.zh-CN.md and the companion package manifest.
