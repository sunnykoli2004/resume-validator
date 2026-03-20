// api.js — connects frontend to scraper and resume backend

const SCRAPER_URL = "http://127.0.0.1:8000/jobs";
const BACKEND_URL = "http://127.0.0.1:8001/generate_resume/";

// ----------------------------------------
// FETCH LIVE JOBS FROM SCRAPER
// ----------------------------------------
// ----------------------------------------
// FETCH LIVE JOBS FROM SCRAPER
// ----------------------------------------
async function loadLiveJobs(jobRole, location) {
  const container = document.getElementById("liveJobsContainer");
  const staticJobs = document.getElementById("staticJobs");
  
  if (!container) return;

  // 1. Show loading state & hide static samples
  container.innerHTML = `<p style="color:#5a3df0; padding:20px 0; font-weight:bold; text-align:center;">⏳ Scraping live jobs for "${jobRole}" in "${location}"...</p>`;
  if (staticJobs) staticJobs.style.display = "none";

  try {
    // 2. Fetch from your Scraper (Port 8000)
    // We send the role and location exactly as typed in your HTML inputs
    const response = await fetch(`http://127.0.0.1:8000/jobs?job_title=${encodeURIComponent(jobRole)}&location=${encodeURIComponent(location)}&limit=10`);
    
    if (!response.ok) throw new Error("Scraper is not responding. Check Terminal 1.");

    const data = await response.json();
    const jobs = data.jobs || [];

    // 3. Handle case where no jobs are found
    if (jobs.length === 0) {
      container.innerHTML = `<p style="color:#ef4444; text-align:center; padding:20px;">No live jobs found for "${jobRole}". Try a broader search.</p>`;
      if (staticJobs) staticJobs.style.display = "block";
      return;
    }

    // 4. Clear the loading message
    container.innerHTML = ""; 

    // 5. Loop through the jobs and create HTML cards
    jobs.forEach((job) => {
      const cardLink = document.createElement("a");
      cardLink.href = "job.html";
      cardLink.className = "job-card-link";
      
      // Save the specific job data to localStorage so job.html can display it
      cardLink.onclick = () => {
        localStorage.setItem("selectedJob", JSON.stringify(job));
      };

      // Build the card using the exact classes from your index.html
      cardLink.innerHTML = `
        <article class="job-card horizontal-card" style="margin-bottom: 20px;">
          <div class="job-logo" style="background:#5a3df0; color:white;">
            ${(job.company || "J")[0].toUpperCase()}
          </div>
          <div class="job-main-info">
            <div class="job-top-row">
              <div>
                <h3>${job.title || "Untitled Role"}</h3>
                <p class="company-name">${job.company || "Company Confidential"}</p>
              </div>
              <div class="job-salary" style="color: #16a34a; font-weight: bold;">
                ${job.min_amount ? `₹${job.min_amount.toLocaleString()} - ₹${job.max_amount.toLocaleString()}` : "Salary not listed"}
              </div>
            </div>
            <div class="job-meta">
              <span>📍 ${job.location || location}</span>
              <span>🕒 ${job.job_type || "Full Time"}</span>
              <span>🌐 ${job.site || "Live Search"}</span>
            </div>
            <p class="job-desc">${(job.description || "No description available. Click to view details.").slice(0, 160)}...</p>
          </div>
        </article>
      `;

      container.appendChild(cardLink);
    });

  } catch (err) {
    console.error("Fetch Error:", err);
    container.innerHTML = `<p style="color:#ef4444; text-align:center; padding:20px;">❌ Error: ${err.message}. Make sure your Scraper is running on Port 8000.</p>`;
    if (staticJobs) staticJobs.style.display = "block";
  }
}
function saveSelectedJob(job) {
  localStorage.setItem("selectedJob", JSON.stringify(job));
}


// ----------------------------------------
// LOAD JOB DETAILS ON job.html
// ----------------------------------------
function loadJobDetails() {
  const job = JSON.parse(localStorage.getItem("selectedJob"));
  if (!job) return;

  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val || "";
  };

  set("jobDetailTitle", job.title);
  set("jobDetailCompany", job.company);
  set("jobDetailLocation", job.location);
  set("jobDetailType", job.job_type || "Full Time");
  set("jobDetailSite", job.site || "Indeed");
  set("jobDetailDate", job.date_posted || "Recent");
  set("jobDetailSalary",
    job.min_amount && job.max_amount
      ? `$${Number(job.min_amount).toLocaleString()} - $${Number(job.max_amount).toLocaleString()}`
      : "Not specified"
  );
  set("jobDetailDescription", job.description || "No description available.");
  set("jobDetailSummary", (job.description || "").slice(0, 200) + "...");

  const logoEl = document.getElementById("jobDetailLogo");
  if (logoEl) logoEl.textContent = (job.company || "?")[0].toUpperCase();
}


