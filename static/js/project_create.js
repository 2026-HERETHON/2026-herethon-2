// 변수
const form = document.getElementById("project-create-form");
const submitBtn = document.querySelector(".create-project-btn");

const preferredGuide = document.getElementById("preferred-skill-guide");
const requiredGuide = document.getElementById("required-skill-guide");

const hiddenAbilityBtn = document.getElementById("hidden-ability-open-btn");
const hiddenAbilitiesInput = document.getElementById("hidden-abilities-input");
const weightInput = document.getElementById("hidden-ability-weight-input");

const modalOverlay = document.querySelector(".modal-overlay");

// 선택한 숨은 능력 목록
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

// 숨은 능력 모달 열기 (직무별 리스트 토글 + 타이틀 갱신 + 선택값 복원)
hiddenAbilityBtn.addEventListener("click", () => {
  // 1. 직무별 타이틀 갱신
  const selectedRadio = document.querySelector(
    // TPL: HTML에서 직무 유형 input name 수정 시 아래 name 변경 필요
    'input[name="job_category"]:checked',
  );
  if (!selectedRadio) return;

  const jobId = selectedRadio.value;
  const jobLabel = selectedRadio.closest("label").textContent.trim();

  document.querySelector(".modal-title").textContent =
    `숨은 능력 매칭 항목 추가_${jobLabel}`;
  document.querySelector(".modal-caption").textContent =
    `${jobLabel} 직무와 관련된 숨은 능력을 선택하면 매칭 가중치에 반영돼요`;

  // 2. 선택한 직무에 따른 숨은 능력 리스트 표시/숨김
  document.querySelectorAll(".hidden-ability-list").forEach((list) => {
    list.style.display = list.dataset.jobId === jobId ? "flex" : "none";
  });

  // 3. 숨은 능력 선택값 복원
  const activeList = document.querySelector(
    `.hidden-ability-list[data-job-id="${jobId}"]`,
  );

  if (activeList) {
    activeList.querySelectorAll(".checkbox").forEach((btn) => {
      // 이미 선택된 항목인 경우 isChecked true
      const isChecked = selectedHiddenAbilities.includes(btn.dataset.key);
      btn.dataset.checked = String(isChecked);

      // 버튼 선택 상태에 따라 체크박스 이미지 교체
      btn.querySelector("img").src = isChecked
        ? btn
            .querySelector("img")
            .src.replace("checkbox-blank", "checkbox-checked")
        : btn
            .querySelector("img")
            .src.replace("checkbox-checked", "checkbox-blank");
    });
  }

  // 4. 매칭 가중치 선택값 복원
  // TPL: 숨은 능력 팝업의 매칭 가중치 input name 변경 시 아래 코드 수정 필요
  document
    .querySelectorAll('input[name="matching_weight"]')
    .forEach((r) => (r.checked = false));

  if (weightInput.value) {
    const radio = document.querySelector(
      `input[name="matching_weight"][value="${weightInput.value}"]`,
    );
    if (radio) radio.checked = true;
  }

  modalOverlay.style.display = "flex";
  validateModalButton();
});

document.querySelector(".modal-close-btn").addEventListener("click", () => {
  modalOverlay.style.display = "none";
});

// 모달 내 체크박스 토글
document.querySelector(".modal-body").addEventListener("click", (e) => {
  const btn = e.target.closest(".checkbox");
  if (!btn) return;

  const isChecked = btn.dataset.checked === "true";
  btn.dataset.checked = String(!isChecked);

  const img = btn.querySelector("img");
  img.src = !isChecked
    ? img.src.replace("checkbox-blank", "checkbox-checked")
    : img.src.replace("checkbox-checked", "checkbox-blank");

  validateModalButton();
});

const addBtn = document.querySelector(".hidden-ability-add-btn");

// 추가하기 버튼 활성화 조건 검사
function validateModalButton() {
  const weightChecked = !!document.querySelector(
    'input[name="matching_weight"]:checked',
  );

  const activeList = document.querySelector(
    '.hidden-ability-list[style*="display: flex"]',
  );
  const abilityChecked = activeList
    ? activeList.querySelectorAll('.checkbox[data-checked="true"]').length > 0
    : false;

  addBtn.disabled = !(weightChecked && abilityChecked);
}

// 매칭 가중치 라디오
document.querySelectorAll('input[name="matching_weight"]').forEach((radio) => {
  radio.addEventListener("change", validateModalButton);
});

// 숨은 능력 모달의 추가하기 버튼
document
  .querySelector(".hidden-ability-add-btn")
  .addEventListener("click", () => {
    const weightRadio = document.querySelector(
      'input[name="matching_weight"]:checked',
    );

    // 선택된 직무의 숨은 능력 리스트
    const activeList = document.querySelector(
      '.hidden-ability-list[style*="display: flex"]',
    );

    // 선택된 숨은 능력의 data-key 리스트
    const checkedKeys = [
      ...activeList.querySelectorAll('.checkbox[data-checked="true"]'),
    ].map((btn) => btn.dataset.key);

    selectedHiddenAbilities = checkedKeys;
    // TPL: 백에서 숨은 능력, 매칭 가중치 받는 형태로 수정
    hiddenAbilitiesInput.value = JSON.stringify(checkedKeys);
    weightInput.value = weightRadio.value;

    modalOverlay.style.display = "none";
  });
