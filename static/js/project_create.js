const form = document.getElementById("project-create-form");
const submitButton = document.querySelector(".create-project-btn");

const requiredGuide = document.getElementById("required-skill-guide");
const preferredGuide = document.getElementById("preferred-skill-guide");

const requiredWrapper = document.getElementById("required-skill-wrapper");
const preferredWrapper = document.getElementById("preferred-skill-wrapper");

const hiddenAbilityButton = document.getElementById("hidden-ability-open-btn");
const hiddenAbilitiesInput = document.getElementById("hidden-abilities-input");

const modalOverlay = document.querySelector(".modal-overlay");
const modalBody = document.querySelector(".modal-body");
const modalCloseButton = document.querySelector(".modal-close-btn");
const hiddenAbilityAddButton = document.querySelector(
  ".hidden-ability-add-btn",
);

const skillsByJob = window.skillsByJob || {};
const hiddenAbilitiesByJob = window.hiddenAbilitiesByJob || {};

const staticImages = window.staticImages || {};

let selectedJobId = null;
let selectedJobName = "";

let selectedRequiredSkills = new Set(
  (window.initialRequiredSkills || []).map(String),
);

let selectedPreferredSkills = new Set(
  (window.initialPreferredSkills || []).map(String),
);

let selectedHiddenAbilities = new Set(
  (window.initialHiddenAbilities || []).map(String),
);

let confirmedHiddenAbilities = new Set(selectedHiddenAbilities);

/* 직무 선택 */
document.querySelectorAll('input[name="job_category"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    selectedJobId = String(radio.value);

    selectedJobName =
      radio.dataset.jobName || radio.closest("label")?.textContent.trim() || "";

    // 직무 변경 시 기존 선택값 초기화
    selectedRequiredSkills.clear();
    selectedPreferredSkills.clear();
    selectedHiddenAbilities.clear();
    confirmedHiddenAbilities.clear();

    syncHiddenAbilitiesInput();

    // 숨은 능력 버튼 문구도 초기화
    hiddenAbilityButton.textContent = "추가하기";

    renderRequiredSkills();
    renderPreferredSkills();

    requiredGuide.style.display = "none";
    hiddenAbilityButton.disabled = false;

    validateForm();
  });
});

/* 필수 스킬 출력 */
function renderRequiredSkills() {
  requiredWrapper.innerHTML = "";

  if (!selectedJobId) {
    requiredGuide.style.display = "block";
    return;
  }

  requiredGuide.style.display = "none";

  const skills = skillsByJob[String(selectedJobId)] || [];

  if (skills.length === 0) {
    requiredGuide.textContent = "해당 직무에 등록된 스킬이 없습니다.";
    requiredGuide.style.display = "block";
    return;
  }

  const group = document.createElement("div");
  group.className = "skill-btn-group";
  group.style.display = "flex";

  skills.forEach((skill) => {
    const skillId = String(skill.id);

    const label = document.createElement("label");
    label.className = "skill-btn";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = "skill_required";
    input.value = skillId;
    input.checked = selectedRequiredSkills.has(skillId);

    input.addEventListener("change", () => {
      if (input.checked) {
        selectedRequiredSkills.add(skillId);
      } else {
        selectedRequiredSkills.delete(skillId);

        // 필수에서 해제하면 우대에서도 제거
        selectedPreferredSkills.delete(skillId);
      }

      renderPreferredSkills();
      validateForm();
    });

    label.appendChild(input);
    label.appendChild(document.createTextNode(skill.name));

    group.appendChild(label);
  });

  requiredWrapper.appendChild(group);
}

