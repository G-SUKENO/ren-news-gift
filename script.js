async function loadNews() {
    try {
        const response = await fetch('news.json');
        const data = await response.json();
        const newsContainer = document.getElementById('news-container');
        if (!newsContainer) return;

        newsContainer.innerHTML = '';
        // 'news'キーに入っているショート動画データをループで回す
        data.news.forEach(item => {
            const slide = document.createElement('div');
            slide.className = 'swiper-slide';
            slide.innerHTML = `
                <a href="${item.url}" target="_blank" class="news-card">
                    <div class="news-image">
                        <img src="${item.img || item.thumbnail}" alt="Shorts" style="width:100%; border-radius:8px;">
                    </div>
                    <div class="news-info">
                        <p class="news-title" style="font-size:0.8rem; margin-top:5px;">${item.title}</p>
                    </div>
                </a>
            `;
            newsContainer.appendChild(slide);
        });
    } catch (error) {
        console.error('Error loading shorts:', error);
    }
}
document.addEventListener('DOMContentLoaded', loadNews);
