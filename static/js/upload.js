let selectedFiles = [];
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("images");
const progressBar = document.querySelector(".progress-bar");
const uploadProgress = document.getElementById("uploadProgress");

const previewContainer = document.getElementById("previewContainer");
const uploadActions = document.getElementById("uploadActions");
const imageGrid = document.getElementById("image-grid");

function showPreview(files) {
  Array.from(files).forEach((file) => {
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      const previewItem = document.createElement("div");
      previewItem.className = "preview-item";

      reader.onload = (e) => {
        previewItem.innerHTML = `
          <img src="${e.target.result}" alt="Preview">
          <button class="remove-btn" onclick="removeFile(this)" data-file="${file.name}">×</button>
        `;
      };

      reader.readAsDataURL(file);
      previewContainer.appendChild(previewItem);
      selectedFiles.push(file);
    }
  });

  uploadActions.style.display = selectedFiles.length > 0 ? "block" : "none";
}

function removeFile(button) {
  const fileName = button.dataset.file;
  selectedFiles = selectedFiles.filter((file) => file.name !== fileName);
  button.closest(".preview-item").remove();

  uploadActions.style.display = selectedFiles.length > 0 ? "block" : "none";
}

async function uploadImages() {
  uploadProgress.style.display = "block";
  const formData = new FormData();
  selectedFiles.forEach((file) => formData.append("images", file));

  try {
    const response = await fetch("/api/upload/", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData,
    });

    if (!response.ok) throw new Error("Failed to upload images");

    await response.json();
    resetUploadState();
    loadImages();
    Swal.fire({ title: "Success!", text: "Images uploaded successfully", icon: "success" });
  } catch (error) {
    Swal.fire({ title: "Error!", text: error.message, icon: "error" });
  } finally {
    uploadProgress.style.display = "none";
  }
}

function resetUploadState() {
  previewContainer.innerHTML = "";
  selectedFiles = [];
  uploadActions.style.display = "none";
}

function setupDragAndDrop() {
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    showPreview(e.dataTransfer.files);
  });

  fileInput.addEventListener("change", (e) => showPreview(e.target.files));
}

async function loadImages() {
  try {
    const response = await fetch("/api/images/");
    if (!response.ok) throw new Error("Failed to load images");

    const data = await response.json();
    renderImages(data.images);
  } catch (error) {
    console.error(error);
  }
}

function renderImages(images) {
  imageGrid.innerHTML = images
    .map((image) => createImageCard(image))
    .join("");
}

function createImageCard(image) {
  return `
    <div class="col-md-6" id="image-${image.id}">
      <div class="card image-card h-100 shadow-sm">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-6">
              <p class="small text-muted mb-2">Original</p>
              <img src="${image.original_image}" alt="Original" class="img-fluid rounded">
            </div>
            <div class="col-6">
              <p class="small text-muted mb-2">Processed</p>
              ${
                image.processed_image
                  ? `<img src="${image.processed_image}" alt="Processed" class="img-fluid rounded">`
                  : `<div class="text-center py-4">
                      <div class="spinner-border text-primary"></div>
                      <p class="small text-muted mt-2">${image.status}</p>
                    </div>`
              }
            </div>
          </div>
          <div class="d-flex justify-content-between mt-3">
            ${image.processed_image ? createDownloadButton(image.id) : ""}
            ${createDeleteButton(image.id)}
          </div>
        </div>
      </div>
    </div>`;
}

function createDownloadButton(id) {
  return `<button onclick="downloadImage('${id}')" class="btn btn-sm btn-outline-primary">Download</button>`;
}

function createDeleteButton(id) {
  return `<button onclick="deleteImage('${id}')" class="btn btn-sm btn-outline-danger">Delete</button>`;
}

async function deleteImage(id) {
  if (!(await confirmAction("Are you sure?", "You won't be able to revert this!", "warning"))) return;

  try {
    const response = await fetch(`/api/images/${id}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
    });

    if (!response.ok) throw new Error("Failed to delete image");

    document.getElementById(`image-${id}`).remove();
    Swal.fire("Deleted!", "Image has been deleted.", "success");
  } catch (error) {
    Swal.fire("Error!", error.message, "error");
  }
}

async function deleteAllImages() {
  if (!(await confirmAction("Are you sure?", "You will delete all images. This action cannot be undone!", "warning"))) return;

  try {
    const response = await fetch("/api/images/delete-all/", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
    });

    const data = await response.json();
    if (data.status !== "success") throw new Error("Failed to delete images");

    imageGrid.innerHTML = "";
    Swal.fire("Deleted!", "All images have been deleted.", "success");
  } catch (error) {
    Swal.fire("Error!", error.message, "error");
  }
}

function downloadImage(id) {
  window.location.href = `/api/images/${id}/download/`;
}

function downloadAllProcessed() {
  window.location.href = "/api/images/download-all/";
}

async function confirmAction(title, text, icon) {
  const result = await Swal.fire({
    title,
    text,
    icon,
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Yes",
  });
  return result.isConfirmed;
}

setupDragAndDrop();
loadImages();
setInterval(loadImages, 5000);