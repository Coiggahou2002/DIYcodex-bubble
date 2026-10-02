# Anonymous submissions: maintainer setup

The gallery remains on GitHub Pages. A Cloudflare Worker receives submissions and writes to a **private** GitHub repository. No AI generation is involved. Public publication remains a separate, human-reviewed action.

## Production requirements

1. Sign into Cloudflare using an email you will retain after graduation. Use the Workers Free plan; do not add a paid plan or domain for this workflow.
2. Create a GitHub fine-grained token limited to the private queue repository, with Contents: read/write. Store it only as Worker secret `GITHUB_TOKEN`. Never use a broad personal token in the hosted Worker or commit a token.
3. Create a Turnstile widget allowing `kaitongg-bit.github.io`. Store its secret as `TURNSTILE_SECRET`. Its public site key goes in `app/static/submission-config.json`.
4. Deploy `community/worker.mjs` using `community/wrangler.jsonc`. The queue repository must already have an initial commit; the API refuses a public repository before sending any image bytes.
5. Set `submission-config.json` to the verified Worker URL (`https://<worker>.workers.dev/api/submissions`) and the public site key. Until configured, the public form explicitly says submissions are not yet enabled.
6. Verify a real anonymous submission from Pages, Turnstile failure, invalid PNG, oversize image, unauthorized origin, and private queue visibility. Do not label local testing as production verification.

GitHub and Cloudflare free quotas apply; this setup does not promise unlimited free storage or requests. Turnstile, filename-independent IDs, PNG limits and a honeypot reduce abuse but are not a guarantee. Monitor usage and pause submissions by clearing the public endpoint if necessary. The API accepts PNG headers; the reviewer must decode and inspect the full image before publishing it.

## Daily review

```sh
python3 scripts/review-submissions.py list
python3 scripts/review-submissions.py inspect <id> --output /tmp/bubble-review
python3 scripts/review-submissions.py approve <id> --reason 'Image and rights reviewed'
python3 scripts/review-submissions.py reject <id> --reason 'Reason'
```

Requires the maintainer's normal `gh` login. List prints pendingCount; rejected/approved entries stay private for the audit trail. Approval changes the review record only. After approval, inspect the image and tune the nine-slice config in the studio, copy only approved PNG/config into `community/approved`, update its manifest, publish PNG assets to the preset release, and export/publish the Pages branch. No public API can approve submissions. Do not publicly expose the private queue, tokens or unreviewed PNGs.

## Local acceptance test

`node scripts/submission-local.mjs /tmp/bubble-submission-preview 19334` provides a loopback-only development adapter. It captures the existing gh token only inside the server process and writes only to the named private queue. It does not deploy a Worker and does not enable online submissions. Stop the server after testing. Export first with `python3 scripts/export-gallery.py /tmp/bubble-submission-preview`.

On 2026-10-02, the maintainer-authorized fluffy-cat PNG was submitted through the browser form under `demo-visitor（流程测试）`, received in the real private queue, reviewed, approved and published. After production deployment, a second submission from the public GitHub Pages form passed Turnstile, reached the private queue, matched the original PNG hash, and was approved; the pending count returned to zero. Public author attribution remains kaitongg and both nicknames are explicitly fictional. Production intake uses `diycodex-bubble-submissions.kaitongguan.workers.dev`, Turnstile and the private review repository.
