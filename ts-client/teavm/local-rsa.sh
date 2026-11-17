#!/usr/bin/env bash
# Point a browser build at a LOCAL engine's login key, for testing against a world you run
# yourself. Run it after setup.sh and before `mvn package`.
#
# The login block is RSA-encrypted with a key compiled into the client (Client.LOGIN_RSAN), and a
# local engine makes its own pair with `npm run rsa`. They do not match, so the server cannot
# decrypt the block and answers 6 - the same code as a revision mismatch, which is why this looks
# like "RuneScape has been updated! Please reload this page" and no reload helps.
#
#   ./local-rsa.sh "$(cd ../../../deathplateau-engine && node -e "
#     const forge=require('node-forge'),fs=require('fs');
#     console.log(forge.pki.privateKeyFromPem(fs.readFileSync('data/config/login-rsa.pem','ascii')).n.toString(10));")"
#
# The local engine must also take this client's revision: ENGINE_REVISION=384 in its .env.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MOD="${1:-}"
[ -n "$MOD" ] || { echo "usage: ./local-rsa.sh <decimal modulus of the local engine's login-rsa.pem>" >&2; exit 1; }
F="$HERE/src/main/java/jagex2/client/Client.java"
[ -f "$F" ] || { echo "no $F - run setup.sh first" >&2; exit 1; }
python3 - "$F" "$MOD" <<'PY'
import re, sys
f, mod = sys.argv[1], sys.argv[2]
s = open(f).read()
new, n = re.subn(r'(LOGIN_RSAN = new BigInteger\(")\d+(")', lambda m: m.group(1) + mod + m.group(2), s, count=1)
if n != 1:
    raise SystemExit("could not find LOGIN_RSAN in " + f)
open(f, 'w').write(new)
print("LOGIN_RSAN set to the local engine's key")
PY
