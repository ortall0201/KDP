# GitHub Workflow Setup Guide

These workflows commit generated books and covers directly to your GitHub repo.

## Prerequisites

1. **OpenAI API Key** - https://platform.openai.com/api-keys
2. **GitHub Personal Access Token** - https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (all repo permissions)
   - Copy the token (starts with `ghp_...`)

---

## Step 1: Configure n8n Credentials (5 min)

### OpenAI Credential
1. n8n → **Credentials** → **Add Credential**
2. Search "OpenAI API"
3. Paste your API key
4. Save as "OpenAI Account"

### GitHub Credential
1. n8n → **Credentials** → **Add Credential**
2. Search "GitHub OAuth2 API" or "GitHub API"
3. Choose authentication method:
   - **Personal Access Token** (simpler)
   - Paste your `ghp_...` token
4. Save as "GitHub Account"

---

## Step 2: Import Workflows

1. **Import**: `2-kdp-content-production-GITHUB.json`
2. **Import**: `3-kdp-cover-design-GITHUB.json`

---

## Step 3: Configure Workflow Settings

### Workflow 2 (Content Production)

Open workflow → Click **"Set Config (EDIT THIS)"** node:

```
niche: "Your Book Topic Here"
book_id: (auto-generated timestamp)
github_owner: "YOUR_GITHUB_USERNAME"  ← CHANGE THIS
github_repo: "KDP"                     ← CHANGE IF DIFFERENT
```

### Workflow 3 (Cover Design)

Open workflow → Click **"Set Config (EDIT THIS)"** node:

```
niche: "Your Book Topic Here"
genre: "health"  (health/business/cookbook/selfhelp/fiction)
book_id: (auto-generated timestamp)
github_owner: "YOUR_GITHUB_USERNAME"  ← CHANGE THIS
github_repo: "KDP"                     ← CHANGE IF DIFFERENT
```

---

## Step 4: Connect Credentials

### For Each Workflow:

1. Click **"Generate Outline"** node (Workflow 2) or **"Generate Cover"** node (Workflow 3)
   - Authentication → Select "OpenAI Account"

2. Click **"Generate Chapter"** node (Workflow 2 only)
   - Authentication → Select "OpenAI Account"

3. Click **"Commit to GitHub"** node
   - Credential → Select "GitHub Account"

---

## Step 5: Test Run

### Test Workflow 2 (Content):
1. Edit the "Set Config" node with your GitHub username
2. Set niche: "Test Book Topic"
3. Click **Execute Workflow**
4. Wait 10-15 minutes
5. Check your GitHub repo → `books/` folder
6. You should see: `{timestamp}_Test_Book_Topic_manuscript.txt`

### Test Workflow 3 (Cover):
1. Edit the "Set Config" node with your GitHub username
2. Set niche: "Test Book" and genre: "health"
3. Click **Execute Workflow**
4. Wait 2-3 minutes
5. Check your GitHub repo → `books/covers/` folder
6. You should see: `cover_{timestamp}_Test_Book.png`

---

## File Locations in GitHub

**Manuscripts**: `books/{timestamp}_{niche}_manuscript.txt`
**Covers**: `books/covers/cover_{timestamp}_{niche}.png`

---

## Commit Messages

The workflows auto-generate commit messages:

- **Content**: `Add book: {title} ({word_count} words)`
- **Cover**: `Add cover: {niche} ({genre})`

---

## Troubleshooting

### "Authentication failed"
- Check GitHub token has `repo` scope
- Regenerate token if expired

### "Owner not found"
- Verify `github_owner` matches your exact GitHub username (case-sensitive)

### "Repository not found"
- Verify `github_repo` matches your repo name
- Check repo is not private (or token has access to private repos)

### "File already exists"
- GitHub node can't overwrite files
- Either:
  1. Use unique filenames (timestamp ensures this)
  2. Manually delete old file from repo first

---

## Cost per Run

- **Workflow 2**: $1.26-$1.50 per book
- **Workflow 3**: $0.08 per cover
- **Total**: ~$1.42 per complete book

---

## GitHub Repo Size Management

### Current Setup
- Manuscripts: ~50-100 KB each (text files, small)
- Covers: ~2-5 MB each (PNG images, larger)

### At 100 Books
- Manuscripts: ~5-10 MB total
- Covers: ~200-500 MB total
- **Total repo size**: ~500 MB (still manageable)

### At 500 Books
- Covers alone: ~2.5 GB
- Consider using **Git LFS** (Large File Storage)

### Enable Git LFS (if needed)
```bash
cd C:/Users/user/Desktop/KDP
git lfs install
git lfs track "books/covers/*.png"
git add .gitattributes
git commit -m "Enable Git LFS for cover images"
git push
```

---

## Benefits of GitHub Integration

✅ **Version control** - Track all changes
✅ **Cloud backup** - Safe in GitHub
✅ **Collaboration** - Share with VA/team
✅ **No extra services** - No Google Drive needed
✅ **Simple setup** - Just 2 credentials (OpenAI + GitHub)
✅ **Automatic commits** - No manual git commands

---

## Production Workflow

### Weekly Publishing Routine:

**Monday**: Generate 2-3 books (Workflow 2)
```
1. Set niche: "Keto Meal Prep"
2. Execute Workflow 2
3. Wait 15 min
4. Repeat for each book
```

**Tuesday**: Generate covers (Workflow 3)
```
1. Set niche: "Keto Meal Prep", genre: "cookbook"
2. Execute Workflow 3
3. Wait 3 min
4. Repeat for each book
```

**Wednesday**: Pull from GitHub
```bash
cd C:/Users/user/Desktop/KDP
git pull
```

**Thursday**: Review & upload to KDP
```
1. Open books/ folder
2. Review manuscripts
3. Upload to KDP dashboard
4. ✅ CHECK AI DISCLOSURE BOX
5. Publish
```

**Friday**: Track commits
```bash
git log books/ --oneline
```

---

## Security Notes

⚠️ **Keep tokens secure**:
- Never commit GitHub tokens to repo
- Store credentials only in n8n
- Use environment variables if possible

⚠️ **API key safety**:
- Rotate OpenAI key monthly
- Monitor usage at platform.openai.com
- Set spending limits

---

## Next Steps

1. ✅ Import both GitHub workflows
2. ✅ Configure credentials
3. ✅ Update github_owner and github_repo
4. ✅ Test with sample book
5. ✅ Review commit in GitHub
6. 🚀 Start generating your book catalog!

---

**Ready to go!** Execute Workflow 2 to generate your first AI book committed to GitHub.
