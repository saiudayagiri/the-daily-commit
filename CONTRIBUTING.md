# Contributing to The Daily Commit

Not set up yet? Start with [SETUP.md](SETUP.md).

You want to get a story into tomorrow's paper. Here is the whole journey, and *why* each step exists.

## The four walls you'll hit (and the door through each one)

| You try to… | …but you can't, because | So you… |
|---|---|---|
| Commit straight into this repo | You're not an editor; you have no write access | **Fork** it — GitHub gives you your own full copy under your account |
| Check your story for mistakes on GitHub | GitHub's editor can't run the proofreader script | **Clone** your fork — now the code and the script are on your laptop |
| Commit from your laptop into *this* repo | Still no write access; your laptop only knows your fork | **Push** to your fork — your copy on GitHub is updated |
| Get your story into the real paper | Only editors can merge | **Open a pull request** — "editors, please pull my changes in" |

## Step by step

### 1. Fork (get your own printing press)
Click **Fork** at the top-right of this repository on GitHub. You now have `github.com/<you>/the-daily-commit`. It's yours. Break it however you like.

### 2. Clone (bring the press home)
```bash
git clone https://github.com/<you>/the-daily-commit.git
cd the-daily-commit
```

### 3. Make a branch (one story, one branch)
```bash
git switch -c story/my-headline
```

### 4. Write your story
Open `SUBMISSIONS.md`, copy the template at the top, and paste your story at the **bottom** of the file. Do not edit `README.md` — that is the editors' page. Keep the newspaper voice. Make it up — every story here is fiction.

### 5. Proofread locally (this is the step you *couldn't* do on GitHub)
```bash
python3 scripts/proofread.py
```
Fix everything it complains about. Run it again until you see `🎉 Everything is fit to print.`

### 6. Commit
```bash
git add .
git commit -m "Add story: Council replaces traffic lights with volunteers"
```

### 7. Push to *your* fork
```bash
git push -u origin story/my-headline
```
Notice: you pushed to `origin`, which is **your fork**, not the editors' repo.

### 8. Open a pull request
GitHub will show a banner: *"story/my-headline had recent pushes — Compare & pull request."* Click it. Write a short description. Submit.

The proofreader runs automatically on your PR. If it's red, go back to step 5, fix, commit, push — the PR updates itself. No new PR needed.

### 9. Respond to review
The editor may leave comments. Make the changes, commit, push. Repeat until merged.

## First-time PRs usually fail the proofreader. That's the point.

The most common catches:
- a lowercase letter starting a sentence
- a space before a comma, or no space after one
- `its` / `it's`, `your` / `you're`, `there` / `their`
- a paragraph with no full stop at the end
- the same word repeated twice twice
- the pronoun `i` in lowercase

You'll fix them in a minute *on your laptop* — that's why we cloned.

## Keeping your fork fresh
Once other stories are merged, your fork falls behind. Bring it up to date:
```bash
git remote add upstream https://github.com/<editors>/the-daily-commit.git   # once
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```
