# Release

Application releases.

To package source code use the following tar command.

```shell
(cd ˜/Documents/GitHub/pi-netconfig/src && tar -czf ˜/Documents/GitHub/pi-netconfig/release/pi-netconfig.tar.gz $(find . -mindepth 1 -maxdepth 1 ! -name ".*"))
```


Copyright (c) 2025 William Watson. This work is licensed under the MIT License.