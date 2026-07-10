// 탭 네비게이션 설정
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab; // profile, apply, offer, condition

    // 모든 버튼의 active 해제
    tabBtns.forEach((b) => b.classList.remove("active"));
    // 클릭한 버튼 active 설정
    btn.classList.add("active");

    // 모든 탭 active 해제
    tabContents.forEach((content) => content.classList.remove("active"));
    // 클릭한 메뉴의 탭 active 설정
    const targetContent = document.getElementById(`tab-${target}`);
    targetContent.classList.add("active");
  });
});

// 근무 조건 수정 모달 설정
function openModal(modalEl) {
  modalEl.style.display = "flex";
}

function closeModal(modalEl) {
  modalEl.style.display = "none";
}

// 희망 직무 모달
const jobModal = document.getElementById("job-modal");
const openJobBtn = document.getElementById("open-job-modal");
const closeJobBtn = document.getElementById("done-job-modal");

openJobBtn.addEventListener("click", () => openModal(jobModal));
closeJobBtn.addEventListener("click", () => closeModal(jobModal));

// 보유 스킬 모달
const skillModal = document.getElementById("skill-modal");
const openSkillBtn = document.getElementById("open-skill-modal");
const closeSkillBtn = document.getElementById("done-skill-modal");

openSkillBtn.addEventListener("click", () => openModal(skillModal));
closeSkillBtn.addEventListener("click", () => closeModal(skillModal));

// 가용 시간 모달
const scheduleModal = document.getElementById("schedule-modal");
const openScheduleBtn = document.getElementById("open-schedule-modal");
const closeScheduleBtn = document.getElementById("done-schedule-modal");

openScheduleBtn.addEventListener("click", () => openModal(scheduleModal));
closeScheduleBtn.addEventListener("click", () => closeModal(scheduleModal));

// 모달 배경 클릭 처리
const allModals = [jobModal, skillModal, scheduleModal];

allModals.forEach((modal) => {
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal(modal);
    }
  });
});
