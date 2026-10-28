# CineFind — free movie listing website

This is a static movie discovery directory. It does **not** host, copy, or stream video files. Each card links out to the original publisher page.

## 1) Publish it for free with Netlify
1. Extract the ZIP file.
2. Sign in at https://app.netlify.com/
3. Choose **Add new site / Deploy manually** (wording may vary).
4. Drag the extracted project folder contents into the deploy area. Ensure `index.html`, `style.css`, `app.js`, and the `data` folder are at the published root.
5. Open the Netlify URL and test search/category filters.

## 2) Enable automatic daily listing refresh (GitHub Actions)
The included workflow attempts to read a public RSS feed first, then the publicly accessible homepage HTML. It only collects visible link text and links, and does not download video files or bypass logins, paywalls, anti-bot checks, or access controls. It may not work if the source blocks automated access or changes its layout. Check the site's terms and robots guidance and obtain permission where required.

1. Create a GitHub account and a new public repository.
2. Upload all project files, preserving folders.
3. In repository Settings → Pages, you can optionally publish from the `main` branch (root). Or keep Netlify as your host.
4. The workflow at `.github/workflows/daily-update.yml` runs daily and can also be run manually from Actions.
5. If the source does not provide a compatible feed or its pages are not parseable, the workflow logs a warning and keeps existing listings.

**Important:** If Netlify is used, GitHub Actions must publish the updated `data/movies.json` to the connected GitHub repository and Netlify must be connected to that repository for the deployed site to rebuild. A one-time drag-and-drop deployment alone will not receive daily file changes automatically.

## 3) Change the source URL
Open `scripts/update_movies.py` and set `SOURCE_URL` to the permitted public listing page. By default it uses `https://southfreak.club/`.

## 4) Manual listings
Edit `data/movies.json` and add items like:
```json
{
  "title": "Example title",
  "category": "Tamil",
  "year": "2026",
  "source_url": "https://example.com/original-movie-page",
  "published_at": "2026-10-28"
}
```
Use verified original page URLs only. Do not use guessed URL patterns.

## 5) Posters and monetization
This starter version uses designed placeholder posters so it does not copy artwork from other websites. Add only images you own or are licensed to use. Advertising approval and revenue are not guaranteed; follow the ad network's policies and the source site's terms.
