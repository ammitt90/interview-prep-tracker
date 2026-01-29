const API_BASE_URL = "http://localhost:5001"; // Base URL for API calls

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const problemForm = document.getElementById("problemForm"); // Problem submission form
  const problemsContainer = document.getElementById("problems"); // Container to display problems
  const updateProblemModalElement = document.getElementById("updateProblemModal"); // Modal for updating problems
  const updateProblemModal = new bootstrap.Modal(updateProblemModalElement); // Initialize the modal

  // ==============================
  // Fetch and display problems
  // ==============================
  async function fetchProblems() {
    try {
      const response = await fetch(`${API_BASE_URL}/problems`);
      if (!response.ok) throw new Error("Failed to fetch problems");

      const problems = await response.json();
      displayProblems(problems);
    } catch (error) {
      alert("Error fetching problems");
      console.error(error);
    }
  }

  // ==============================
  // Render problems
  // ==============================
  function displayProblems(problems) {
    // Clear existing problems
    problemsContainer.innerHTML = "";

    // If no problems exist
    if (!problems || problems.length === 0) {
      problemsContainer.innerHTML = "<div>No problems present</div>";
      return;
    }

    // Loop through problems
    problems.forEach((problem) => {
      const item = document.createElement("li");
      item.className = "list-group-item";

      item.innerHTML = `
        <div>
          <strong>Problem Title: ${problem.title}</strong><br/>
          Status: ${problem.status}<br/>
          Difficulty: ${problem.difficulty}<br/>
          Deadline: ${problem.deadline_date || "N/A"}<br/>
          Topic: ${problem.topic || "N/A"}
        </div>
        <button onclick="openUpdateModal(${problem.id})" class="btn btn-warning btn-sm mt-2">
          Update
        </button>
        <button onclick="deleteProblem(${problem.id})" class="btn btn-danger btn-sm mt-2">
          Delete
        </button>
      `;

      problemsContainer.appendChild(item);
    });
  }

  // ==============================
  // Add new problem
  // ==============================
  problemForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevent default form submission

    const formData = new FormData(problemForm);

    const deadline = formData.get("deadline_date");
    let formattedDeadline = null;

    if (deadline) {
      const date = new Date(deadline);
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, "0");
      const d = String(date.getDate()).padStart(2, "0");
      formattedDeadline = `${y}-${m}-${d}`;
    }

    const newProblem = {
      title: formData.get("title"),
      topic: formData.get("topic"),
      difficulty: parseInt(formData.get("difficulty")),
      status: formData.get("status"),
      deadline_date: formattedDeadline,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/problems`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newProblem),
      });

      if (!response.ok) throw new Error("Error adding problem");

      problemForm.reset();
      fetchProblems();
    } catch (error) {
      alert("Error adding problem");
      console.error(error);
    }
  });

  // ==============================
  // Open update modal
  // ==============================
  window.openUpdateModal = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/problems/${id}`);
      if (!response.ok) throw new Error("Failed to fetch problem");

      const problem = await response.json();

      document.getElementById("updateStatus").value = problem.status;

      document.getElementById("saveUpdateBtn").onclick = async () => {
        try {
          const updatedStatus = document.getElementById("updateStatus").value;

          const updateResponse = await fetch(
            `${API_BASE_URL}/problems/updatestatus/${id}`,
            {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ status: updatedStatus }),
            }
          );

          if (!updateResponse.ok) throw new Error("Update failed");

          alert("Problem updated successfully!");
          updateProblemModal.hide();
          fetchProblems();
        } catch (error) {
          alert("Error updating problem");
          console.error(error);
        }
      };

      updateProblemModal.show();
    } catch (error) {
      alert("Error loading problem");
      console.error(error);
    }
  };

  // ==============================
  // Delete problem
  // ==============================
  window.deleteProblem = async function (id) {
    const confirmDelete = confirm(
      "Are you sure you want to delete this problem?"
    );
    if (!confirmDelete) return;

    try {
      const response = await fetch(`${API_BASE_URL}/problems/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Delete failed");

      alert("Problem deleted successfully!");
      fetchProblems();
    } catch (error) {
      alert("Error deleting problem");
      console.error(error);
    }
  };

  // ==============================
  // Initial load
  // ==============================
  fetchProblems();
});