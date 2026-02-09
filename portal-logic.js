// ニュースを表示する関数
async function loadNews() {
    const newsGrid = document.querySelector('.news-grid');
    if (!newsGrid) return;

    try {
        const res = await fetch('news.json?t=' + Date.now());
        const data = await res.json();
        
        // 重要：'shorts' ではなく 'news' を使うように強制固定
        const articles = data.news || [];
        
        if (articles.length === 0) {
            newsGrid.innerHTML = '<p style="color:white;">ニュースを読み込み中...</p>';
            return;
        }

        newsGrid.innerHTML = articles.map(item => `
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
    } catch (e) {
        console.error("News Load Error:", e);
    }
}

// ショート動画を表示する関数
async function loadShorts() {
    const videoList = document.getElementById('video-list');
    if (!videoList) return;
    try {
        const res = await fetch('news.json?t=' + Date.now());
        const data = await res.json();
        const items = data.shorts || []; // こちらは shorts を使う
        videoList.innerHTML = items.map(item => `
            <a href="${item.url}" target="_blank" class="short-item">
                <div class="short-thumb">
                    <img src="https://img.youtube.com/vi/${item.id}/mqdefault.jpg">
                </div>
                <p class="short-title">${item.title}</p>
            </a>
        `).join('');
    } catch (e) { console.error("Shorts Error:", e); }
}

window.addEventListener('load', () => {
    loadNews();
    loadShorts();
    // ヒーロー画像等の他の初期化処理があればここに追加
    if (typeof initHeroSlideshow === 'function') initHeroSlideshow();
});
