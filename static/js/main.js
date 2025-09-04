// Этот код заработает, как только вся страница загрузится
// Этот код заработает, как только вся страница загрузится
// Этот код заработает, как только вся страница загрузится
// Ждем, пока весь HTML-документ будет загружен и готов к работе
document.addEventListener('DOMContentLoaded', function() {

    // --- ФУНКЦИЯ 1: УПРАВЛЕНИЕ МЕНЮ ---
    function handleMenu() {
        const menuContainer = document.getElementById('menu-container');
        const menuIcon = document.getElementById('menu-icon');

        if (!menuContainer || !menuIcon) return;

        let lastScrollY = window.scrollY;
        window.addEventListener('scroll', () => {
            if (lastScrollY < window.scrollY) {
                menuContainer.classList.add('collapsed');
            } else {
                menuContainer.classList.remove('collapsed');
            }
            lastScrollY = window.scrollY;
        });

        menuIcon.addEventListener('click', (event) => {
            event.stopPropagation();
            menuContainer.classList.remove('collapsed');
        });
    }

    // --- ФУНКЦИЯ 2: СЛЕД ЗА КУРСОРОМ ---
    function handleCursorTrail() {
        const trailImages = window.djangoData.trailImages
        if (trailImages.length === 0) return;

        let currentImageIndex = 0;
        document.addEventListener('mousemove', function(e) {
            const trail = document.createElement('div');
            trail.className = 'cursor-trail';
            trail.style.left = `${e.clientX}px`;
            trail.style.top = `${e.clientY}px`;
            trail.style.backgroundImage = `url('${trailImages[currentImageIndex]}')`;
            document.body.appendChild(trail);
            currentImageIndex = (currentImageIndex + 1) % trailImages.length;
            requestAnimationFrame(() => { trail.style.opacity = '1'; });
            setTimeout(() => {
                trail.style.opacity = '0';
                trail.addEventListener('transitionend', () => trail.remove());
            }, 800);
        });
    }

    // --- ФУНКЦИЯ 3: УПРАВЛЕНИЕ ВСЕМИ ФОРМАМИ И КЛИКАМИ ---
    function handleFormsAndClicks() {
         document.querySelectorAll('.post-content, .lot-description').forEach(contentBlock => {
            const targetId = contentBlock.dataset.contentId;
            const readMoreButton = document.querySelector(`.read-more[data-target-id="${targetId}"]`);
            if (readMoreButton) {
                contentBlock.style.maxHeight = '100px';
                contentBlock.classList.add('collapsed');
            }
        });

        const addLotModal = document.getElementById('addLotModal');
        const makeBidModal = document.getElementById('makeBidModal');
        const createPostModal = document.getElementById('createPostModal');
        const lotRequestForm = document.getElementById('lotRequestForm');
        const bidForm = document.getElementById('bidForm');
        const createPostForm = document.getElementById('createPostForm');

        function openModal(modal) { if (modal) modal.classList.add('active'); }
        function closeModal(modal) { if (modal) modal.classList.remove('active'); }

        const handleAjaxFormSubmit = function(event) {
            event.preventDefault();
            const form = event.target;
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && submitButton.disabled) return;
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Отправка...';
            }

            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {'X-CSRFToken': formData.get('csrfmiddlewaretoken')}
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const formBody = form.querySelector('.form-body');
                    const successMessage = form.querySelector('.form-success-message');
                    if (formBody) formBody.style.display = 'none';
                    if (successMessage) successMessage.style.display = 'block';
                    if (form.id === 'createPostForm') {
                        setTimeout(() => window.location.reload(), 1500);
                    }
                } else {
                    alert('Ошибка! ' + (data.message || 'Пожалуйста, проверьте все поля.'));
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = form.id === 'createPostForm' ? 'Создать пост' : 'Отправить';
                    }
                }
            })
            .catch(error => {
                alert('Произошла сетевая ошибка.');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = form.id === 'createPostForm' ? 'Создать пост' : 'Отправить';
                }
                console.error(error);
            });
        };

        if (lotRequestForm) lotRequestForm.addEventListener('submit', handleAjaxFormSubmit);
        if (bidForm) bidForm.addEventListener('submit', handleAjaxFormSubmit);
        if (createPostForm) createPostForm.addEventListener('submit', handleAjaxFormSubmit);

        document.addEventListener('click', function(event) {
            const target = event.target;

            // Кнопки "показать далее" для новостей и лотов
            if (target.matches('.read-more')) {
                const targetId = target.dataset.targetId;
                if (targetId) {
                    // Ищем текстовый блок по его data-атрибуту
                    const content = document.querySelector(`[data-content-id="${targetId}"]`);

                    if (content) {
                        const currentMaxHeight = window.getComputedStyle(content).maxHeight;

                        if (currentMaxHeight !== '100px') {
                            // Если он развернут - сворачиваем
                            content.style.maxHeight = '100px';
                            target.textContent = '...показать далее';
                        } else {
                            // Если он свернут - разворачиваем
                            content.style.maxHeight = content.scrollHeight + "px";
                            target.textContent = '...свернуть';
                        }
                    }
                }
            }

            // Открытие модальных окон
            if (target.matches('#addLotBtn')) {
                if(lotRequestForm) lotRequestForm.reset();
                openModal(addLotModal);
            }
            if (target.matches('#createPostBtn')) {
                if(createPostForm) createPostForm.reset();
                openModal(createPostModal);
            }
            if (target.matches('.btn-make-bid')) {
                const lotId = target.closest('.lot-card')?.dataset.lotId;
                if (lotId && bidForm) {
                    bidForm.action = `/api/lot/${lotId}/bid/create/`;
                    bidForm.reset();
                    openModal(makeBidModal);
                }
            }

            // Закрытие модальных окон
            if (target.matches('.modal-overlay') || target.matches('.btn-close')) {
                const modal = target.closest('.modal-overlay');
                if (modal) {
                    closeModal(modal);
                    // Возвращаем форму в исходное состояние при закрытии
                    const formBody = modal.querySelector('.form-body');
                    const successMessage = modal.querySelector('.form-success-message');
                    if (formBody) formBody.style.display = 'block';
                    if (successMessage) successMessage.style.display = 'none';
                }
            }
                // --- НОВЫЙ БЛОК: Предотвращаем переход по ссылке в режиме редактирования ---
            if (target.closest('.is-editing')) {
                // Если клик произошел внутри карточки, которая сейчас редактируется...
                event.preventDefault(); // ...отменяем все стандартные действия, включая переход по ссылке.
            }
            // --- Логика редактирования ---
            const postCard = target.closest('.post-card');
            if (!postCard) return;

            if (target.matches('.edit-btn')) {
                const editPanel = target.parentElement;
                postCard.querySelectorAll('.editable').forEach(element => {
                    element.setAttribute('contenteditable', 'true');
                    element.style.outline = '2px dashed #007bff';
                    element.dataset.originalHtml = element.innerHTML;
                });
                postCard.classList.add('is-editing');
                const firstEditable = postCard.querySelector('.editable[data-field="title"]');
                if (firstEditable) firstEditable.focus();
                editPanel.innerHTML = `<button class="save-btn">Сохранить</button><button class="cancel-btn">Отмена</button>`;
            }

            if (target.matches('.save-btn')) {
                const postId = postCard.dataset.postId;
                const dataToSend = {};
                postCard.querySelectorAll('.editable').forEach(element => {
                    dataToSend[element.dataset.field] = element.innerText.trim();
                });
                // Здесь мы пока не обрабатываем файлы, только текст

                fetch(`/api/post/${postId}/update/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
                    body: JSON.stringify(dataToSend)
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Ошибка сохранения!');
                    }
                });
            }

            if (target.matches('.cancel-btn')) {
                postCard.querySelectorAll('.editable').forEach(element => {
                    element.innerHTML = element.dataset.originalHtml;
                    element.removeAttribute('contenteditable');
                    element.style.outline = 'none';
                });
                postCard.classList.remove('is-editing');
                postCard.querySelector('.admin-edit-panel').innerHTML = `<button class="edit-btn">Редактировать</button>`;
            }
        });
    }

    // --- ЗАПУСК ВСЕХ ФУНКЦИЙ ---
    handleMenu();
    handleCursorTrail();
    handleFormsAndClicks();
});