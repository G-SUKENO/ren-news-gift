document.addEventListener('DOMContentLoaded', () => {
    const contentWrap = document.querySelector('.content-wrap');
    const footer = document.querySelector('footer');
    if (!contentWrap || !footer) return;

    const newsTitle = document.createElement('div');
    newsTitle.className = 'section-label';
    newsTitle.innerText = 'Latest News';

    const newsContainer = document.createElement('div');
    newsContainer.id = 'news-section';
    
    const injectStyles = () => {
        const isPC = window.innerWidth >= 1024;
        newsContainer.style.display = 'grid';
        newsContainer.style.gap = '15px';
        newsContainer.style.padding = '0 15px 40px';
        newsContainer.style.width = '100%';
        newsContainer.style.maxWidth = '1200px';
        newsContainer.style.marginLeft = 'auto';
        newsContainer.style.marginRight = 'auto';
        newsContainer.style.boxSizing = 'border-box';
        newsContainer.style.gridTemplateColumns = isPC ? 'repeat(3, 1fr)' : '1fr';
    };

    window.addEventListener('resize', injectStyles);
    injectStyles();

    contentWrap.insertBefore(newsTitle, footer);
    contentWrap.insertBefore(newsContainer, footer);

    fetch('news.json?t=' + Date.now())
        .then(res => res.json())
        .then(data => {
            const articles = data.news || [];
            if (articles.length > 0) {
                newsContainer.innerHTML = articles.map(n => {
                    let cleanTitle = n.title.replace(/^\d{4}\.\d{2}\.\d{2}\s*/, '').replace(/^\[\d{4}\.\d{2}\.\d{2}\]\s*/, '');
                    
                    return `
                    <a href="${n.url}" target="_blank" style="display: flex; background: #111; border-radius: 10px; overflow: hidden; text-decoration: none; border: 1px solid #222; height: 100px; width: 100%; box-sizing: border-box; transition: transform 0.2s;">
                        <div style="width: 100px; min-width: 100px; height: 100px; background: #222;">
                            <img src="${n.image}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='images/photo_9.jpg'">
                        </div>
                        <div style="padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; text-align: left;">
                            <div style="font-size: 0.85rem; color: #fff; line-height: 1.4; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                ${cleanTitle}
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 0.65rem; color: #777; font-family: monospace; white-space: nowrap;">${n.date}</span>
                                <span style="font-size: 0.6rem; color: #d4af37; font-weight: bold; white-space: nowrap; border-left: 1px solid #333; padding-left: 10px;">${n.site_name}</span>
                            </div>
                        </div>
                    </a>`;
                }).join('');
            }
        })
        .catch(err => console.error("News Load Error:", err));
});
