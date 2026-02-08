async function initShorts() {
    try {
        const response = await fetch('news.json');
        const data = await response.json();
        const container = document.getElementById('news-container');
        if (!container) return;

        container.innerHTML = '';
        // data.news の中にあるアイテムを処理
        const items = data.news || [];
        
        items.forEach(item => {
            // img, thumbnail, thumbnail_url のどれがあっても動くようにする
            const imageUrl = item.img || item.thumbnail || item.thumbnail_url;
            if (!imageUrl) return;

            const slide = document.createElement('div');
            slide.className = 'swiper-slide';
            slide.style.width = '150px'; // ショート動画らしい縦長感
            slide.innerHTML = `
                <a href="${item.url}" target="_blank" style="text-decoration:none; color:white;">
                    <div style="position:relative; padding-top:177%; overflow:hidden; border-radius:12px; background:#333;">
                        <img src="${imageUrl}" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover;">
                    </div>
                    <p style="font-size:11px; margin-top:8px; line-height:1.2; height:2.4em; overflow:hidden;">${item.title}</p>
                </a>
            `;
            container.appendChild(slide);
        });
        console.log("SHORTセクションの描画に成功しました！表示件数:", items.length);
    } catch (e) {
        console.error("データの読み込みエラー:", e);
    }
}
window.addEventListener('load', initShorts);
