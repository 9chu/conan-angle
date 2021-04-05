# Conan package recipe of Google ANGLE

This recipe will fetch and build the Google ANGLE project.

Tested under Windows/Linux.

## Requirements

The following dependencies will NOT install automatically.
You may have to install these packages before building the ANGLE.

- Linux

```bash
# from angle/build/install-build-deps.sh
sudo apt install binutils bison bzip2 cdbs curl dbus-x11 dpkg-dev elfutils devscripts fakeroot flex git-core gperf \
  libappindicator3-dev libasound2-dev libatspi2.0-dev libbrlapi-dev libbz2-dev libcairo2-dev libcap-dev libc6-dev \
  libcups2-dev libcurl4-gnutls-dev libdrm-dev libelf-dev libevdev-dev libffi-dev libgbm-dev libglib2.0-dev \
  libglu1-mesa-dev libgtk-3-dev libkrb5-dev libnspr4-dev libnss3-dev libpam0g-dev libpci-dev libpulse-dev libsctp-dev \
  libspeechd-dev libsqlite3-dev libssl-dev libudev-dev libwww-perl libxslt1-dev libxss-dev libxt-dev libxtst-dev \
  locales openbox p7zip patch perl pkg-config python python-dev python-setuptools rpm ruby subversion uuid-dev wdiff \
  x11-utils xcompmgr xz-utils zip libbluetooth-dev libxkbcommon-dev realpath
```

- Windows
    - Python2/3
    - Visual Studio 17/19
    - Windows SDK >= 10.0.19041.0
