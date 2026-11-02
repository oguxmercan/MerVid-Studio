// MerVid Studio Frontend Logic

let currentMediaInfo = null;
let downloadDestination = "";
let activePollInterval = null;

// DOM Elements
const urlInput = document.getElementById('urlInput');
const pasteBtn = document.getElementById('pasteBtn');
const extractSpinner = document.getElementById('extractSpinner');
const mediaCard = document.getElementById('mediaCard');
const playlistPanel = document.getElementById('playlistPanel');
const qualitySelect = document.getElementById('qualitySelect');
const formatSelect = document.getElementById('formatSelect');
const activeDlBadge = document.getElementById('activeDlBadge');
const activeDlCount = document.getElementById('activeDlCount');
const downloadsContainer = document.getElementById('downloadsContainer');
const historyList = document.getElementById('historyList');
const historySearch = document.getElementById('historySearch');
const historyCount = document.getElementById('historyCount');
const toastEl = document.getElementById('toast');

// Initialize
window.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupEventListeners();
  waitForPywebviewApi();
});

function showToast(msg, duration = 3000) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => {
    toastEl.classList.remove('show');
  }, duration);
}

function waitForPywebviewApi() {
  if (window.pywebview && window.pywebview.api) {
    onApiReady();
  } else {
    window.addEventListener('pywebviewready', onApiReady);
  }
}

async function onApiReady() {
  try {
    const settings = await window.pywebview.api.get_settings();
    if (settings) {
      downloadDestination = settings.save_path;
      const el = document.getElementById('currentDownloadPathText');
      if (el) el.textContent = downloadDestination;
    }
    refreshCookieStatus();
    refreshRdStatus();
    refreshHistory();
    startDownloadPolling();
  } catch (e) {
    console.error("API Error:", e);
  }
}

// Dock Tabs
function setupTabs() {
  const dockItems = document.querySelectorAll('.dock-item');
  dockItems.forEach(item => {
    item.addEventListener('click', () => {
      const target = item.dataset.tab;
      dockItems.forEach(d => d.classList.remove('active'));
      item.classList.add('active');

      document.querySelectorAll('.tab-content').forEach(section => {
        section.classList.remove('active');
      });
      const targetSec = document.getElementById(`tab-${target}`);
      if (targetSec) targetSec.classList.add('active');

      if (target === 'gecmis') refreshHistory();
      if (target === 'ayarlar') {
        refreshCookieStatus();
        refreshRdStatus();
      }
    });
  });
}

