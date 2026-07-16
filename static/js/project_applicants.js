document.addEventListener("DOMContentLoaded", () => {
  const profileModals = document.querySelectorAll(
    ".applicant-profile-modal",
  );

  const decisionModal = document.getElementById(
    "applicant-doublecheck-modal",
  );

  const decisionForm = document.getElementById(
    "application-decision-form",
  );

  const decisionInput = document.getElementById(
    "application-decision-input",
  );

  const decisionModalTitle = document.getElementById(
    "decision-modal-title",
  );

  const decisionModalText = document.getElementById(
    "decision-modal-text",
  );

  const decisionModalCaption = document.getElementById(
    "decision-modal-caption",
  );

  const decisionSubmitButton = document.getElementById(
    "decision-submit-btn",
  );

  const decisionCancelButton = document.querySelector(
    ".doublecheck-cancel-btn",
  );

  function getOpenedModals() {
    return Array.from(
      document.querySelectorAll(".modal-overlay"),
    ).filter((modal) => {
      return window.getComputedStyle(modal).display !== "none";
    });
  }

  function updateBodyModalState() {
    const hasOpenedModal =
      getOpenedModals().length > 0;

    document.body.classList.toggle(
      "modal-open",
      hasOpenedModal,
    );
  }

  function openModal(modal) {
    if (!modal) return;

    modal.style.display = "flex";
    updateBodyModalState();
  }

  function closeModal(modal) {
    if (!modal) return;

    modal.style.display = "none";
    updateBodyModalState();
  }

  function closeContainingProfileModal(element) {
    const profileModal = element.closest(
      ".applicant-profile-modal",
    );

    if (profileModal) {
      closeModal(profileModal);
    }
  }

  document
    .querySelectorAll(".applicant-profile-open-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        const modalId = button.dataset.modalId;

        if (!modalId) return;

        const profileModal =
          document.getElementById(modalId);

        openModal(profileModal);
      });
    });


  document
    .querySelectorAll(".close-profile-modal-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        closeContainingProfileModal(button);
      });
    });

  document
    .querySelectorAll(".decision-open-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        if (
          !decisionModal ||
          !decisionForm ||
          !decisionInput ||
          !decisionModalTitle ||
          !decisionModalText ||
          !decisionSubmitButton
        ) {
          return;
        }

        const applicantName =
          button.dataset.name || "지원자";

        const decision =
          button.dataset.decision;

        const actionUrl =
          button.dataset.action;

        if (
          !actionUrl ||
          !["accept", "reject"].includes(decision)
        ) {
          return;
        }

        const isAccept =
          decision === "accept";

        const decisionLabel =
          isAccept ? "수락" : "거절";


        closeContainingProfileModal(button);

        decisionForm.action = actionUrl;
        decisionInput.value = decision;

        decisionModalTitle.textContent =
          `${decisionLabel} 확인`;

        decisionModalText.textContent =
          `${applicantName} 님의 지원을 ${decisionLabel}하시겠어요?`;

        if (decisionModalCaption) {
          decisionModalCaption.textContent =
            `${decisionLabel} 후에는 취소할 수 없어요`;
        }

        decisionSubmitButton.textContent =
          decisionLabel;

        decisionSubmitButton.classList.toggle(
          "accept",
          isAccept,
        );

        decisionSubmitButton.classList.toggle(
          "reject",
          !isAccept,
        );

        openModal(decisionModal);
      });
    });

  decisionCancelButton?.addEventListener(
    "click",
    () => {
      closeModal(decisionModal);
    },
  );


  profileModals.forEach((modal) => {
    modal.addEventListener("click", (event) => {
      if (event.target === modal) {
        closeModal(modal);
      }
    });
  });


  decisionModal?.addEventListener(
    "click",
    (event) => {
      if (event.target === decisionModal) {
        closeModal(decisionModal);
      }
    },
  );

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;

    const openedModals = getOpenedModals();

    if (openedModals.length === 0) return;

    const topModal =
      openedModals[openedModals.length - 1];

    closeModal(topModal);
  });
});