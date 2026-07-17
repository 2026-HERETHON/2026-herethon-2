const openButtons = document.querySelectorAll(".openModalBtn");
const closeButtons = document.querySelectorAll(".closeModalBtn");
const modal = document.getElementById("modal");

const applicationForm = document.getElementById("application-form");
const attachBox = document.querySelector(".attach-box");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const attachCount = document.querySelector(".attach-count");
const plusFile = document.querySelector(".plus-file");
const submitFileBtn = document.querySelector(".btn-submit");

const MAX_FILES = 5;
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

const allowedExtensions = [".pdf", ".ppt", ".pptx", ".jpg", ".jpeg", ".png"];

let files = []; // 첨부된 파일들 저장

// 헤더 active 클래스 추가
const menuLinks = document.querySelectorAll(".header-menu a");
console.log(menuLinks);
const currentPath = window.location.pathname;

let bestMatch = null;

menuLinks.forEach((link) => {
  link.classList.remove("active");
  const linkPath = new URL(link.href).pathname;
  console.log(`currentPath: ${currentPath}`);
  console.log(`currentPath.startsWith(): ${currentPath.startsWith(linkPath)}`);
  console.log(`linkPath: ${linkPath}`);

  if (
    currentPath === linkPath ||
    (linkPath !== "/" && currentPath.startsWith(linkPath))
  ) {
    if (
      !bestMatch ||
      linkPath.length > new URL(bestMatch.href).pathname.length
    ) {
      bestMatch = link;
    }
  }
});

if (bestMatch) {
  bestMatch.classList.add("active");
  console.log(`classList: ${bestMatch.classList}`);
}

// menuLinks.forEach((link) => {
//   link.classList.remove("active");

//   const linkPath = new URL(link.href).pathname;
//   console.log(`currentPath: ${currentPath}`);
//   console.log(`linkPath: ${linkPath}`);
//   if (linkPath === currentPath) {
//     link.classList.add("active");
//     console.log(link.classList);
//   }
// });

function openModal() {
  if (!modal) return;

  modal.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function closeModal() {
  if (!modal) return;

  modal.classList.add("hidden");
  document.body.classList.remove("modal-open");
}

openButtons.forEach((button) => {
  button.addEventListener("click", openModal);
});

closeButtons.forEach((button) => {
  button.addEventListener("click", closeModal);
});

modal?.addEventListener("click", (event) => {
  if (event.target === modal) {
    closeModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && modal && !modal.classList.contains("hidden")) {
    closeModal();
  }
});

attachBox?.addEventListener("click", () => {
  fileInput?.click();
});

plusFile?.addEventListener("click", () => {
  fileInput?.click();
});

fileInput?.addEventListener("change", () => {
  addFiles(Array.from(fileInput.files));
  fileInput.value = ""; // 같은 파일 다시 선택할 수 있게 초기화
});

// 드래그 앤 드롭
attachBox?.addEventListener("dragover", (event) => {
  event.preventDefault(); // 이거 없으면 drop 이벤트가 안 먹음
  attachBox.classList.add("drag-over");
});

attachBox?.addEventListener("dragleave", () => {
  attachBox.classList.remove("drag-over");
});

attachBox?.addEventListener("drop", (event) => {
  event.preventDefault(); // 브라우저가 파일을 새 탭으로 열어버리는 것 방지
  attachBox.classList.remove("drag-over");

  addFiles(Array.from(event.dataTransfer.files));
});

function getExtension(filename) {
  const lastDotIndex = filename.lastIndexOf(".");

  if (lastDotIndex === -1) {
    return "";
  }

  return filename.slice(lastDotIndex).toLowerCase();
}

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) {
    return `${Math.round(bytes / 1024)}KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function isDuplicateFile(newFile) {
  return files.some((file) => {
    return (
      file.name === newFile.name &&
      file.size === newFile.size &&
      file.lastModified === newFile.lastModified
    );
  });
}

// 파일 추가 (검증 포함)
function addFiles(newFiles) {
  for (const file of newFiles) {
    if (files.length >= MAX_FILES) {
      alert("파일은 최대 5개까지 첨부할 수 있어요");
      break;
    }

    const extension = getExtension(file.name);

    if (!allowedExtensions.includes(extension)) {
      alert(`${file.name}: 지원하지 않는 파일 형식이에요`);
      continue;
    }

    if (file.size > MAX_SIZE) {
      alert(`${file.name}: 파일 크기는 10MB 이하여야 해요`);
      continue;
    }

    if (isDuplicateFile(file)) {
      alert(`${file.name}: 이미 첨부한 파일이에요`);
      continue;
    }

    files.push(file);
  }

  syncFileInput();
  renderFileList();
}

function removeFile(index) {
  files.splice(index, 1);
  syncFileInput();
  renderFileList();
}

function syncFileInput() {
  if (!fileInput) return;

  const dataTransfer = new DataTransfer();

  files.forEach((file) => {
    dataTransfer.items.add(file);
  });

  fileInput.files = dataTransfer.files;
}

// 파일 목록 그리기
function renderFileList() {
  if (!fileList || !attachCount) return;

  fileList.innerHTML = "";

  files.forEach((file, index) => {
    const item = document.createElement("li");

    //파일 아이콘
    const icon = document.createElement("span");
    icon.className = "file-icon";
    icon.dataset.ext = getExtension(file.name).slice(1);

    // 파일명 + 메타정보 묶음
    const fileInfo = document.createElement("div");
    fileInfo.className = "file-info";

    const filename = document.createElement("span");
    filename.className = "file-name";
    filename.textContent = file.name;

    const fileMeta = document.createElement("small");
    fileMeta.className = "file-meta";
    fileMeta.textContent = `${formatFileSize(file.size)} · 업로드 완료`;

    fileInfo.appendChild(filename);
    fileInfo.appendChild(fileMeta);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "×";
    removeButton.setAttribute("aria-label", `${file.name} 삭제`);

    removeButton.addEventListener("click", () => {
      removeFile(index);
    });

    item.appendChild(icon);
    item.appendChild(fileInfo);
    item.appendChild(removeButton);
    fileList.appendChild(item);
  });

  attachCount.textContent = `첨부 파일 (${files.length}/${MAX_FILES})`;

  if (files.length > 0) {
    attachBox?.classList.add("hidden");
    plusFile?.classList.remove("hidden");
    submitFileBtn?.classList.add("attached");
  } else {
    attachBox?.classList.remove("hidden");
    plusFile?.classList.add("hidden");
    submitFileBtn?.classList.remove("attached");
  }

  if (files.length >= MAX_FILES) {
    plusFile?.classList.add("hidden");
  }
}

applicationForm?.addEventListener("submit", (event) => {
  if (files.length > MAX_FILES) {
    event.preventDefault();
    alert("파일은 최대 5개까지 첨부할 수 있어요");
    return;
  }

  syncFileInput();
});
