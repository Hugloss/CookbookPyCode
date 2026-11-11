# WSL2 DNS and VPN troubleshooting

[Setup index](README.md) · Previous: [WSL installation](wsl_1_install.md) · Next: [uv setup](wsl_3_uv_setup.md)

On Windows 11 22H2 or newer with updated WSL, start with the
[`.wslconfig` profile](wsl_1_install.md#2-configure-wsl2-on-windows): mirrored
networking, DNS tunneling, and Windows proxy integration. Microsoft's
[networking guide][networking] describes these features and their prerequisites.

An earlier version of this cookbook disabled DNS generation, replaced the
resolver with static public DNS servers, and made `/etc/resolv.conf` immutable.
Those settings conflict with DNS tunneling and can break corporate DNS. Follow
the migration below only if you applied that workaround. A fresh installation
can go straight to verification.

## 1. Restore automatic DNS after the old workaround

Microsoft explicitly states that DNS tunneling requires `generateResolvConf`
not to be disabled. See [networking considerations with DNS tunneling][troubleshooting].

First inspect the existing settings **inside Ubuntu**:

```bash
if [ -f /etc/wsl.conf ]; then
    cat /etc/wsl.conf
fi
ls -l /etc/resolv.conf
cat /etc/resolv.conf
```

If you used the old static-DNS workaround, make a backup before editing. Keep
the printed backup directory for a possible rollback:

```bash
(
    set -eu
    dns_backup_dir=$(sudo mktemp -d /etc/wsl-dns-backup.XXXXXX)
    sudo cp -a /etc/resolv.conf "$dns_backup_dir/resolv.conf"
    if [ -f /etc/wsl.conf ]; then
        sudo cp -a /etc/wsl.conf "$dns_backup_dir/wsl.conf"
    fi
    printf 'DNS backup: %s\n' "$dns_backup_dir"
)
```

Stop if the backup block fails. After it succeeds, edit the configuration:

```bash
sudo nano /etc/wsl.conf
```

In the existing `[network]` section, remove `generateResolvConf=false` or change
it to `true`. If you retain the key, it should read:

```ini
[network]
generateResolvConf=true
```

Preserve all other sections and settings, including `[boot]`, `[user]`, and
mount configuration. Do not replace the whole file with the snippet.

The old guide used `chattr +i` on a regular resolver file. The immutable flag
prevents changes to the file; it does not by itself prevent reads or establish
the cause of a network outage. See [chattr][chattr]. Inspect that file's
attributes and remove the immutable flag **only if you previously set it**:

```bash
sudo lsattr /etc/resolv.conf
```

If the output includes the `i` flag on the old regular file:

```bash
sudo chattr -i /etc/resolv.conf
```

The presence of a symlink is not itself evidence that DNS is broken. If this
path is a symlink or managed by another resolver, do not change the target's
attributes blindly. Check your resolver configuration first. Stop on
any unexpected error. For the old regular static file, remove that active copy
after the backup and config edit succeeded so WSL can recreate it:

```bash
sudo rm -- /etc/resolv.conf && exit
```

Save work and close WSL-connected applications. In **ordinary PowerShell**, use
the exact installed distro name:

```powershell
wsl --shutdown
wsl --distribution Ubuntu
```

The shutdown affects all distributions. On restart, WSL should generate a new
resolver file. Do not add public DNS servers or make the generated file immutable.

## 2. Verify DNS, routing, and HTTPS separately

First check the active network **inside Ubuntu**:

```bash
wslinfo --networking-mode
ip -br address
ip -4 route get 1.1.1.1 ipproto tcp dport 443
```

`wslinfo` reports the [current networking mode][wslinfo]. The [route lookup][routes]
checks the kernel's route for this IPv4/TCP destination without sending packets;
`1.1.1.1` here is a destination, not a DNS setting. A successful lookup does not
prove an HTTPS connection works.

If the only interfaces are `lo` and an inactive `docker0`, and the lookup reports
`Network unreachable`, investigate WSL networking in section 3 before changing
DNS. A Docker bridge alone does not supply the missing upstream connection, and
adding nameservers cannot create an interface or route.

Once there is a usable network path, check DNS and HTTPS:

```bash
cat /etc/resolv.conf
timeout 10s getent hosts pypi.org
curl --fail --show-error --head --max-time 20 https://pypi.org/simple/
```

Use your organization's approved package-index hostname/URL instead when public
PyPI access is intentionally blocked. While connected to the VPN, also test a
real internal hostname you normally use:

```bash
timeout 10s getent hosts YOUR_INTERNAL_HOSTNAME
```

Replace the placeholder before running it. Public DNS success alone does not
verify internal names, split DNS, or access to an internal package index. If the
hostname also fails in Windows, check the Windows/VPN connection first.

| Symptom | Next check |
| --- | --- |
| No usable interface and a numeric TCP route lookup reports `Network unreachable` | WSL's active mode, Windows network/VPN, and the restart/comparison steps below. |
| Name does not resolve | Windows/VPN DNS, regenerated `/etc/resolv.conf`, and whether `generateResolvConf=false` is still configured. |
| Name resolves but connection times out | VPN route, proxy requirements, service availability, or firewall policy. |
| HTTPS reports a certificate verification error | Install the approved CA in Ubuntu and follow the [uv/certificate guide](wsl_3_uv_setup.md). |
| Proxy configuration uses a PAC URL | Linux clients do not all interpret PAC automatically; obtain the supported proxy setup from your organization. |
| A local development port is unreachable | Check the application is listening and the applicable Windows/Hyper-V firewall rules. Test the actual port. |

`autoProxy=true` imports proxy information; it does not import Windows CA trust
into Ubuntu. DNS, proxy routing, and TLS verification are different checks.
Keep firewall changes scoped to the required service; do not disable the
firewall to make a connectivity check pass.

## 3. If WSL has no network or mirrored mode fails with your VPN

Compare the active mode reported above with the saved configuration. In
**ordinary PowerShell under the distro's owning Windows account**:

```powershell
$wslConfigPath = Join-Path $env:USERPROFILE ".wslconfig"
Get-Item -LiteralPath $wslConfigPath | Select-Object FullName, Length
Get-Content -LiteralPath $wslConfigPath
```

A missing file, blank output, or an unsaved edit does not establish the current
mode. Check the account, full filename (without `.txt`), and saved contents.
Configuration changes apply when the WSL VM restarts; see Microsoft's
[configuration reference][config].

Update WSL and inspect Microsoft's [known networking issues][troubleshooting].
For a controlled comparison, change only `networkingMode` to `nat` in your
existing `.wslconfig`, retaining `dnsTunneling=true` on supported Windows.
Save work, close applications that could restart WSL, run `wsl --shutdown` in
PowerShell, and reopen the distro. This stops all distributions. Repeat
`wslinfo --networking-mode` and the same interface, route, DNS, and HTTPS checks.
Treat NAT as a comparison, not a confirmed fix. If this does not help, restore
the prior setting and restart again. If the expected mode does not take effect,
check for startup warnings and organization-managed [WSL policies][policies].
NAT changes Windows/WSL addressing;
consult the [networking guide][networking] for the relevant connection direction.

For older Windows versions without DNS tunneling, use Microsoft's documented
VPN workaround only when needed, using the DNS servers supplied by your VPN or
organization. Static public resolvers are not a general replacement for
corporate DNS. Keep a rollback copy and preserve unrelated settings.

For applications using glibc's resolver directly, `/etc/resolv.conf` supports up
to three nameservers and normally tries them in order, moving on after a timeout.
It does not choose an office DNS server by domain just because you mix office
and public servers in the list. See [resolv.conf][resolver]. On supported WSL,
prefer DNS tunneling so Windows can apply the VPN's DNS policies.

If you need to restore the old files, use the backup directory printed earlier.
After verifying that it contains your saved copies, restore `/etc/wsl.conf` and
the resolver file from inside Ubuntu, then restart WSL from PowerShell. Restoring
`generateResolvConf=false` also restores the incompatibility with tunneling; it
is a rollback for diagnosis, not the desired final setup.

[networking]: https://learn.microsoft.com/en-us/windows/wsl/networking
[troubleshooting]: https://learn.microsoft.com/en-us/windows/wsl/troubleshooting#networking-considerations-with-dns-tunneling
[config]: https://learn.microsoft.com/en-us/windows/wsl/wsl-config
[wslinfo]: https://github.com/microsoft/WSL/discussions/10590
[policies]: https://learn.microsoft.com/en-us/windows/wsl/intune
[routes]: https://man7.org/linux/man-pages/man8/ip-route.8.html
[resolver]: https://man7.org/linux/man-pages/man5/resolv.conf.5.html
[chattr]: https://man7.org/linux/man-pages/man1/chattr.1.html
