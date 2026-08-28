# SmartSafeHub OpenWrt Packages

OpenWrt package repository for SmartSafeHub and SafeShield.

## Package versions

The badges below show the versions currently published to each repository channel. They are read from the generated `versions.json`, so the README does not need to be updated for each release.

| Package | Stable | Beta |
| --- | --- | --- |
| SmartSafeHub | [![Stable SmartSafeHub](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frepo.smartsafehub.com%2Fstable%2Fversions.json&query=%24.packages%5B%22luci-app-smartsafehub%22%5D&label=&color=brightgreen&cacheSeconds=300)](https://repo.smartsafehub.com/stable/versions.json) | [![Beta SmartSafeHub](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frepo.smartsafehub.com%2Fbeta%2Fversions.json&query=%24.packages%5B%22luci-app-smartsafehub%22%5D&label=&color=orange&cacheSeconds=300)](https://repo.smartsafehub.com/beta/versions.json) |
| SafeShield | [![Stable SafeShield](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frepo.smartsafehub.com%2Fstable%2Fversions.json&query=%24.packages%5B%22safeshield%22%5D&label=&color=brightgreen&cacheSeconds=300)](https://repo.smartsafehub.com/stable/versions.json) | [![Beta SafeShield](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frepo.smartsafehub.com%2Fbeta%2Fversions.json&query=%24.packages%5B%22safeshield%22%5D&label=&color=orange&cacheSeconds=300)](https://repo.smartsafehub.com/beta/versions.json) |
| LuCI SafeShield | [![Stable LuCI SafeShield](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frepo.smartsafehub.com%2Fstable%2Fversions.json&query=%24.packages%5B%22luci-app-safeshield%22%5D&label=&color=brightgreen&cacheSeconds=300)](https://repo.smartsafehub.com/stable/versions.json) | [![Beta LuCI SafeShield](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frepo.smartsafehub.com%2Fbeta%2Fversions.json&query=%24.packages%5B%22luci-app-safeshield%22%5D&label=&color=orange&cacheSeconds=300)](https://repo.smartsafehub.com/beta/versions.json) |

`versions.json` is generated from the `index.json` files of the packages that were actually built and staged for publication. Deployment fails if the tracked package versions differ between architectures.

## Repository channels

- **Stable**: production packages built from the `main` branches.
- **Beta**: development packages built from the `develop` branches.

Repository root: <https://repo.smartsafehub.com/>
