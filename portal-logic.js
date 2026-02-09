// 共通のデータ取得関数
async function fetchData(url) {
    const res = await fetch(url + '?t=' + Date.now());
    return await res.json();
}

// 1. ヒーロー画像 (image_list.json)
async function initHero() {
    const heroImg = document.getElementById('hero-image');
    if (!heroImg) return;
    try {
        const images = await fetchData('image_list.json');
        const updateHero = () => {
            const img = images[Math.floor(Math.random() * images.length)];
            heroImg.style.opacity = 0;
            setTimeout(() => {
                heroImg.src = img;
                heroImg.style.opacity = 1;
            }, 1000);
        };
        setInterval(updateHero, 5000);
        updateHero();
    } catch (e) { console.error("Hero Error:", e); }
}

// 2. ニュース (news.json の news セクション)
async function initNews() {
    const grid = document.querySelector('.news-grid');
    if (!grid) return;
    try {
        const data = await fetchData('news.json');
        const articles = data.news || [];
        grid.innerHTML = articles.map(item => `
            <a href="${item.url}" target="_blank" class="news-item">
                <div class="news-thumb">
                    <img src="${item.image}" alt="">
                    <span class="site-tag">${item.site_name || 'News'}</span>
                </div>
                <div class="news-content">
                    <p class="news-date">${item.date || ''}</p>
                    <h3 class="news-title">${item.title}</h3>
                </div>
            </a>
        `).join('');
    } catch (e) { console.error("News Error:", e); }
}

// 3. YouTube動画 (news.json の shorts セクション)
async function initVideos() {
    const list = document.getElementById('video-list');
    if (!list) return;
    try {
        const data = await fetchData('news.json');
        const items = data.shorts || [];
        list.innerHTML = items.map(item => `
            <a href="${item.url}" target="_blank" class="short-item">
                <div class="short-thumb">
                    <img src="https://img.youtube.com/vi/${item.id}/mqdefault.jpg">
                </div>
                <p class="short-title">${item.title}</p>
            </a>
        `).join('');
    } catch (e) { console.error("Video Error:", e); }
}

// ページ読み込み時にすべて起動
document.addEventListener('DOMContentLoaded', () => {
    initHero();
    initNews();
    initVideos();
});
