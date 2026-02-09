const FEATURED_VIDEO_ID = "8HxFsdGL6og";

async function initHeroSlideshow() {
    const heroImg = document.getElementById('random-photo');
    if (!heroImg) return;

    try {
        // キャッシュを避けるためにタイムスタンプを付与
        const response = await fetch('./image_list.json?t=' + new Date().getTime());
        if (!response.ok) throw new Error('Network response was not ok');
        const images = await response.json();
        
        if (!images || images.length === 0) {
            console.error("Image list is empty");
            return;
        }

        let lastIdx = -1;
        const updateImage = () => {
            heroImg.style.opacity = '0';
            setTimeout(() => {
                let newIdx;
                do {
                    newIdx = Math.floor(Math.random() * images.length);
                } while (newIdx === lastIdx && images.length > 1);
                
                lastIdx = newIdx;
                // 画像URLにもキャッシュ対策
                heroImg.src = `images/${images[newIdx]}?v=${new Date().getTime()}`;
                heroImg.onload = () => { heroImg.style.opacity = '1'; };
            }, 500);
        };

        updateImage();
        setInterval(updateImage, 5000);
    } catch (e) {
        console.error("Hero Image Error:", e);
    }
}

// YouTube/Shorts読み込み関数（既存のまま）
function loadFeaturedVideo() {
    const mainVideo = document.getElementById('main-video');
    if (!mainVideo) return;
    mainVideo.innerHTML = `
        <div class="v-main" style="position: relative; padding-bottom: 56.25%; height: 0; border-radius: 15px; overflow: hidden; border: 1px solid #333; background: #000;">
            <iframe src="https://www.youtube.com/embed/${FEATURED_VIDEO_ID}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" frameborder="0" allowfullscreen></iframe>
        </div>
        <p style="color: #d4af37; font-size: 0.7rem; text-align: center; margin-top: 15px; font-weight: bold; opacity: 0.8;">
            King & Prince「Shake Hands」 in Quiet Session Club vol.1
        </p>`;
}

async function loadShorts() {
    const videoList = document.getElementById('video-list');
    if (!videoList) return;
    try {
        const res = await fetch('news.json?t=' + Date.now());
        const data = await res.json();
        const items = data.shorts || [];
        videoList.innerHTML = items.map(item => {
            const vidId = item.id;
            const thumbUrl = `https://img.youtube.com/vi/${vidId}/mqdefault.jpg`;
            return `
                <a href="${item.url}" target="_blank" style="text-decoration: none; width: 150px; flex-shrink: 0; display: block; margin-right: 12px; margin-bottom: 20px;">
                    <div style="width: 100%; aspect-ratio: 9/16; background: #111; border-radius: 15px; overflow: hidden; border: 1px solid #333;">
                        <img src="${thumbUrl}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div style="padding: 0 4px;">
                        <p style="color: #ffffff; font-size: 0.7rem; margin: 10px 0 0; line-height: 1.4; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            ${item.title}
                        </p>
                    </div>
                </a>`;
        }).join('');
    } catch (e) { console.error("Shorts Error:", e); }
}

window.addEventListener('load', () => {
    initHeroSlideshow();
    loadFeaturedVideo();
    loadShorts();
});
