// King & Prince 公式チャンネルID
const CHANNEL_ID = 'UC_66ySqc_7R_p_u6_pAnKdg'; 

async function loadLatestVideos() {
    const videoGrid = document.querySelector('.video-grid');
    if (!videoGrid) return;

    try {
        // RSSフィード経由で最新動画を取得（APIキーなしで動く軽量な方法）
        const rssUrl = `https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}`;
        const proxyUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(rssUrl)}`;
        
        const res = await fetch(proxyUrl);
        const data = await res.json();
        
        if (data.items) {
            videoGrid.innerHTML = ''; // 一旦空にする
            
            // 最新4件を表示
            data.items.slice(0, 4).forEach(item => {
                const videoId = item.link.split('v=')[1];
                const card = document.createElement('div');
                card.className = 'video-card';
                card.innerHTML = `
                    <div class="video-wrapper">
                        <iframe src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>
                    </div>
                    <p class="video-caption">${item.title}</p>
                `;
                videoGrid.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Video Load Error:", e);
    }
}

async function initHero() {
    const heroImg = document.getElementById('hero-image');
    if (!heroImg) return;
    try {
        const res = await fetch('image_list.json?t=' + Date.now());
        const images = await res.json();
        if (images && images.length > 0) {
            heroImg.src = images[0];
            heroImg.style.opacity = 1;
        }
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
    initHero();
    loadLatestVideos();
});
