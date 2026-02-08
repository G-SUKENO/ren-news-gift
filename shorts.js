async function initShorts() {
    try {
        const res = await fetch('news.json');
        const data = await res.json();
        // news.json の中に 'shorts' か 'news' というキーでデータが入っていることを想定
        const items = data.shorts || data.news || [];
        const wrapper = document.getElementById('shorts-wrapper') || document.querySelector('.swiper-wrapper');
        
        if (!wrapper) return;
        wrapper.innerHTML = ''; 

        items.forEach(item => {
            const slide = document.createElement('div');
            slide.className = 'swiper-slide';
            slide.style.width = '160px'; 
            
            // パスの正規化: 必ず images/ から始まるようにする
            let imgSrc = item.img || item.thumbnail || '';
            if (imgSrc && !imgSrc.startsWith('images/')) {
                imgSrc = 'images/' + imgSrc;
            }

            slide.innerHTML = `
                <a href="${item.url}" target="_blank">
                    <div style="border-radius:12px; overflow:hidden; background:#1a1a1a; border:1px solid #333; height:240px;">
                        <img src="${imgSrc}" style="width:100%; height:100%; object-fit:cover; display:block;" 
                             onerror="this.src='images/photo_9.jpg'">
                    </div>
                </a>`;
            wrapper.appendChild(slide);
        });

        // Swiperを起動
        new Swiper('.swiper', {
            slidesPerView: 'auto',
            spaceBetween: 15,
            freeMode: true,
            grabCursor: true,
            observer: true,
            observeParents: true
        });
        console.log("SHORTスライダーの構築が完了しました");
    } catch (e) { console.error("SHORT Error:", e); }
}
window.addEventListener('load', initShorts);
