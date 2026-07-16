document.addEventListener("DOMContentLoaded", () => {
  // 공통 모달
  function openModal(modal) {
    if (!modal) return;

    modal.style.display = "flex";
    document.body.classList.add("modal-open");
  }

  function closeModal(modal) {
    if (!modal) return;

    modal.style.display = "none";

    const opened = [...document.querySelectorAll(".modal-overlay")].some(
      (modal) => modal.style.display === "flex",
    );

    if (!opened) {
      document.body.classList.remove("modal-open");
    }
  }

  // 리턴십 모달

  const returnshipModal =
    document.getElementById("returnship-modal");

  const returnshipForm =
    document.getElementById("returnship-form");

  const closeModalBtn =
    document.querySelector(".close-modal-btn");

  const submitBtn =
    document.querySelector(".submit-returnship-btn");

  const titleInput =
    document.getElementById("returnship-title");

  const detailTextarea =
    document.getElementById("returnship-detail");

  // 리턴십 제안하기 버튼 클릭 시 모달 열기
  document
    .querySelectorAll(".open-returnship-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        if (!returnshipModal || !returnshipForm) return;

        const actionUrl = button.dataset.action;

        if (!actionUrl) {
          console.error(
            "리턴십 제안 URL이 없습니다.",
          );
          return;
        }

        returnshipForm.reset();
        returnshipForm.action = actionUrl;

        if (submitBtn) {
          submitBtn.disabled = true;
        }

        returnshipModal.style.display = "flex";
        document.body.classList.add("modal-open");
      });
    });

  // 제목과 내용이 모두 입력됐는지 검사
  function checkReturnshipValidity() {
    if (
      !titleInput ||
      !detailTextarea ||
      !submitBtn
    ) {
      return;
    }

    const textFilled =
      titleInput.value.trim() !== "" &&
      detailTextarea.value.trim() !== "";

    submitBtn.disabled = !textFilled;
  }

  titleInput?.addEventListener(
    "input",
    checkReturnshipValidity,
  );

  detailTextarea?.addEventListener(
    "input",
    checkReturnshipValidity,
  );

  // 모달 닫기
  function closeReturnshipModal() {
    if (!returnshipModal) return;

    returnshipModal.style.display = "none";
    document.body.classList.remove("modal-open");
  }

  closeModalBtn?.addEventListener(
    "click",
    closeReturnshipModal,
  );

  // 배경 클릭 시 모달 닫기
  returnshipModal?.addEventListener(
    "click",
    (event) => {
      if (event.target === returnshipModal) {
        closeReturnshipModal();
      }
    },
  );

  // 공고 삭제 모달
  const deleteModal =
    document.getElementById("project-delete-modal");

  const deleteForm =
    document.getElementById("project-delete-form");

  const deleteCaption =
    document.getElementById("delete-project-caption");

  const deleteCancelButton =
    document.getElementById("delete-cancel-btn");

  document
    .querySelectorAll(".project-delete-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        deleteForm.action = button.dataset.deleteUrl;

        if (deleteCaption) {
          deleteCaption.textContent =
            "삭제하면 참여 인원과의 대화, 진행 기록이\n모두 함께 삭제되며 복구할 수 없어요.";
        }

        openModal(deleteModal);
      });
    });

  deleteCancelButton?.addEventListener("click", () => {
    closeModal(deleteModal);
  });

  deleteModal?.addEventListener("click", (e) => {
    if (e.target === deleteModal) {
      closeModal(deleteModal);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;

    closeModal(returnshipModal);
    closeModal(deleteModal);
  });
});
