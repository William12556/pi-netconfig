# Release

Application releases.

To package source code use the following tar command.

```shell
(cd ˜/Documents/GitHub/pi-netconfig/src && tar -czf ˜/Documents/GitHub/pi-netconfig/release/pi-netconfig.tar.gz $(find . -mindepth 1 -maxdepth 1 ! -name ".*"))
```

To download the tar package.
```shell
curl -L -o pi-netconfig.tar.gz https://github.com/William12556/pi-netconfig/releases/latest/download/pi-netconfig.tar.gz
```

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.