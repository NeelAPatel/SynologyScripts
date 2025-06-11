# Synology Metadata Fixer
A targeted tool to restore timestamps, GPS, and EXIF data from Google Takeout media - built to enable clean imports into Synology Photos.

---

## 📸 Problem

Google Takeout exports your media files (`.jpg`, `.mp4`, `.png`, etc.) alongside messy and mismatched `.json` metadata files. These often contain critical EXIF info like original timestamps, GPS coordinates, and resolution - but:

- Filenames don’t match due to Google’s weird copy-naming (`(1)`, etc.)
- EXIF tags are stripped or inconsistent
- Synology Photos fails to display proper dates or organize albums correctly

---

## 🛠️ Solution

`Synology Metadata Fixer` is a one-off utility script designed to:

- 🕒 Restore **original timestamps** from Takeout `.json` files
- 🌍 Inject **GPS coordinates** (if available)
- 🖼️ Patch **resolution and EXIF fields** when missing
- 🔄 Match renamed `.json` files with their correct media counterparts
- 🧼 Clean and prep files for seamless import into Synology Photos

---

## ✅ Supported Media Formats

- `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.dng`
- `.mp4`, `.mov`


