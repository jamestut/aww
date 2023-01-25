# Apple Wi-Fi Workaround (AWW)

The goal of this project is to workaround Wi-Fi problems on macOS.

Apple Developer Command Line Tools are required for both compiling and using.

Due to the nature of this tool, this tool requires root access. It will call `sudo` automatically if it is not currently running as root user.

## Usage

1. Clone this repo.

2. Go to `nativeapi` directory, and run `make` to compile the native library.

3. Simply run `python3 /path/to/this/repo`. Can optionally set an alias in your shell for better convenience.

## Available Workarounds

- `airportd`
  This workaround suspends the `airportd` program to disable Wi-Fi roaming and scanning. When this workaround is active, connecting to a different Wi-Fi will not work. Wi-Fi list on the UI will also freeze. Should the current Wi-Fi connection becomes out of range and disconnected, no further reconnection attempt will be made until this workaround is disabled.

- `awdl`
  This workarounds suspends AirPlay (the `AirPlayXPCHelper` process) and disables the `awdl0` interface to avoid ping spikes for a much more stable internet. When this workaround is active, AirPlay will not work. Additionally, automatic audio sink/source switching when connecting and/or disconnecting Bluetooth audio will not work until this workaround is disabled (already connected Bluetooth audio will work just fine).
