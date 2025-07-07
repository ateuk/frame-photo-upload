const deleteAllBtn = document.getElementById('delete-all-btn');
const viewArchivedBtn = document.getElementById('view-archived-btn');
const viewStocksBtn = document.getElementById('view-stocks-btn');

deleteAllBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to delete all pictures?')) {
        fetch('/delete-all', { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadImages();
                }
            });
    }
});

viewArchivedBtn.addEventListener('click', () => {
    window.location.href = '/archived';
});

viewStocksBtn.addEventListener('click', () => {
    window.location.href = '/stocks';
});

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const progressBar = document.getElementById('progress-bar');
const gallery = document.getElementById('gallery');

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    handleFiles(files);
});

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    handleFiles(files);
});

function handleFiles(files) {
    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
        }
    };

    xhr.onload = () => {
        if (xhr.status === 200) {
            loadImages();
        } else {
            console.error('Upload failed');
        }
        progressBar.style.width = '0%';
    };

    xhr.send(formData);
}

function loadImages() {
    const galleryLoadingOverlay = document.getElementById('gallery-loading-overlay');
    galleryLoadingOverlay.style.display = 'flex';

    fetch('/pictures')
        .then(response => response.json())
        .then(images => {
            const gallery = document.getElementById('gallery');
            gallery.innerHTML = '';
            let imagesLoaded = 0;
            const totalImages = images.length;

            if (totalImages === 0) {
                galleryLoadingOverlay.style.display = 'none';
                return;
            }

            images.forEach(imageData => {
                const thumb = document.createElement('div');
                thumb.classList.add('thumbnail');
                const img = new Image();
                img.src = `/thumbnails/${imageData.thumbnail_filename}?t=${new Date().getTime()}`;
                img.alt = imageData.original_filename;
                img.onload = () => {
                    imagesLoaded++;
                    if (imagesLoaded === totalImages) {
                        galleryLoadingOverlay.style.display = 'none';
                    }
                };
                img.onerror = () => {
                    imagesLoaded++;
                    if (imagesLoaded === totalImages) {
                        galleryLoadingOverlay.style.display = 'none';
                    }
                    console.error(`Error loading image: ${imageData.original_filename}`);
                };

                thumb.innerHTML = `
                    <button class="delete-btn" data-filename="${imageData.original_filename}">&times;</button>
                    <button class="rotate-btn" data-filename="${imageData.original_filename}">&#x21BB;</button>
                    <div class="loading-overlay" style="display: none;"><div class="loading-spinner"></div></div>
                `;
                thumb.prepend(img);
                thumb.querySelector('.rotate-btn').addEventListener('click', function() {
                    const loadingOverlay = thumb.querySelector('.loading-overlay');
                    loadingOverlay.style.display = 'flex';
                    const filename = this.dataset.filename;
                    fetch(`/rotate/${filename}`, {
                            method: 'POST',
                        })
                        .then(response => {
                            if (response.ok) {
                                loadImages();
                            } else {
                                alert('Error rotating image.');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while rotating the image.');
                        })
                        .finally(() => {
                            loadingOverlay.style.display = 'none';
                        });
                });
                gallery.appendChild(thumb);
            });
        });
}

gallery.addEventListener('click', (e) => {
    if (e.target.classList.contains('delete-btn')) {
        const filename = e.target.dataset.filename;
        fetch(`/delete/${filename}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadImages();
                }
            });
    }
});

loadImages();