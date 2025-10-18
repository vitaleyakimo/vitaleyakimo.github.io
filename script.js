document.addEventListener('DOMContentLoaded', async () => {
    const main = document.querySelector('.portfolios');
    if (!main) return;

    // Карта перевода ключей категорий → человекочитаемые заголовки
    // Добавляйте сюда новые категории по мере необходимости
    const categoryTitles = {
        girls: 'Девушки',
        guys: 'Парни',
        family: 'Семья',
        studio: 'Студия',
        weddings: 'Свадьбы',
        portraits: 'Портреты'
        // Можно добавить другие, или использовать fallback (см. ниже)
    };

    try {
        const response = await fetch('images/portfolio.json');
        if (!response.ok) throw new Error('Не удалось загрузить portfolio.json');
        const data = await response.json();

        // Получаем все ключи из JSON, у которых есть photos — непустой массив
        const autoCategories = Object.keys(data).filter(key => {
            const cat = data[key];
            return cat && Array.isArray(cat.photos) && cat.photos.length > 0;
        });

        // Преобразуем в массив объектов { key, title }
        const categories = autoCategories.map(key => ({
            key: key,
            title: categoryTitles[key] || key.charAt(0).toUpperCase() + key.slice(1) // fallback: "studio" → "Studio"
        }));

        // Сортировка (опционально): можно задать порядок через массив приоритетов
        // Например: ['girls', 'guys', 'studio', 'family']
        // categories.sort((a, b) => autoCategories.indexOf(a.key) - autoCategories.indexOf(b.key));

        categories.forEach(cat => {
            const catData = data[cat.key];
            const photos = catData.photos;
            let currentIndex = 0;
            const total = photos.length;

            const section = document.createElement('section');
            section.className = 'portfolio-category';
            section.innerHTML = `
                <h2>${cat.title}</h2>
                <div class="slider-container" data-category="${cat.key}">
                    <div class="slider">
                        <img src="${photos[0].url}" 
                             alt="${photos[0].alt}" 
                             loading="lazy" 
                             decoding="async"
                             fetchpriority="low">
                    </div>
                    <div class="slider-nav">
                        <button class="prev-btn">‹</button>
                        <button class="next-btn">›</button>
                    </div>
                </div>
            `;
            main.appendChild(section);

            const sliderImg = section.querySelector('.slider img');
            const prevBtn = section.querySelector('.prev-btn');
            const nextBtn = section.querySelector('.next-btn');
            const container = section.querySelector('.slider-container');

            const updateImage = () => {
                sliderImg.src = photos[currentIndex].url;
                sliderImg.alt = photos[currentIndex].alt;
                sliderImg.style.opacity = '';
                sliderImg.onerror = () => sliderImg.style.opacity = '0.4';
            };

            prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                currentIndex = (currentIndex - 1 + total) % total;
                updateImage();
            });

            nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                currentIndex = (currentIndex + 1) % total;
                updateImage();
            });

            let autoSlide = setInterval(() => {
                currentIndex = (currentIndex + 1) % total;
                updateImage();
            }, 5000);

            container.addEventListener('mouseenter', () => clearInterval(autoSlide));
            container.addEventListener('mouseleave', () => {
                clearInterval(autoSlide);
                autoSlide = setInterval(() => {
                    currentIndex = (currentIndex + 1) % total;
                    updateImage();
                }, 5000);
            });

            container.addEventListener('click', () => {
                openModalSlider(photos, currentIndex);
            });
        });

    } catch (error) {
        console.error('Ошибка загрузки портфолио:', error);
        main.innerHTML = '<p style="text-align:center; padding:40px; color:#555;">Не удалось загрузить портфолио. Обновите страницу.</p>';
    }

    // === МОДАЛЬНЫЙ СЛАЙДЕР ===
    function openModalSlider(photoList, startIndex) {
        const modal = document.getElementById('gallery-modal');
        const imgEl = document.getElementById('modal-img');
        const prevBtn = modal.querySelector('.modal-prev');
        const nextBtn = modal.querySelector('.modal-next');
        const closeBtn = document.getElementById('close-modal');
        let currentIndex = startIndex;
        const total = photoList.length;

        const updateImage = () => {
            imgEl.src = photoList[currentIndex].url;
            imgEl.alt = photoList[currentIndex].alt;
        };

        updateImage();

        const closeModal = () => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
            document.removeEventListener('keydown', handleKey);
        };

        const handleKey = (e) => {
            if (e.key === 'Escape') {
                closeModal();
            } else if (e.key === 'ArrowLeft') {
                currentIndex = (currentIndex - 1 + total) % total;
                updateImage();
            } else if (e.key === 'ArrowRight') {
                currentIndex = (currentIndex + 1) % total;
                updateImage();
            }
        };

        prevBtn.onclick = (e) => {
            e.stopPropagation();
            currentIndex = (currentIndex - 1 + total) % total;
            updateImage();
        };

        nextBtn.onclick = (e) => {
            e.stopPropagation();
            currentIndex = (currentIndex + 1) % total;
            updateImage();
        };

        closeBtn.onclick = closeModal;
        modal.onclick = (e) => {
            if (e.target === modal) closeModal();
        };

        document.addEventListener('keydown', handleKey);
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
});