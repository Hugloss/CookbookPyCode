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

The old guide used `chattr +i` on a regular resolver file. Inspect that file's
attributes and remove the immutable flag **only if you previously set it**:

```bash
sudo lsattr /etc/resolv.conf
```

If the output includes the `i` flag on the old regular file:

```bash
sudo chattr -i /etc/resolv.conf
```

If this path is a symlink or managed by another resolver, do not change the
target's attributes blindly. Check your resolver configuration first. Stop on
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

Inside **Ubuntu**:

```bash
cat /etc/resolv.conf
getent hosts pypi.org
curl --fail --show-error --head --max-time 20 https://pypi.org/simple/
```

Use your organization's approved package-index hostname/URL instead when public
PyPI access is intentionally blocked. While connected to the VPN, also test a
real internal hostname you normally use:

```bash
getent hosts YOUR_INTERNAL_HOSTNAME
```

Replace the placeholder before running it. Public DNS success alone does not
verify internal names, split DNS, or access to an internal package index. If the
hostname also fails in Windows, check the Windows/VPN connection first.

| Symptom | Next check |
| --- | --- |
| Name does not resolve | Windows/VPN DNS, regenerated `/etc/resolv.conf`, and whether `generateResolvConf=false` is still configured. |
| Name resolves but connection times out | VPN route, proxy requirements, service availability, or firewall policy. |
| HTTPS reports a certificate verification error | Install the approved CA in Ubuntu and follow the [uv/certificate guide](wsl_3_uv_setup.md). |
| Proxy configuration uses a PAC URL | Linux clients do not all interpret PAC automatically; obtain the supported proxy setup from your organization. |
| A local development port is unreachable | Check the application is listening and the applicable Windows/Hyper-V firewall rules. Test the actual port. |

`autoProxy=true` imports proxy information; it does not import Windows CA trust
into Ubuntu. DNS, proxy routing, and TLS verification are different checks.
Keep firewall changes scoped to the required service; do not disable the
firewall to make a connectivity check pass.

## 3. If mirrored networking does not work with your VPN

Update WSL and inspect Microsoft's [known networking issues][troubleshooting].
For a controlled comparison, change only `networkingMode` to `nat` in your
existing `.wslconfig`, retaining `dnsTunneling=true` on supported Windows.
Save work, shut down WSL, reopen the distro, and repeat the same checks. If this
does not help, restore the prior setting. NAT changes Windows/WSL addressing;
consult the [networking guide][networking] for the relevant connection direction.

For older Windows versions without DNS tunneling, use Microsoft's documented
VPN workaround only when needed, using the DNS servers supplied by your VPN or
organization. Static public resolvers are not a general replacement for
corporate DNS. Keep a rollback copy and preserve unrelated settings.

If you need to restore the old files, use the backup directory printed earlier.
After verifying that it contains your saved copies, restore `/etc/wsl.conf` and
the resolver file from inside Ubuntu, then restart WSL from PowerShell. Restoring
`generateResolvConf=false` also restores the incompatibility with tunneling; it
is a rollback for diagnosis, not the desired final setup.

[networking]: https://learn.microsoft.com/en-us/windows/wsl/networking
[troubleshooting]: https://learn.microsoft.com/en-us/windows/wsl/troubleshooting#networking-considerations-with-dns-tunneling
