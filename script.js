function renderShorts() {
    console.log("SHORTセクションの上書きを開始します...");
    fetch('news.json')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('news-container');
            if (!container) return;

            // 重要：HTMLに残っている古いゴミ（placeholder画像など）をここで一気に全消去！
            container.innerHTML = '';

            const items = data.news || [];
            items.forEach(item => {
                const imageUrl = item.img || item.thumbnail || item.thumbnail_url;
                const slide = document.createElement('div');
                slide.className = 'swiper-slide';
                slide.style.width = '150px';
                slide.innerHTML = `
                    <a href="${item.url}" target="_blank" style="text-decoration:none; color:white;">
                        <div style="position:relative; padding-top:177%; overflow:hidden; border-radius:12px; background:#222;">
                            <img src="${imageUrl}" style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover;">
                        </div>
                        <p style="font-size:11px; margin-top:8px; line-height:1.2; height:2.4em; overflow:hidden; text-align:center;">
                            ${item.title}
                        </p>
                    </a>
                `;
                container.appendChild(slide);
            });
            console.log("SHORTセクションの強制上書きが完了しました！ 件数:", items.length);
        })
        .catch(err => console.error("読み込みエラー:", err));
}

// ページが読み込まれたら即実行
window.addEventListener('load', renderShorts);
// 保険として3秒後にもう一度実行（遅延読み込み対策）
setTimeout(renderShorts, 3000);