/* 필수 스킬 중 우대로 지정할 항목 */
function renderPreferredSkills() {
  preferredWrapper.innerHTML = "";

  if (!selectedJobId) {
    preferredGuide.textContent = "직무를 먼저 선택해주세요.";
    preferredGuide.style.display = "block";
    return;
  }

  if (selectedRequiredSkills.size === 0) {
    preferredGuide.textContent = "필수 스킬을 먼저 선택해주세요.";
    preferredGuide.style.display = "block";
    return;
  }

  preferredGuide.style.display = "none";

  const skills = skillsByJob[String(selectedJobId)] || [];

  const selectedSkills = skills.filter((skill) =>
    selectedRequiredSkills.has(String(skill.id)),
  );

  const group = document.createElement("div");
  group.className = "skill-btn-group";
  group.style.display = "flex";

  selectedSkills.forEach((skill) => {
    const skillId = String(skill.id);

    const label = document.createElement("label");
    label.className = "skill-btn";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = "skill_preferred";
    input.value = skillId;
    input.checked = selectedPreferredSkills.has(skillId);

    input.addEventListener("change", () => {
      if (input.checked) {
        selectedPreferredSkills.add(skillId);
      } else {
        selectedPreferredSkills.delete(skillId);
      }
    });

    label.appendChild(input);
    label.appendChild(document.createTextNode(skill.name));

    group.appendChild(label);
  });

  preferredWrapper.appendChild(group);
}

/* 숨은 능력 모달 */
hiddenAbilityButton?.addEventListener("click", () => {
  if (!selectedJobId) return;

  const checkedJob = document.querySelector(
    'input[name="job_category"]:checked',
  );

  if (!checkedJob) return;

  selectedJobName =
    checkedJob.dataset.jobName ||
    checkedJob.closest("label")?.textContent.trim() ||
    "";

  document.querySelector(".modal-title").textContent =
    `숨은 능력 매칭 항목 추가_${selectedJobName}`;

  document.querySelector(".modal-caption").textContent =
    `${selectedJobName} 직무와 관련된 숨은 능력을 선택하면 매칭률에 반영돼요`;

  renderHiddenAbilities();

  modalOverlay.style.display = "flex";
});

function renderHiddenAbilities() {
  modalBody.innerHTML = "";

  const abilities = hiddenAbilitiesByJob[String(selectedJobId)] || [];

  const originalActivities = originalActivitiesByJob[selectedJobName] || [];

  const list = document.createElement("div");
  list.className = "hidden-ability-list";
  list.style.display = "flex";

  if (abilities.length === 0) {
    const emptyMessage = document.createElement("p");
    emptyMessage.className = "skill-guide-msg";
    emptyMessage.textContent = "해당 직무에 등록된 숨은 능력이 없습니다.";

    modalBody.appendChild(emptyMessage);
    validateModalButton();
    return;
  }

  abilities.forEach((ability, index) => {
    const abilityId = String(ability.id);
    const isChecked = selectedHiddenAbilities.has(abilityId);

    const originalText = originalActivities[index] || "관련 활동 경험";

    const item = document.createElement("div");
    item.className = "hidden-ability-item";

    // 체크박스 버튼
    const checkboxButton = document.createElement("button");

    checkboxButton.type = "button";
    checkboxButton.className = "checkbox";
    checkboxButton.dataset.key = abilityId;
    checkboxButton.dataset.checked = String(isChecked);

    const checkboxImage = document.createElement("img");

    checkboxImage.src = isChecked
      ? staticImages.checkboxChecked
      : staticImages.checkboxBlank;

    checkboxImage.alt = "checkbox";

    checkboxButton.appendChild(checkboxImage);

    // 변환 전 활동
    const originalAbility = document.createElement("div");

    originalAbility.className = "hidden-ability-text original";

    originalAbility.textContent = originalText;

    // 화살표
    const rightArrow = document.createElement("img");

    rightArrow.className = "right-arrow-img";
    rightArrow.src = staticImages.rightArrow;
    rightArrow.alt = "숨은 능력 변환";

    // 변환된 숨은 능력
    const translatedAbility = document.createElement("div");

    translatedAbility.className = "hidden-ability-text translated";

    const greenIcon = document.createElement("img");

    greenIcon.className = "green-icon";
    greenIcon.src = staticImages.greenEllipse;
    greenIcon.alt = "";

    const translatedText = document.createElement("span");

    translatedText.className = "translated-text";

    translatedText.textContent = ability.name;

    translatedAbility.appendChild(greenIcon);
    translatedAbility.appendChild(translatedText);

    checkboxButton.addEventListener("click", () => {
      if (selectedHiddenAbilities.has(abilityId)) {
        selectedHiddenAbilities.delete(abilityId);
      } else {
        selectedHiddenAbilities.add(abilityId);
      }

      renderHiddenAbilities();
    });

    item.appendChild(checkboxButton);
    item.appendChild(originalAbility);
    item.appendChild(rightArrow);
    item.appendChild(translatedAbility);

    list.appendChild(item);
  });

  modalBody.appendChild(list);
  validateModalButton();
}

