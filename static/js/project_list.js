document.addEventListener("DOMContentLoaded", function () {
  const filterForm = document.getElementById("filter-form");
  const sortLinks = document.querySelectorAll(".bar-sort a");
  const moreButton = document.querySelector(".more-button");
  if (filterForm) {
    const searchInput = filterForm.querySelector(".search-bar");

    if (searchInput) {
      searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          filterForm.submit();
        }
      });
    }

    filterForm
      .querySelectorAll(".career input, .work-type input")
      .forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
          filterForm.submit();
        });
      });
  }

  sortLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();

      const linkParams = new URLSearchParams(
        new URL(link.href, window.location.origin).search,
      );
      const params = new URLSearchParams();

      if (filterForm) {
        const formData = new FormData(filterForm);
        formData.forEach(function (value, key) {
          if (!value || key === "sort" || key === "type" || key === "page") {
            return;
          }
          params.append(key, value);
        });
      }

      const nextType = linkParams.get("type");
      const nextSort = linkParams.get("sort");
      if (nextType) {
        params.set("type", nextType);
      }
      if (nextSort) {
        params.set("sort", nextSort);
      }

      window.location.href = "?" + params.toString();

      
    });
  });

  if (moreButton) {
    moreButton.addEventListener("click", function () {
      const currentParams = new URLSearchParams(window.location.search);
      const currentPage = parseInt(currentParams.get("page") || "1", 10);
      currentParams.set("page", currentPage + 1);
      window.location.href = "?" + currentParams.toString() + "#project-list";
    });
  }
});
