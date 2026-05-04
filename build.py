#!/usr/bin/env python3
"""a.csv, b.csv, c.csv, d.csv를 읽어서 index.html 노래책 앱을 생성합니다."""

import csv
import json
import os

def parse_csv_file(filepath):
    songs = []
    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return songs

    start = 1 if rows[0][0].strip() == '구분' else 0

    for row in rows[start:]:
        if len(row) < 4:
            continue
        genre = row[0].strip().replace('﻿', '')
        title = row[1].strip()
        if not genre or not title:
            continue

        # b.csv: lyrics at col[3], col[4] is empty
        # a/c/d.csv: chord at col[3], lyrics at col[4]
        if len(row) >= 5 and row[4].strip():
            chord = row[3].strip()
            lyrics = row[4].strip()
        else:
            chord = ''
            lyrics = row[3].strip()

        if lyrics:
            songs.append({'genre': genre, 'title': title, 'chord': chord, 'lyrics': lyrics})

    return songs


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>kusa 7080 노래</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --bg: #f1f5f9;
  --white: #ffffff;
  --text: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --chord-bg: #fef3c7;
  --chord-text: #92400e;
  --genre-bg: #ede9fe;
  --genre-text: #5b21b6;
}

html, body { height: 100%; overflow: hidden; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', '맑은 고딕', sans-serif;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}

.view {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.view.hidden { display: none; }

/* ── 목록 화면 ── */

.list-header {
  background: var(--primary);
  padding: 14px 16px 12px;
  flex-shrink: 0;
}

.app-title {
  color: white;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 10px;
  letter-spacing: -0.3px;
}

.search-wrap { position: relative; }

.search-icon {
  position: absolute;
  left: 12px; top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  opacity: 0.7;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 16px 0 38px;
  border-radius: 20px;
  border: none;
  background: rgba(255,255,255,0.2);
  color: white;
  font-size: 15px;
  outline: none;
  -webkit-appearance: none;
}
.search-input::placeholder { color: rgba(255,255,255,0.65); }
.search-input::-webkit-search-cancel-button { filter: invert(1) opacity(0.6); }

.genre-scroll {
  background: var(--white);
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  white-space: nowrap;
  padding: 8px 12px;
  flex-shrink: 0;
}
.genre-scroll::-webkit-scrollbar { display: none; }

.genre-btn {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 14px;
  border-radius: 16px;
  border: 1.5px solid var(--border);
  background: white;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-right: 6px;
  -webkit-tap-highlight-color: transparent;
  white-space: nowrap;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.genre-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.song-count {
  padding: 8px 16px 4px;
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
  background: var(--bg);
}

.song-list-wrap {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: var(--bg);
}

.song-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  gap: 10px;
  -webkit-tap-highlight-color: transparent;
}
.song-item:active { background: #f8fafc; }

.song-title {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.3;
}

.song-badges {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
}

.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
}
.badge-genre { background: var(--genre-bg); color: var(--genre-text); }
.badge-chord {
  background: var(--chord-bg);
  color: var(--chord-text);
  max-width: 72px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-arrow { color: #cbd5e1; font-size: 18px; }

.no-results {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 15px;
}

/* ── 가사 화면 ── */
#lyricsView { background: var(--white); }

.lyrics-nav {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--primary);
  font-size: 15px;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 0;
  -webkit-tap-highlight-color: transparent;
}

.lyrics-title-section {
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.lyrics-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
  margin-bottom: 8px;
}

.lyrics-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.lyrics-chord-full {
  font-size: 13px;
  background: var(--chord-bg);
  color: var(--chord-text);
  padding: 4px 10px;
  border-radius: 8px;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.lyrics-body {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 20px 16px 16px;
}

.lyrics-text {
  font-size: 16px;
  line-height: 1.9;
  white-space: pre-wrap;
  color: var(--text);
  word-break: keep-all;
}

.lyrics-footer {
  flex-shrink: 0;
  padding: 12px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom, 12px));
  border-top: 1px solid var(--border);
  background: var(--white);
}

.footer-btns {
  display: flex;
  gap: 10px;
}

.back-to-list-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 50px;
  flex: 1;
  background: var(--bg);
  color: var(--text);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.back-to-list-btn:active { background: var(--border); }

.sheet-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 50px;
  flex: 2;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.sheet-btn:active { background: var(--primary-dark); }
</style>
</head>
<body>

<!-- 목록 화면 -->
<div id="listView" class="view">
  <div class="list-header">
    <div class="app-title">🎵 kusa 7080 노래</div>
    <div class="search-wrap">
      <svg class="search-icon" width="16" height="16" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input
        class="search-input" id="searchInput" type="search"
        placeholder="노래 제목 검색..."
        autocomplete="off" autocorrect="off" spellcheck="false"
      >
    </div>
  </div>

  <div class="genre-scroll" id="genreScrollEl"></div>
  <div class="song-count" id="songCountEl"></div>
  <div class="song-list-wrap">
    <div id="songListEl"></div>
  </div>
</div>

<!-- 가사 화면 -->
<div id="lyricsView" class="view hidden">
  <div class="lyrics-nav">
    <button class="back-btn" onclick="showList()">
      <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path d="M15 18l-6-6 6-6"/>
      </svg>
      목록
    </button>
  </div>
  <div class="lyrics-title-section">
    <div class="lyrics-title" id="lyricsTitleEl"></div>
    <div class="lyrics-meta-row">
      <span class="badge badge-genre" id="lyricsGenreEl"></span>
      <span class="lyrics-chord-full" id="lyricsChordEl" style="display:none"></span>
    </div>
  </div>
  <div class="lyrics-body" id="lyricsBodyEl">
    <div class="lyrics-text" id="lyricsTextEl"></div>
  </div>
  <div class="lyrics-footer">
    <div class="footer-btns">
      <button class="back-to-list-btn" onclick="showList()">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
        목록
      </button>
      <button class="sheet-btn" id="sheetBtnEl">
        <svg width="18" height="18" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        악보 검색
      </button>
    </div>
  </div>
</div>

<script>
const SONGS = /* SONGS_DATA */;

let activeGenre = '전체';
let searchQuery = '';

const genres = ['전체', ...[...new Set(SONGS.map(s => s.genre))].sort()];

function renderGenreTabs() {
  document.getElementById('genreScrollEl').innerHTML = genres.map(g =>
    `<button class="genre-btn ${g === activeGenre ? 'active' : ''}" data-genre="${g}">${g}</button>`
  ).join('');
}

document.getElementById('genreScrollEl').addEventListener('click', e => {
  const btn = e.target.closest('.genre-btn');
  if (!btn) return;
  activeGenre = btn.dataset.genre;
  renderGenreTabs();
  renderList();
});

document.getElementById('searchInput').addEventListener('input', e => {
  searchQuery = e.target.value.trim();
  renderList();
});

function filteredSongs() {
  return SONGS.filter(s =>
    (activeGenre === '전체' || s.genre === activeGenre) &&
    (!searchQuery || s.title.includes(searchQuery))
  );
}

function renderList() {
  const songs = filteredSongs();
  document.getElementById('songCountEl').textContent = `총 ${songs.length}곡`;

  if (!songs.length) {
    document.getElementById('songListEl').innerHTML = '<div class="no-results">검색 결과가 없습니다</div>';
    return;
  }

  document.getElementById('songListEl').innerHTML = songs.map(s => {
    const idx = SONGS.indexOf(s);
    return `<div class="song-item" data-idx="${idx}">
      <div class="song-title">${esc(s.title)}</div>
      <div class="song-badges">
        <span class="badge badge-genre">${esc(s.genre)}</span>
        ${s.chord ? `<span class="badge badge-chord">${esc(s.chord)}</span>` : ''}
      </div>
      <span class="item-arrow">›</span>
    </div>`;
  }).join('');
}

document.getElementById('songListEl').addEventListener('click', e => {
  const item = e.target.closest('.song-item');
  if (!item) return;
  showLyrics(+item.dataset.idx);
});

function showLyrics(idx) {
  const s = SONGS[idx];
  document.getElementById('lyricsTitleEl').textContent = s.title;
  document.getElementById('lyricsGenreEl').textContent = s.genre;

  const chordEl = document.getElementById('lyricsChordEl');
  if (s.chord) { chordEl.textContent = s.chord; chordEl.style.display = ''; }
  else { chordEl.style.display = 'none'; }

  document.getElementById('lyricsTextEl').textContent = s.lyrics;
  document.getElementById('lyricsBodyEl').scrollTop = 0;

  document.getElementById('sheetBtnEl').onclick = () =>
    window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(s.title + ' 악보');

  document.getElementById('listView').classList.add('hidden');
  document.getElementById('lyricsView').classList.remove('hidden');
}

function showList() {
  document.getElementById('lyricsView').classList.add('hidden');
  document.getElementById('listView').classList.remove('hidden');
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

renderGenreTabs();
renderList();
</script>
</body>
</html>'''


def build():
    base = os.path.dirname(os.path.abspath(__file__))
    all_songs = []
    for name in ['a.csv', 'b.csv', 'c.csv', 'd.csv']:
        path = os.path.join(base, name)
        if os.path.exists(path):
            songs = parse_csv_file(path)
            print(f'{name}: {len(songs)}곡')
            all_songs.extend(songs)

    genres = sorted(set(s['genre'] for s in all_songs))
    print(f'총 {len(all_songs)}곡 | 장르: {", ".join(genres)}')

    songs_json = json.dumps(all_songs, ensure_ascii=False)
    html = HTML_TEMPLATE.replace('/* SONGS_DATA */', songs_json)

    out = os.path.join(base, 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'생성 완료: {out}')


if __name__ == '__main__':
    build()
