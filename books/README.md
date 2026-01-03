# Generated Books

This folder contains AI-generated content committed directly from n8n workflows.

## Structure

```
books/
├── {timestamp}_{niche}_manuscript.txt     # Book manuscripts
└── covers/
    └── cover_{timestamp}_{niche}.png      # Book covers
```

## Files

### Manuscripts
- Format: `.txt`
- Size: ~50-100 KB per book
- Word count: 15,000-20,000 words
- Structure: 12 chapters + intro + conclusion

### Covers
- Format: `.png`
- Size: 1024x1792 pixels (portrait)
- Quality: HD DALL-E 3 generated
- Size: ~2-5 MB per cover

## Workflow

These files are automatically committed by n8n workflows:
1. **Workflow 2** generates manuscript → commits to `books/`
2. **Workflow 3** generates cover → commits to `books/covers/`

## Usage

1. Pull latest from GitHub
2. Review content in `books/` folder
3. Edit/format as needed
4. Upload to KDP
5. ✅ **CHECK AI DISCLOSURE BOX** (mandatory!)

## Git LFS (Optional)

If repo size becomes large, consider using Git LFS for binary files:

```bash
git lfs track "books/covers/*.png"
git add .gitattributes
git commit -m "Configure Git LFS for covers"
```

## Cost per File

- Manuscript: $1.26-$1.50 (GPT-4 API)
- Cover: $0.08 (DALL-E 3 API)
- **Total**: ~$1.42/book

---

All files are tracked in git history. You can review past versions using `git log` and `git checkout`.
