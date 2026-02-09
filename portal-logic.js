// 1. ニュース読み込み (undefinedとショート動画の混線を修正済み)
async function loadNews() {
    const newsGrid = document.querySelector('.news-grid');
    if (!newsGrid) return;
    try {
        const res = await fetch('news.json?t=' + Date.now());
        const data = await res.json();
        const articles = data.news || [];
        
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
    } catch (e) { console.error("News Load Error:", e); }
}

// 2. YouTubeショート動画の復活
async function loadShorts() {
    const videoList = document.getElementById('video-list');
    if (!videoList) return;
    try {
        const res = await fetch('news.json?t=' + Date.now());
        const data = await res.json();
        const items = data.shorts || [];
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

// 3. ヒーロー画像スライドショーの復活
async function initHeroSlideshow() {
    const heroImage = document.getElementById('hero-image');
    if (!heroImage) return;
    try {
        const res = await fetch('image_list.json?t=' + Date.now());
        const images = await res.json();
        if (images.length === 0) return;

        let currentIndex = 0;
        const updateHero = () => {
            const nextIndex = Math.floor(Math.random() * images.length);
            heroImage.style.opacity = 0;
            setTimeout(() => {
                heroImage.src = images[nextIndex];
                heroImage.style.opacity = 1;
            }, 1000);
        };
        setInterval(updateHero, 5000);
        updateHero(); // 初回表示
    } catch (e) { console.error("Hero Error:", e); }
}

// 全てをページ読み込み時に実行
window.addEventListener('load', () => {
    loadNews();
    loadShorts();
    initHeroSlideshow();
});