function validateModalButton() {
  if (!hiddenAbilityAddButton) return;

  // hiddenAbilityAddButton.disabled = selectedHiddenAbilities.size === 0;
  hiddenAbilityAddButton.disabled = false; // 항상 활성화
}

modalCloseButton?.addEventListener("click", () => {
  selectedHiddenAbilities = new Set(confirmedHiddenAbilities);
  modalOverlay.style.display = "none";
});

modalOverlay?.addEventListener("click", (event) => {
  if (event.target === modalOverlay) {
    selectedHiddenAbilities = new Set(confirmedHiddenAbilities);
    modalOverlay.style.display = "none";
  }
});

hiddenAbilityAddButton?.addEventListener("click", () => {
  confirmedHiddenAbilities = new Set(selectedHiddenAbilities);
  syncHiddenAbilitiesInput();
  modalOverlay.style.display = "none";

  hiddenAbilityButton.textContent =
    selectedHiddenAbilities.size > 0
      ? `${selectedHiddenAbilities.size}개 추가됨`
      : "추가하기";
});

function syncHiddenAbilitiesInput() {
  hiddenAbilitiesInput.value = JSON.stringify([...selectedHiddenAbilities]);
}

/* 필수 항목 검사 */
function hasCheckedInput(name) {
  return Boolean(document.querySelector(`input[name="${name}"]:checked`));
}

function validateForm() {
  const requiredTextIds = [
    "project-name",
    "project-detail",
    "recruit-count",
    "pay-amount",
    "deadline-date",
    "project-period",
  ];

  const textFilled = requiredTextIds.every((id) => {
    const element = document.getElementById(id);

    return element && String(element.value).trim() !== "";
  });

  const radioFilled = [
    "job_category",
    "work_style",
    "weekly_hours",
    "career_years",
  ].every(hasCheckedInput);

  const checkboxFilled = [
    "core_times",
    "preferred_scales",
    "skill_required",
  ].every(hasCheckedInput);

  submitButton.disabled = !(textFilled && radioFilled && checkboxFilled);
}

form?.addEventListener("input", validateForm);
form?.addEventListener("change", validateForm);

form?.addEventListener("submit", () => {
  syncHiddenAbilitiesInput();
});

/* POST 오류 후 선택값 복원 */
function initializeForm() {
  const checkedJob = document.querySelector(
    'input[name="job_category"]:checked',
  );

  if (checkedJob) {
    selectedJobId = String(checkedJob.value);

    selectedJobName =
      checkedJob.dataset.jobName ||
      checkedJob.closest("label")?.textContent.trim() ||
      "";

    requiredGuide.style.display = "none";
    hiddenAbilityButton.disabled = false;

    renderRequiredSkills();
    renderPreferredSkills();
  }

  syncHiddenAbilitiesInput();

  if (selectedHiddenAbilities.size > 0) {
    hiddenAbilityButton.textContent = `${selectedHiddenAbilities.size}개 추가됨`;
  }

  validateForm();
}

initializeForm();

// 입력창 선택 시 날짜 선택창 뜨도록
const dateInput = document.querySelector('.form-input[type="date"]');

dateInput.addEventListener("click", () => {
  dateInput.showPicker();
});