function setupEventListeners() {
  // Paste Button
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text && text.trim()) {
        urlInput.value = text.trim();
        inspectUrl();
      } else {
        urlInput.focus();
        document.execCommand('paste');
        if (urlInput.value.trim()) inspectUrl();
      }
    } catch (err) {
      urlInput.focus();
      document.execCommand('paste');
      if (urlInput.value.trim()) inspectUrl();
    }
  });

  // Analyze / Enter Button
  const analyzeBtn = document.getElementById('analyzeBtn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', inspectUrl);
  }

  // URL Enter Key
  urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      inspectUrl();
    }
  });

  // Format selection change
  formatSelect.addEventListener('change', () => {
    updateQualityOptions();
  });

  // Start Single Download Button
  document.getElementById('startDownloadBtn').addEventListener('click', startSingleDownload);

  // Quick Banner Download Button
  document.getElementById('downloadBannerBtn').addEventListener('click', async () => {
    if (!currentMediaInfo) return;
    const bannerUrl = currentMediaInfo.banner_url || currentMediaInfo.thumbnail;
    if (!bannerUrl) {
      showToast("Kapak görseli bulunamadı");
      return;
    }
    showToast("Banner indiriliyor...");
    try {
      const res = await window.pywebview.api.download_banner(bannerUrl, currentMediaInfo.title, downloadDestination);
      if (res && res.success) {
        showToast("Banner kaydedildi: " + res.filename);
      } else {
        showToast("Banner kaydedilemedi: " + (res.error || ""));
      }
    } catch (e) {
      showToast("Hata: " + e.message);
    }
  });

  // Playlist Batch Download Button
  document.getElementById('downloadPlaylistBtn').addEventListener('click', startPlaylistBatchDownload);

  // Settings: Change download folder
  document.getElementById('browseDownloadDirBtn').addEventListener('click', async () => {
    try {
      const newPath = await window.pywebview.api.select_folder();
      if (newPath) {
        downloadDestination = newPath;
        document.getElementById('currentDownloadPathText').textContent = newPath;
        await window.pywebview.api.save_settings({ save_path: newPath });
        showToast("İndirme klasörü güncellendi");
      }
    } catch (e) {
      console.error(e);
    }
  });

  // Cookie Vault Buttons (Inside Ayarlar)
  document.getElementById('selectCookieFileBtn').addEventListener('click', async () => {
    try {
      const res = await window.pywebview.api.select_cookie_file();
      if (res && res.success) {
        showToast("cookies.txt başarıyla yüklendi!");
        refreshCookieStatus();
      } else if (res && res.error) {
        showToast("Hata: " + res.error);
      }
    } catch (e) {
      showToast("Dosya seçme hatası");
    }
  });

  document.getElementById('saveCookieTextBtn').addEventListener('click', async () => {
    const text = document.getElementById('cookieTextInput').value.trim();
    if (!text) {
      showToast("Lütfen önce çerez metnini yapıştırın");
      return;
    }
    try {
      const res = await window.pywebview.api.save_cookie_text(text);
      if (res && res.success) {
        showToast("Çerezler kaydedildi!");
        document.getElementById('cookieTextInput').value = '';
        refreshCookieStatus();
      } else {
        showToast("Kayıt hatası: " + (res.error || ""));
      }
    } catch (e) {
      showToast("Çerez kaydedilemedi");
    }
  });

  document.getElementById('clearCookiesBtn').addEventListener('click', async () => {
    try {
      await window.pywebview.api.clear_cookie();
      showToast("Çerezler temizlendi");
      refreshCookieStatus();
    } catch (e) {
      showToast("Hata");
    }
  });

  // Real-Debrid Integration
  const saveRdBtn = document.getElementById('saveRdTokenBtn');
  if (saveRdBtn) {
    saveRdBtn.addEventListener('click', async () => {
      const tokenInput = document.getElementById('rdTokenInput');
      const token = tokenInput ? tokenInput.value.trim() : '';
      if (!token) {
        showToast("Lütfen bir Real-Debrid API Token girin.");
        return;
      }
      showToast("Real-Debrid doğrulanıyor...");
      try {
        const res = await window.pywebview.api.save_rd_token(token);
        if (res && res.success) {
          showToast(`Real-Debrid Bağlandı! (${res.username})`);
          if (tokenInput) tokenInput.value = '';
          refreshRdStatus();
        } else {
          showToast("Bağlantı Başarısız: " + (res.error || "Geçersiz Token"));
          refreshRdStatus();
        }
      } catch (err) {
        showToast("Hata: " + err.message);
      }
    });
  }

  const removeRdBtn = document.getElementById('removeRdTokenBtn');
  if (removeRdBtn) {
    removeRdBtn.addEventListener('click', async () => {
      try {
        await window.pywebview.api.remove_rd_token();
        showToast("Real-Debrid bağlantısı kaldırıldı.");
        refreshRdStatus();
      } catch (err) {
        showToast("Hata");
      }
    });
  }

  // History Controls
  document.getElementById('clearHistoryBtn').addEventListener('click', async () => {
    if (confirm("İndirme geçmişini temizlemek istediğinizden emin misiniz?")) {
      await window.pywebview.api.clear_history();
      refreshHistory();
      showToast("Geçmiş temizlendi");
    }
  });

  historySearch.addEventListener('input', () => {
    filterHistory(historySearch.value);
  });
}

// URL Inspecting
async function inspectUrl() {
  const url = urlInput.value.trim();
  if (!url) {
    showToast("Lütfen geçerli bir video linki yapıştırın");
    return;
  }

  extractSpinner.style.display = "inline-block";
  mediaCard.style.display = "none";
  playlistPanel.style.display = "none";

  try {
    const res = await window.pywebview.api.inspect_url(url);
    if (!res || !res.success) {
      showToast("Medya çözümlenemedi: " + (res.error || ""));
      return;
    }

    currentMediaInfo = res;

    if (res.is_playlist) {
      renderPlaylistView(res);
    } else {
      renderSingleMediaView(res);
    }
  } catch (err) {
    showToast("Hata: " + err.message);
  } finally {
    extractSpinner.style.display = "none";
  }
}

