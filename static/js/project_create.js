// 변수
const form = document.getElementById("project-create-form");
const submitBtn = document.querySelector(".create-project-btn");

const preferredGuide = document.getElementById("preferred-skill-guide");
const requiredGuide = document.getElementById("required-skill-guide");

const hiddenAbilityBtn = document.getElementById("hidden-ability-open-btn");
const hiddenAbilitiesInput = document.getElementById("hidden-abilities-input");
const weightInput = document.getElementById("hidden-ability-weight-input");

const modalOverlay = document.querySelector(".modal-overlay");

let selectedHiddenAbilities = [];

// 직무 선택 시 스킬 그룹 토글 (생성x, 표시/숨김 전환)
// TPL: 직무 유형 input name 값 job_category로 작성. 연동하면서 HTML 수정 시 아래 코드 수정 필요
document.querySelectorAll('input[name="job_category"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    const jobId = radio.value;

    document
      .querySelectorAll("#preferred-skill-wrapper .skill-btn-group")
      .forEach((group) => {
        group.style.display = group.dataset.jobId === jobId ? "flex" : "none";
      });
    document
      .querySelectorAll("#required-skill-wrapper .skill-btn-group")
      .forEach((group) => {
        group.style.display = group.dataset.jobId === jobId ? "flex" : "none";
      });

    // 안내 메세지 숨김 처리
    preferredGuide.style.display = "none";
    requiredGuide.style.display = "none";

    // 숨은 능력 추가하기 버튼 활성화
    hiddenAbilityBtn.disabled = false;

    // 직무 변경 시 숨은 능력 선택 및 다른 직무 스킬 체크값 초기화
    resetSkillChecksExcept(jobId);
    selectedHiddenAbilities = [];
    hiddenAbilitiesInput.value = "[]";
    weightInput.value = "";

    validateForm();
  });
});

// 직무 변경 시 현재 선택한 직무 외의 스킬 체크값 초기화
function resetSkillChecksExcept(jobId) {
  document.querySelectorAll(".skill-btn-group").forEach((group) => {
    if (group.dataset.jobId !== jobId) {
      group
        .querySelectorAll('input[type="checkbox"]')
        .forEach((cb) => (cb.checked = false));
    }
  });
}
