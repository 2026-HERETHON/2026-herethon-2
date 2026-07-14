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

// 체크박스 그룹에 1개 이상 체크 유효성 검사 함수
function hasAtLeastOneChecked(name) {
  return document.querySelectorAll(`input[name="${name}"]:checked`).length > 0;
}

// 필수 항목 유효성 검사
function validateForm() {
  // 텍스트 입력 항목 id 목록
  const textFieldIds = [
    "company-name", // 기업명
    "project-name", // 프로젝트명
    "project-detail", // 상세 내용
    "recruit-count", // 모집 인원
    "pay-amount", // 보수 금액
    "deadline-date", // 마감일
    "project-period", // 프로젝트 기간
  ];

  // 빈 텍스트 항목이 없을 경우 true
  const textFilled = textFieldIds.every(
    (id) => document.getElementById(id).value.trim() !== "",
  );

  // 모든 라디오 버튼이 체크일 경우 true
  const radioFilled = [
    // 라디오 버튼 항목 name 목록
    // TPL: HTML 코드에서 라디오 input의 name 변경 시 아래에 수정 필요 !
    "job_category", // 직무 유형
    "work_style", // 근무 형태
    "weekly_hours", // 가용 시간
    "career_years", // 경력 연차
  ].every((name) => document.querySelector(`input[name="${name}"]:checked`));

  // 모든 체크박스가 1개 이상 체크일 경우 true
  const checkboxFilled = [
    // 체크박스 항목 name 목록
    // TPL: HTML 코드에서 체크박스 input의 name 변경 시 아래에 수정 필요 !
    "core_times", // 코어 타임
    "preferred_scales", // 업무 규모
    "skill_required", // 보유 스킬
  ].every((name) => hasAtLeastOneChecked(name));

  // 공고 추가 버튼 활성화 유효성 검사
  submitBtn.disabled = !(textFilled && radioFilled && checkboxFilled);
}

// 항목 입력 및 선택 시 유효성 검사 진행
form.addEventListener("input", validateForm);
form.addEventListener("change", validateForm);