// Render Single Video Card
function renderSingleMediaView(info) {
  document.getElementById('mediaThumbnail').src = info.thumbnail || "mervid-studio.png";
  document.getElementById('mediaTitle').textContent = info.title;
  document.getElementById('mediaDuration').textContent = info.duration_string || "00:00";

  if (info.is_debrid) {
    const ext = info.title && info.title.includes('.') ? info.title.split('.').pop().toUpperCase() : 'FILE';
    formatSelect.innerHTML = `<option value="${ext.toLowerCase()}" selected>Orijinal (${ext})</option>`;
  } else {
    formatSelect.innerHTML = `
      <option value="mp4" selected>MP4 (Video)</option>
      <option value="mkv">MKV (Video)</option>
      <option value="mp3">MP3 (320k Ses)</option>
      <option value="flac">FLAC (Kayıpsız Ses)</option>
      <option value="wav">WAV (Ham Ses)</option>
    `;
  }

  updateQualityOptions();

  mediaCard.style.display = "block";
  mediaCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Update Quality Dropdown based on Format
function updateQualityOptions() {
  const fmt = formatSelect.value;
  const isAudio = (fmt === 'mp3' || fmt === 'flac' || fmt === 'wav');

  qualitySelect.innerHTML = "";

  if (isAudio) {
    qualitySelect.innerHTML = `
      <option value="320">Kayıpsız / Max Bitrate (320k)</option>
      <option value="256">256 kbps (Yüksek Kalite)</option>
      <option value="192">192 kbps (Standart)</option>
      <option value="128">128 kbps (Kompakt)</option>
    `;
  } else {
    if (currentMediaInfo && currentMediaInfo.resolutions && currentMediaInfo.resolutions.length > 0) {
      currentMediaInfo.resolutions.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.height > 0 ? r.height : "best";
        opt.textContent = r.label || r.tier_name;
        qualitySelect.appendChild(opt);
      });
    } else {
      qualitySelect.innerHTML = `
        <option value="best" selected>YouTube 4K / En Yüksek</option>
        <option value="2160">4K Ultra HD (2160p)</option>
        <option value="1440">2K Quad HD (1440p)</option>
        <option value="1080">1080p Full HD</option>
        <option value="720">720p HD</option>
        <option value="480">480p SD</option>
      `;
    }
  }
}

