# Setup

Two audiences: the **editor** (instructor) who runs the paper, and **reporters** (students) who submit stories.

## For the editor (one-time)

1. **Create the repo.** Fork or copy this repository into your own GitHub account. Keep it public so students can fork it.
2. **Protect `main`.** Settings → Branches → Add rule for `main`:
   - Require a pull request before merging (1 approval).
   - Require status checks to pass: select `proofread`.
   - Leave "Include administrators" off so you can still push fixes.
   
   Or do it from the command line:
   ```bash
   gh api -X PUT repos/<you>/the-daily-commit/branches/main/protection --input - <<'JSON'
   {"required_status_checks":{"strict":true,"contexts":["proofread"]},
    "enforce_admins":false,
    "required_pull_request_reviews":{"required_approving_review_count":1},
    "restrictions":null}
   JSON
   ```
3. **Let first-time contributors' checks run.** Settings → Actions → General → "Fork pull request workflows from outside collaborators" → *Require approval for first-time contributors who are new to GitHub* (or lower). Otherwise you must click "Approve and run" on every new student's PR before it turns red or green.
4. **Check CI is alive.** The Actions tab should show a green `Proofreader` run for the latest commit on `main`.
5. **Print a new edition (optional).** Change the date badge at the top of `README.md` and empty out `SUBMISSIONS.md` back to its template before each class.

## For reporters (each student)

You need three things on your laptop: Git, Python 3, and a GitHub account.

| Tool | Check it's installed | Install if missing |
|------|----------------------|--------------------|
| Git | `git --version` | https://git-scm.com/downloads |
| Python 3.8+ | `python3 --version` | https://www.python.org/downloads/ |
| GitHub account | log in at https://github.com | Sign up, then verify your email |

Then tell Git who you are (once):
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Verify everything works by cloning **your fork** (not the editor's repo) and running the proofreader:
```bash
git clone https://github.com/<you>/the-daily-commit.git
cd the-daily-commit
python3 scripts/proofread.py
```
You should see `🎉 Everything is fit to print.` If you do, you are set up. Now read [CONTRIBUTING.md](CONTRIBUTING.md) and write your story in [SUBMISSIONS.md](SUBMISSIONS.md).

## Running the checks

```bash
python3 scripts/proofread.py                 # check README.md, SUBMISSIONS.md and newsroom/
python3 scripts/proofread.py SUBMISSIONS.md  # check one file
python3 -m unittest scripts/test_proofread.py  # test the proofreader itself
```

## Troubleshooting

- **`python3: command not found` on Windows** — try `py -3 scripts/proofread.py`.
- **Push rejected: "protected branch"** — you pushed to the editor's repo instead of your fork. Check `git remote -v`; `origin` should point at `github.com/<you>/…`.
- **The PR check is red but the script passes locally** — you probably didn't push your latest commit. Run `git status` and `git push`.
- **My fork is behind** — see "Keeping your fork fresh" in [CONTRIBUTING.md](CONTRIBUTING.md).
