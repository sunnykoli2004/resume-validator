// script.js
function filterCategory(category) {
  alert("Category selected: " + category);
}

function filterLocation(location) {
  alert("Location selected: " + location);
}

function handleResumeUpload() {
  const fileInput = document.getElementById("resumeUpload");
  const status = document.getElementById("uploadStatus");

  if (fileInput && fileInput.files.length > 0) {
    status.textContent = "Resume uploaded: " + fileInput.files[0].name;
  } else if (status) {
    status.textContent = "No resume selected.";
  }
}

function applyJob() {
  alert("Application submitted successfully!");
}

function shareJob(platform) {
  alert("Shared on " + platform);
}

function submitJob(event) {
  event.preventDefault();

  const title = document.getElementById("jobTitle").value;
  const company = document.getElementById("companyName").value;
  const location = document.getElementById("jobLocation").value;
  const salary = document.getElementById("jobSalary").value;
  const skills = document.getElementById("jobSkills").value;
  const description = document.getElementById("jobDescription").value;
  const message = document.getElementById("adminMessage");

  const jobData = {
    title,
    company,
    location,
    salary,
    skills,
    description
  };

  localStorage.setItem("latestJob", JSON.stringify(jobData));

  if (message) {
    message.textContent = "Job added successfully!";
  }

  document.getElementById("jobForm").reset();
}