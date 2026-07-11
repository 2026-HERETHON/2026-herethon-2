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
const jobUnselectedList = document.getElementById("job-unselected-list");
const selectedJobTagList = document.getElementById("job-tag-list");

// 1. 모달 열기
openJobBtn.addEventListener("click", () => openModal(jobModal));

// 2. 미선택 태그 선택
jobUnselectedList.addEventListener("click", (e) => {
  const btn = e.target.closest(".unselected-tag");
  if (!btn) return; // 버튼 아닌 곳 클릭이면 무시

  btn.classList.toggle("selected"); // 선택 표시만 토글
});

// 3. 선택 태그 리스트에 추가 및 모달 닫기
closeJobBtn.addEventListener("click", () => {
  const selectedBtns = jobUnselectedList.querySelectorAll(
    ".unselected-tag.selected",
  );

  selectedBtns.forEach((btn) => {
    const label = btn.textContent.replace("+", "").trim(); // "데이터 분석 +" -> "데이터 분석"

    // 선택된 tag-list에 새 태그 추가
    const newTag = document.createElement("span");
    newTag.className = "tag-item";
    newTag.innerHTML = `
    ${label} <button type="button" class="btn-tag-remove">✕</button>
    `;
    selectedJobTagList.appendChild(newTag);

    // 모달의 미선택 목록에서는 제거 (이미 선택됐으니 다시 안 보이게)
    btn.remove();
  });

  // 모달 닫기
  closeModal(jobModal);
});

// 4. 선택 태그 리스트에서 삭제
selectedJobTagList.addEventListener("click", (e) => {
  const btn = e.target.closest(".btn-tag-remove");
  if (!btn) return;

  const tagItem = btn.closest(".tag-item");
  const label = tagItem.textContent.replace(btn.textContent, "").trim();

  // 삭제할 태그 모달 내의 미선택 태그 리스트에 추가
  const removeTag = document.createElement("button");
  removeTag.className = "unselected-tag";
  removeTag.type = "button";
  removeTag.innerHTML = `${label} +`;
  jobUnselectedList.appendChild(removeTag);

  // 태그 삭제
  tagItem.remove();
});

// 보유 스킬 모달
const skillModal = document.getElementById("skill-modal");
const openSkillBtn = document.getElementById("open-skill-modal");
const closeSkillBtn = document.getElementById("done-skill-modal");
const skillUnselectedList = document.getElementById("skill-unselected-list");
const selectedSkillTagList = document.getElementById("skill-tag-list");

// 1. 모달 열기
openSkillBtn.addEventListener("click", () => openModal(skillModal));

// 2. 미선택 태그 선택
skillUnselectedList.addEventListener("click", (e) => {
  const btn = e.target.closest(".unselected-tag");
  if (!btn) return; // 버튼 아닌 곳 클릭이면 무시

  btn.classList.toggle("selected"); // 선택 표시만 토글
});

// 3. 선택 태그 리스트에 추가 및 모달 닫기
closeSkillBtn.addEventListener("click", () => {
  const selectedBtns = skillUnselectedList.querySelectorAll(
    ".unselected-tag.selected",
  );

  selectedBtns.forEach((btn) => {
    const label = btn.textContent.replace("+", "").trim();

    // 선택된 tag-list에 새 태그 추가
    const newTag = document.createElement("span");
    newTag.className = "tag-item";
    newTag.innerHTML = `
    ${label} <button type="button" class="btn-tag-remove">✕</button>
    `;
    selectedSkillTagList.appendChild(newTag);

    // 모달의 미선택 목록에서는 제거 (이미 선택됐으니 다시 안 보이게)
    btn.remove();
  });

  // 모달 닫기
  closeModal(skillModal);
});

// 4. 선택 태그 리스트에서 삭제
selectedSkillTagList.addEventListener("click", (e) => {
  const btn = e.target.closest(".btn-tag-remove");
  if (!btn) return;

  const tagItem = btn.closest(".tag-item");
  const label = tagItem.textContent.replace(btn.textContent, "").trim();

  // 삭제할 태그 모달 내의 미선택 태그 리스트에 추가
  const removeTag = document.createElement("button");
  removeTag.className = "unselected-tag";
  removeTag.type = "button";
  removeTag.innerHTML = `${label} +`;
  skillUnselectedList.appendChild(removeTag);

  // 태그 삭제
  tagItem.remove();
});

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
