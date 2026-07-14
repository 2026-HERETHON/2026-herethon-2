const openBtn = document.querySelector(".openModalBtn");
const closeBtn = document.querySelectorAll(".closeModalBtn");
const modal = document.getElementById("modal");

const attachBox = document.querySelector(".attach-box");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const attachCount = document.querySelector(".attach-count");
const plusFile = document.querySelector(".plus-file");

const MAX_FILES = 5;
const MAX_SIZE = 10 * 1024 * 1024; // 10MB
let files = []; // 첨부된 파일들 저장

//추가하기 버튼 클릭 시 모달 열림
openBtn.addEventListener("click", () => {
  modal.classList.remove("hidden");
});

// x버튼, 취소버튼 누르면 모달 닫힘
closeBtn.forEach((btn) => {
  btn.addEventListener("click", () => {
    modal.classList.add("hidden");
  });
});

// 배경(오버레이) 클릭하면 닫기
modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.classList.add("hidden");
  }
});

// 클릭하면 파일 선택창 열기
attachBox.addEventListener("click", () => {
  fileInput.click();
});

plusFile.addEventListener("click", () => {
  fileInput.click();
});

// 파일 선택창에서 파일 고르면
fileInput.addEventListener("change", () => {
  addFiles(fileInput.files);
  fileInput.value = ""; // 같은 파일 다시 선택할 수 있게 초기화
});

// 드래그 앤 드롭
attachBox.addEventListener("dragover", (e) => {
  e.preventDefault(); // 이거 없으면 drop 이벤트가 안 먹음
  attachBox.classList.add("drag-over");
});

attachBox.addEventListener("dragleave", () => {
  attachBox.classList.remove("drag-over");
});

attachBox.addEventListener("drop", (e) => {
  e.preventDefault(); // 브라우저가 파일을 새 탭으로 열어버리는 것 방지
  attachBox.classList.remove("drag-over");
  addFiles(e.dataTransfer.files);
});

// 파일 추가 (검증 포함)
function addFiles(newFiles) {
  for (const file of newFiles) {
    if (files.length >= MAX_FILES) {
      alert("파일은 최대 5개까지 첨부할 수 있어요");
      break;
    }
    if (file.size > MAX_SIZE) {
      alert(`${file.name}은(는) 10MB를 초과해요`);
      continue;
    }
    files.push(file);
  }
  renderFileList();
}

// 파일 목록 그리기
function renderFileList() {
  fileList.innerHTML = "";
  files.forEach((file, i) => {
    const li = document.createElement("li");
    li.textContent = file.name;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "×";
    removeBtn.addEventListener("click", () => {
      files.splice(i, 1);
      renderFileList();
    });

    li.appendChild(removeBtn);
    fileList.appendChild(li);
  });
  attachCount.textContent = `첨부 파일 (${files.length}/5)`;

  if (files.length > 0) {
    attachBox.classList.add("hidden");
    plusFile.classList.remove("hidden");
  }
}
