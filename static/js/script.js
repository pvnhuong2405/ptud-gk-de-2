document.addEventListener("DOMContentLoaded", function () {
  // Hiệu ứng mờ dần cho thông báo flash
  const flashMessages = document.querySelectorAll(".message");
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.display = "none";
    }, 5000);
  });

  // Lọc công việc theo danh mục và trạng thái
  const categoryFilter = document.getElementById("category-filter");
  const statusFilter = document.getElementById("status-filter");

  if (categoryFilter && statusFilter) {
    const filterTasks = () => {
      const categoryValue = categoryFilter.value;
      const statusValue = statusFilter.value;
      const taskCards = document.querySelectorAll(".task-card");

      taskCards.forEach((card) => {
        const cardCategory = card.getAttribute("data-category");
        const cardStatus = card.getAttribute("data-status");
        let categoryMatch =
          categoryValue === "all" || cardCategory === categoryValue;
        let statusMatch = statusValue === "all" || cardStatus === statusValue;

        if (categoryMatch && statusMatch) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });

      // Hiển thị trạng thái trống nếu không có công việc nào được hiển thị
      const visibleCards = document.querySelectorAll(
        '.task-card[style="display: block"]'
      );
      const emptyState = document.querySelector(".empty-state");

      if (visibleCards.length === 0 && !emptyState) {
        const taskContainer = document.querySelector(".task-container");
        const newEmptyState = document.createElement("div");
        newEmptyState.className = "empty-state filtered-empty";
        newEmptyState.innerHTML =
          '<i class="fas fa-filter"></i><p>Không tìm thấy công việc nào phù hợp với bộ lọc.</p>';
        taskContainer.appendChild(newEmptyState);
      } else if (visibleCards.length > 0) {
        const filteredEmpty = document.querySelector(".filtered-empty");
        if (filteredEmpty) {
          filteredEmpty.remove();
        }
      }
    };

    categoryFilter.addEventListener("change", filterTasks);
    statusFilter.addEventListener("change", filterTasks);
  }

  // Xử lý form tải lên avatar
  const avatarInput = document.getElementById("avatar");
  const avatarPreview = document.getElementById("avatar-preview");

  if (avatarInput && avatarPreview) {
    avatarInput.addEventListener("change", function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          avatarPreview.style.backgroundImage = `url(${e.target.result})`;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Xử lý nút lấy avatar ngẫu nhiên
  const randomAvatarBtn = document.getElementById("random-avatar-btn");

  if (randomAvatarBtn) {
    randomAvatarBtn.addEventListener("click", function (e) {
      e.preventDefault();

      // Tạo input ẩn để đánh dấu đã nhấn nút random avatar
      const randomInput = document.createElement("input");
      randomInput.type = "hidden";
      randomInput.name = "random_avatar";
      randomInput.value = "true";

      // Thêm input vào form
      const form = randomAvatarBtn.closest("form");
      form.appendChild(randomInput);

      // Submit form
      form.submit();
    });
  }

  // Hiển thị xác nhận trước khi xóa
  const deleteButtons = document.querySelectorAll(".delete-confirm");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      if (!confirm("Bạn có chắc chắn muốn xóa?")) {
        e.preventDefault();
      }
    });
  });

  // Kiểm tra trạng thái completed và hiển thị ngày hoàn thành
  const statusSelect = document.getElementById("status");
  const finishedDateGroup = document.getElementById("finished-date-group");

  if (statusSelect && finishedDateGroup) {
    const toggleFinishedDateVisibility = () => {
      if (statusSelect.value === "completed") {
        finishedDateGroup.style.display = "block";
      } else {
        finishedDateGroup.style.display = "none";
      }
    };

    toggleFinishedDateVisibility();
    statusSelect.addEventListener("change", toggleFinishedDateVisibility);
  }
});