// Render Playlist View
function renderPlaylistView(playlist) {
  document.getElementById('playlistTitle').textContent = playlist.title || "Oynatma Listesi";
  document.getElementById('playlistCount').textContent = `${playlist.total_items} video bulundu`;

  const container = document.getElementById('playlistItemsList');
  container.innerHTML = "";

  (playlist.items || []).forEach(item => {
    const row = document.createElement('div');
    row.className = "playlist-row";
    row.innerHTML = `
      <input type="checkbox" class="pl-item-check" data-url="${item.url}" data-title="${encodeURIComponent(item.title)}" data-thumb="${item.thumbnail || ''}" checked>
      <span style="color:var(--text-muted); font-size:11px; width:24px;">#${item.index}</span>
      <span style="flex:1; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${item.title}</span>
      <span style="font-family:var(--mono); font-size:11px; color:var(--text-muted);">${item.duration_string}</span>
    `;
    container.appendChild(row);
  });

  playlistPanel.style.display = "block";
  playlistPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function toggleSelectAllPlaylist(selectAll) {
  document.querySelectorAll('.pl-item-check').forEach(cb => {
    cb.checked = selectAll;
  });
}

// Start Single Download
async function startSingleDownload() {
  if (!currentMediaInfo) return;

  const fmt = formatSelect.value;
  const isAudio = (fmt === 'mp3' || fmt === 'flac' || fmt === 'wav');
  const isDebrid = currentMediaInfo.is_debrid || false;
  const originalExt = currentMediaInfo.title && currentMediaInfo.title.includes('.')
    ? currentMediaInfo.title.split('.').pop().toUpperCase()
    : 'FILE';

  const threadsVal = document.getElementById('threadsSelect') ? document.getElementById('threadsSelect').value : "8";

  const payload = {
    url: currentMediaInfo.url,
    title: currentMediaInfo.title,
    thumbnail: currentMediaInfo.thumbnail,
    mode: isDebrid ? 'DEBRID' : (isAudio ? 'audio' : 'video'),
    resolution: qualitySelect.value,
    format: isDebrid ? originalExt : fmt,
    audio_quality: qualitySelect.value,
    save_banner: document.getElementById('saveBannerCheck') ? document.getElementById('saveBannerCheck').checked : true,
    sponsorblock: document.getElementById('sponsorBlockCheck') ? document.getElementById('sponsorBlockCheck').checked : true,
    embed_subtitles: document.getElementById('embedSubtitlesCheck') ? document.getElementById('embedSubtitlesCheck').checked : false,
    threads: threadsVal,
    save_path: downloadDestination,
    use_cookies: true,
    download_url: currentMediaInfo.download_url || null,
    is_debrid: currentMediaInfo.is_debrid || false,
    filename: currentMediaInfo.filename || null,
    filesize: currentMediaInfo.filesize || 0
  };

  try {
    const res = await window.pywebview.api.start_download(payload);
    if (res && res.success) {
      showToast("İndirme başladı! İndirilenler sekmesine geçildi.");
      // Switch to İndirilenler dock tab
      document.querySelector('[data-tab="indirilenler"]').click();
    } else {
      showToast("İndirme başlatılamadı: " + (res.error || ""));
    }
  } catch (err) {
    showToast("Hata: " + err.message);
  }
}

// Start Playlist Batch Download
async function startPlaylistBatchDownload() {
  const checkboxes = document.querySelectorAll('.pl-item-check:checked');
  if (checkboxes.length === 0) {
    showToast("Lütfen indirilecek en az bir video seçin.");
    return;
  }

  const fmt = formatSelect.value;
  const isAudio = (fmt === 'mp3' || fmt === 'flac' || fmt === 'wav');
  const threadsVal = document.getElementById('threadsSelect') ? document.getElementById('threadsSelect').value : "8";
  const saveBanner = document.getElementById('playlistBannerCheck') ? document.getElementById('playlistBannerCheck').checked : true;

  let started = 0;
  for (const cb of checkboxes) {
    const itemUrl = cb.dataset.url;
    const itemTitle = decodeURIComponent(cb.dataset.title);
    const itemThumb = cb.dataset.thumb;

    const payload = {
      url: itemUrl,
      title: itemTitle,
      thumbnail: itemThumb,
      mode: isAudio ? 'audio' : 'video',
      resolution: qualitySelect.value,
      format: fmt,
      threads: threadsVal,
      sponsorblock: true,
      save_banner: saveBanner,
      save_path: downloadDestination,
      use_cookies: true
    };

    await window.pywebview.api.start_download(payload);
    started++;
  }

  showToast(`${started} video indirme sırasına eklendi!`);
  document.querySelector('[data-tab="indirilenler"]').click();
}

// Polling Active Downloads
function startDownloadPolling() {
  if (activePollInterval) clearInterval(activePollInterval);
  activePollInterval = setInterval(async () => {
    try {
      const downloads = await window.pywebview.api.get_active_downloads();
      renderActiveDownloads(downloads || []);
    } catch (e) {
      // ignore transient error
    }
  }, 750);
}

function renderActiveDownloads(downloads) {
  const activeCount = downloads.filter(d => d.status === 'downloading' || d.status === 'queued' || d.status === 'muxing').length;
  
  if (activeCount > 0) {
    activeDlBadge.style.display = 'inline-block';
    activeDlBadge.textContent = activeCount;
  } else {
    activeDlBadge.style.display = 'none';
  }

  activeDlCount.textContent = `${downloads.length} toplam işlem (${activeCount} aktif)`;

  if (downloads.length === 0) {
    downloadsContainer.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 50px 0;">
        Şu anda aktif indirme bulunmuyor. Link yapıştırarak indirme başlatabilirsiniz.
      </div>
    `;
    return;
  }

  downloadsContainer.innerHTML = "";
  downloads.forEach(d => {
    const card = document.createElement('div');
    card.className = "download-card";

    let statusBadge = `<span class="dl-badge status-dl">${d.status.toUpperCase()}</span>`;
    if (d.status === 'completed') {
      statusBadge = `<span class="dl-badge status-ok">TAMAMLANDI</span>`;
    } else if (d.status === 'error') {
      statusBadge = `<span class="dl-badge" style="color:#ff4d6d;border-color:red;">HATA</span>`;
    }

    card.innerHTML = `
      <div class="dl-header">
        <span class="dl-title" title="${d.title}">${d.title}</span>
        <div style="display:flex; gap:6px;">
          <span class="dl-badge">${d.mode.toUpperCase()} • ${d.format.toUpperCase()}</span>
          ${statusBadge}
        </div>
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" style="width: ${d.percent}%"></div>
      </div>
      <div class="dl-metrics">
        <span>%${d.percent} • ${d.downloaded} / ${d.total}</span>
        <span>Hız: ${d.speed}</span>
        <span>Kalan: ${d.eta}</span>
      </div>
      <div class="dl-actions">
        ${d.filepath ? `
          <button class="btn-sm" onclick="openFile('${encodeURIComponent(d.filepath)}')">Aç</button>
          <button class="btn-sm" onclick="openFolder('${encodeURIComponent(d.filepath)}')">Klasörde Göster</button>
        ` : ''}
        ${d.status === 'downloading' || d.status === 'queued' ? `
          <button class="btn-sm" style="color:#ff4d6d;" onclick="cancelDownload('${d.id}')">İptal</button>
        ` : ''}
      </div>
    `;
    downloadsContainer.appendChild(card);
  });
}

async function cancelDownload(id) {
  await window.pywebview.api.cancel_download(id);
  showToast("İndirme iptal edildi");
}

async function openFile(encodedPath) {
  const p = decodeURIComponent(encodedPath);
  await window.pywebview.api.open_file(p);
}

async function openFolder(encodedPath) {
  const p = decodeURIComponent(encodedPath);
  await window.pywebview.api.open_folder(p);
}

// History
async function refreshHistory() {
  try {
    const history = await window.pywebview.api.get_history();
    renderHistoryList(history || []);
  } catch (e) {
    console.error("History error:", e);
  }
}

function renderHistoryList(items) {
  historyCount.textContent = `${items.length} dosya`;
  if (items.length === 0) {
    historyList.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 40px 0;">Henüz indirme geçmişi yok.</div>`;
    return;
  }

  historyList.innerHTML = "";
  items.forEach(item => {
    const row = document.createElement('div');
    row.className = "history-item";
    row.innerHTML = `
      <div style="flex:1; min-width:0;">
        <div style="font-size:13px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${item.title}">${item.title}</div>
        <div style="font-size:11px; color:var(--text-muted); display:flex; gap:10px; margin-top:3px;">
          <span>${item.date_formatted || ''}</span>
          <span>•</span>
          <span>${item.format.toUpperCase()} (${item.resolution})</span>
          <span>•</span>
          <span>${item.filesize || ''}</span>
        </div>
      </div>
      <div style="display: flex; gap: 6px;">
        <button class="btn-sm" onclick="openFile('${encodeURIComponent(item.filepath)}')">Oynat</button>
        <button class="btn-sm" onclick="openFolder('${encodeURIComponent(item.filepath)}')">Göster</button>
      </div>
    `;
    historyList.appendChild(row);
  });
}

function filterHistory(query) {
  const q = query.toLowerCase().trim();
  const items = historyList.querySelectorAll('.history-item');
  items.forEach(el => {
    const title = el.textContent.toLowerCase();
    if (title.includes(q)) {
      el.style.display = 'flex';
    } else {
      el.style.display = 'none';
    }
  });
}

// Cookie Vault Status (Inside Ayarlar)
async function refreshCookieStatus() {
  try {
    const status = await window.pywebview.api.get_cookie_status();
    const statusText = document.getElementById('cookieStatusText');
    if (!statusText) return;
    if (status.has_cookie) {
      statusText.textContent = `Aktif • ${status.message} (${status.total_domains} domain)`;
      statusText.style.color = '#2CF09E';
    } else {
      statusText.textContent = `Pasif • Çerez yüklenmedi`;
      statusText.style.color = '#71717a';
    }
  } catch (e) {
    console.error("Cookie status error:", e);
  }
}

// Real-Debrid Status (Inside Ayarlar)
async function refreshRdStatus() {
  const statusText = document.getElementById('rdStatusText');
  if (!statusText) return;

  try {
    const res = await window.pywebview.api.get_rd_status();
    if (res && (res.valid || res.has_token || res.success)) {
      const isPrem = res.is_premium;
      const exp = res.expiration ? ` • Bitiş: ${res.expiration}` : '';
      statusText.textContent = `Aktif • ${res.username} (${isPrem ? 'PREMIUM' : 'STANDART'})${exp}`;
      statusText.style.color = '#2CF09E';
    } else {
      statusText.textContent = `Bağlı Değil • API Token Yok`;
      statusText.style.color = '#71717a';
    }
  } catch (e) {
    statusText.textContent = `Hata • Bağlantı kurulamadı`;
    statusText.style.color = '#ff4d6d';
  }
}

async function openExternalUrl(url) {
  try {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.open_url(url);
    } else {
      window.open(url, '_blank');
    }
  } catch (e) {
    console.error(e);
  }
}
