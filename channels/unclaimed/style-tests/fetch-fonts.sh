#!/usr/bin/env bash
# Fetch the 14 faces build-ep02.py needs into work-ep02/fonts.
#
# The Episode 5 script reads macOS system fonts. This run was built in a Linux
# container, so the Episode 2 set uses Google Fonts equivalents instead:
#   Anton        stands in for Impact          (Style 2B slam type)
#   Public Sans  the real US Web Design System face (Style 6 government pages)
#   IBM Plex Mono, Source Serif, DM Serif, Oswald  (Style 9 archival register)
#
# Run once after a fresh clone, before build-ep02.py.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)/work-ep02/fonts"
mkdir -p "$D"

fetch() {  # family-spec  outfile
  local url
  url=$(curl -sS -H "User-Agent: Mozilla/5.0" \
        "https://fonts.googleapis.com/css2?family=$1" \
        | grep -o 'https://fonts.gstatic.com[^)]*\.ttf' | head -1)
  if [ -z "$url" ]; then echo "could not resolve $1" >&2; return 1; fi
  curl -sS -o "$D/$2" "$url"
  echo "  $2"
}

echo "fetching fonts into $D"
fetch "Anton"                      anton.ttf
fetch "Archivo+Black"              archivoblack.ttf
fetch "Oswald:wght@700"            oswald-bold.ttf
fetch "Inter:wght@400"             inter-regular.ttf
fetch "Inter:wght@600"             inter-semibold.ttf
fetch "Inter:wght@700"             inter-bold.ttf
fetch "IBM+Plex+Mono:wght@500"     plexmono.ttf
fetch "IBM+Plex+Mono:wght@700"     plexmono-bold.ttf
fetch "DM+Serif+Display"           dmserif.ttf
fetch "Space+Mono:wght@700"        spacemono-bold.ttf
fetch "Barlow+Condensed:wght@700"  barlowcond.ttf
fetch "Public+Sans:wght@700"       publicsans-bold.ttf
fetch "Public+Sans:wght@400"       publicsans.ttf
fetch "Source+Serif+4:wght@600"    sourceserif.ttf
echo "done. now run: python3 build-ep02.py"
