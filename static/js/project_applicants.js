// 모달 함수 설정
function openModal(modalEl) {
  modalEl.style.display = "flex";
}

function closeModal(modalEl) {
  modalEl.style.display = "none";
}

// 지원자 카드의 수락/거절 버튼
const applicantBtns = document.querySelectorAll(
  ".applicant-action-btns button",
);

// 지원자 프로필 모달
const applicantProfileModal = document.getElementById(
  "applicant-profile-modal",
);
const closeModalBtn = document.querySelector(".close-modal-btn");
const modalRejectBtn = document.querySelector(".modal-reject-btn");
const modalAcceptBtn = document.querySelector(".modal-accept-btn");

// 지원자 수락, 거절 이중 확인 모달
const applicantDoublecheckModal = document.getElementById(
  "applicant-doublecheck-modal",
);
const doublecheckCancelBtn = document.querySelector(".doublecheck-cancel-btn");
const doublecheckAcceptBtn = document.querySelector(".doublecheck-accept-btn");

// 지원자 프로필 모달 열기
applicantBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    openModal(applicantProfileModal);
  });
});

// 닫기 버튼으로 모달 닫기
closeModalBtn.addEventListener("click", () =>
  closeModal(applicantProfileModal),
);

// 이중 확인 모달 열기
// TPL: 수락, 거절 선택 상태에 따라 모달 내용 다르게 출력 필요
// 거절 확인 모달
modalRejectBtn.addEventListener("click", () => {
  openModal(applicantDoublecheckModal);
});
// 수락 확인 모달
modalAcceptBtn.addEventListener("click", () => {
  openModal(applicantDoublecheckModal);
});

// 모달 전체 닫기
// 수락 제출
doublecheckAcceptBtn.addEventListener("click", () => {
  closeModal(applicantDoublecheckModal);
  closeModal(applicantProfileModal);
});

// 취소
doublecheckCancelBtn.addEventListener("click", () => {
  closeModal(applicantDoublecheckModal);
});

// 배경 클릭으로 모달 닫기
const allModals = [applicantProfileModal, applicantDoublecheckModal];

allModals.forEach((modal) => {
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal(modal);
    }
  });
});