// ----------------------------------------
// ANALYZE RESUME AGAINST JOB
// ----------------------------------------
async function analyzeResume() {
  const fileInput = document.getElementById("resumeUpload");
  const status = document.getElementById("uploadStatus");
  const resultsSection = document.getElementById("matchResults");

  if (!fileInput || fileInput.files.length === 0) {
    status.textContent = "Please upload your resume first.";
    status.style.color = "red";
    return;
  }

  const job = JSON.parse(localStorage.getItem("selectedJob"));
  if (!job || !job.description) {
    status.textContent = "Job description not found. Please go back and select a job.";
    status.style.color = "red";
    return;
  }

  status.textContent = "⏳ Analyzing your resume... this may take a moment.";
  status.style.color = "#5a3df0";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("job_description", job.description);

  try {
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.error) {
      status.textContent = "Error: " + result.error;
      status.style.color = "red";
      return;
    }

    status.textContent = "✅ Analysis complete!";
    status.style.color = "green";

    displayMatchResults(result, resultsSection);

  } catch (err) {
    status.textContent = "❌ Could not connect to backend. Make sure it is running on port 8001.";
    status.style.color = "red";
    console.error(err);
  }
}


// ----------------------------------------
// DISPLAY MATCH RESULTS
// ----------------------------------------
function displayMatchResults(result, section) {
  if (!section) return;

  const score = result.match_percentage || 0;
  const color = score >= 80 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
  const label = score >= 80 ? "Strong Match ✅" : score >= 50 ? "Moderate Match ⚠️" : "Low Match ❌";

  const missingSkills = (result.missing_skills || [])
    .map(s => `<span style="background:#fef2f2;color:#ef4444;padding:6px 12px;border-radius:20px;font-size:13px;font-weight:600;display:inline-block;margin:4px;">${s}</span>`)
    .join("");

  const resumeSkills = (result.resume_skills || [])
    .map(s => `<span style="background:#f0fdf4;color:#16a34a;padding:6px 12px;border-radius:20px;font-size:13px;font-weight:600;display:inline-block;margin:4px;">${s}</span>`)
    .join("");

  const courses = result.recommended_courses || {};
  const courseLinks = Object.entries(courses)
    .slice(0, 5)
    .map(([skill, url]) => `<a href="${url}" target="_blank" style="display:block;color:#5a3df0;margin-bottom:8px;font-weight:600;">📚 Learn ${skill}</a>`)
    .join("");

  section.style.display = "block";
  section.innerHTML = `
    <div style="background:#fff;border:1px solid #dfe3f4;border-radius:20px;padding:28px;margin-top:24px;">
      <h2 style="margin-top:0;color:#1d1d1d;">Resume Analysis Results</h2>
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;padding:20px;background:#f8f9ff;border-radius:16px;">
        <div style="font-size:52px;font-weight:bold;color:${color};">${score}%</div>
        <div>
          <div style="font-size:20px;font-weight:700;color:${color};">${label}</div>
          <div style="color:#666;font-size:14px;margin-top:4px;">Match score between your resume and this job description</div>
        </div>
      </div>
      <h3 style="color:#1d1d1d;">✅ Your Skills Found</h3>
      <div style="margin-bottom:20px;">${resumeSkills || "<p style='color:#888'>No matching skills detected</p>"}</div>
      <h3 style="color:#1d1d1d;">❌ Missing Skills</h3>
      <div style="margin-bottom:20px;">${missingSkills || "<p style='color:#22c55e;font-weight:600;'>Great! No missing skills found.</p>"}</div>
      ${courseLinks ? `
        <h3 style="color:#1d1d1d;">📚 Recommended Courses</h3>
        <div style="margin-bottom:20px;">${courseLinks}</div>
      ` : ""}
      ${result.download_resume ? `
        <a href="http://127.0.0.1:8001/download_resume/?path=${encodeURIComponent(result.download_resume)}"
           style="display:inline-block;background:#5a3df0;color:#fff;padding:12px 24px;border-radius:12px;text-decoration:none;font-weight:600;margin-top:8px;">
          ⬇️ Download Improved Resume
        </a>
      ` : ""}
    </div>
  `;
}


// ----------------------------------------
// SEARCH HANDLER
// ----------------------------------------
// --- SEARCH HANDLER (Fixes the "Nothing Happening" bug) ---
function searchJobs(event) {
  // Prevent page refresh if button is inside a form
  if (event) event.preventDefault(); 

  // 1. Match your HTML IDs exactly
  const roleInput = document.getElementById("searchRole");
  const locationInput = document.getElementById("searchLocation");

  // 2. Check if the inputs exist in the HTML
  if (!roleInput || !locationInput) {
    console.error("Missing IDs: Make sure your HTML has id='searchRole' and id='searchLocation'");
    return;
  }

  const role = roleInput.value.trim();
  const location = locationInput.value.trim();

  // 3. Simple Validation
  if (!role || !location) {
    alert("Please enter both a job role and a location.");
    return;
  }

  console.log("Button clicked! Fetching jobs for:", role, "in", location);

  // 4. Start the scraper flow
  loadLiveJobs(role, location);
}


// ----------------------------------------
// AUTO INIT
// ----------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const page = window.location.pathname;
  if (page.includes("job.html")) {
    loadJobDetails();
  }
});