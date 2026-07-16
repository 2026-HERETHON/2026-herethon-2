// 모달 함수 설정
function openModal(modalEl) {
  modalEl.style.display = "flex";
}

function closeModal(modalEl) {
  modalEl.style.display = "none";
}

const back = document.querySelector(".back");
const projectDeleteBtn = document.querySelector(".project-delete-btn");
const projectDeleteModal = document.getElementById("project-delete-modal");
const DeleteCancelBtn = document.getElementById("delete-cancel-btn");
const DeleteBtn = document.getElementById("delete-btn");

projectDeleteBtn.addEventListener("click", () => {
  openModal(projectDeleteModal);
});

projectDeleteModal.addEventListener("click", (e) => {
  if (e.target === projectDeleteModal) {
    closeModal(projectDeleteModal);
  }
});

DeleteCancelBtn.addEventListener("click", () => {
  closeModal(projectDeleteModal);
});

DeleteBtn.addEventListener("click", () => {
  closeModal(projectDeleteModal);
});
