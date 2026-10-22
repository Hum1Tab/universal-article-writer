# Assets

| File | Purpose |
|---|---|
| `banner.svg` | Banner used at the top of the three READMEs. 1280×360. |
| `social-preview.svg` | Source for the GitHub social preview. 1280×640. |
| `social-preview.png` | PNG to upload under **Settings → Social preview**. |
| `social-preview.html` | Local render helper for the PNG (no build system required). |
| `banner.html` | Local render helper for inspecting the banner. |
| `source-ledger.csv` | Source-ledger template. |
| `claim-evidence.csv` | Claim–evidence matrix template. |
| `argument-map.md` | Toulmin argument-map template. |
| `article-brief.md` | Intake template. |
| `dossier-template.md` | Evidence-dossier template. |
| `review-scorecard.md` | Red-team scorecard. |

## Regenerating the social preview

Open `social-preview.html` in a browser and capture the 1280×640 viewport, or
use a headless browser:

```bash
msedge --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1280,640 \
  --screenshot=assets/social-preview.png \
  "file:///absolute/path/to/assets/social-preview.html"
```

On Windows, `msedge.exe` is usually at
`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`.

The PNG is a convenience for GitHub's social-preview upload. `social-preview.svg`
remains the editable source.
