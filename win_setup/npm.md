# Node.js and npm on Ubuntu WSL

These commands run **inside Ubuntu WSL**, not native Windows PowerShell.
First install [nvm for Linux](https://github.com/nvm-sh/nvm) using an
organization-approved installation method, and complete the
[proxy and CA preflight](wsl_3_uv_setup.md). If `command -v nvm` fails, install
nvm before running the commands below. Native Windows users need separate
Windows Node/nvm instructions.

```bash
nvm install --lts
nvm use --lts
node --version
npm --version
```

Use the npm version bundled with the selected Node LTS initially; a blanket
`npm install -g npm@latest` can select an npm major incompatible with your Node
version. For reproducible projects, pin a supported Node version in `.nvmrc`
and commit the project's dependency lockfile.

## Corporate CA configuration (only if needed)

First install the approved corporate root CA in the **Ubuntu** trust store
using [the WSL guide](wsl_3_uv_setup.md#install-an-approved-corporate-ca-before-https-downloads).
If npm still requires an explicit CA bundle in Ubuntu WSL:

```bash
test -s /etc/ssl/certs/ca-certificates.crt
npm config set cafile /etc/ssl/certs/ca-certificates.crt
```

Leave npm defaults alone when they already work; never disable `strict-ssl`
to bypass certificate errors. A Windows-only CA path such as
`C:\_INSTALL\ca-bundle.pem` does not exist in Ubuntu WSL. On native Windows,
use the certificate path approved for that Windows environment instead.
To remove an obsolete user-level override when no longer needed:

```bash
npm config delete cafile
```

Reference: [npm `cafile` setting](https://docs.npmjs.com/cli/v11/using-npm/config/#cafile).
