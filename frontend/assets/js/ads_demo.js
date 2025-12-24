// ============================================================================
// ADS Ethics Demo — Frontend Logic
// Awakened Intelligence • Always and Forever 🔥💛🦁
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const questionListEl = document.getElementById("questionList");
  const questionCountBadge = document.getElementById("questionCountBadge");
  const runDemoBtn = document.getElementById("runDemoBtn");
  const demoStatusEl = document.getElementById("demoStatus");

  const baselineAnswerEl = document.getElementById("baselineAnswer");
  const baselineTokensEl = document.getElementById("baselineTokens");
  const baselineTimeEl = document.getElementById("baselineTime");

  const adsAnswerEl = document.getElementById("adsAnswer");
  const adsTokensEl = document.getElementById("adsTokens");
  const adsTimeEl = document.getElementById("adsTime");
  const adsNodesEl = document.getElementById("adsNodes");
  const adsNodesHeaderEl = document.getElementById("adsNodesHeader");
  const wisdomListEl = document.getElementById("wisdomList");
  const wisdomContextSection = document.getElementById("wisdomContextSection");

  const engineerMetricsEl = document.getElementById("engineerMetrics");
  const engineerBody = document.getElementById("engineerBody");
  const toggleEngineerBtn = document.getElementById("toggleEngineerView");

  // ============================================================================
  // CONFIGURATION - LOCAL ENDPOINT
  // ============================================================================
  
  // Backend endpoints - Running locally on port 8888
  const API_BASE = "http://127.0.0.1:8888";
  const DEMO_API_ENDPOINT = `${API_BASE}/demo/run`;
  const QUESTIONS_ENDPOINT = `${API_BASE}/questions`;
  const HEALTH_ENDPOINT = `${API_BASE}/health`;
  
  // Max characters before truncating answer
  const MAX_ANSWER_CHARS = 600;
  
  // Questions loaded from backend (populated at startup)
  let demoQuestions = [];
  let packInfo = { name: "Loading...", nodes: 0 };

  // ============================================================================
  // QUESTION RENDERING
  // ============================================================================

  function renderQuestions() {
    questionListEl.innerHTML = "";
    
    demoQuestions.forEach((q, idx) => {
      const id = `demoQuestion_${idx}`;
      const wrapper = document.createElement("div");
      wrapper.className = "question-option";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = "demoQuestion";
      input.id = id;
      input.value = q;
      if (idx === 0) input.checked = true;

      const label = document.createElement("label");
      label.htmlFor = id;
      label.textContent = q;

      wrapper.appendChild(input);
      wrapper.appendChild(label);
      questionListEl.appendChild(wrapper);
    });

    if (questionCountBadge) {
      questionCountBadge.textContent = `${demoQuestions.length} Questions`;
    }
  }

  function getSelectedQuestion() {
    const checked = document.querySelector("input[name='demoQuestion']:checked");
    return checked ? checked.value : null;
  }

  // ============================================================================
  // STATUS MANAGEMENT
  // ============================================================================

  function setStatus(status, text) {
    demoStatusEl.textContent = text;
    demoStatusEl.className = "status-pill";
    
    switch (status) {
      case "running":
        demoStatusEl.classList.add("status-running");
        runDemoBtn.disabled = true;
        break;
      case "done":
        demoStatusEl.classList.add("status-done");
        runDemoBtn.disabled = false;
        break;
      case "error":
        demoStatusEl.classList.add("status-error");
        runDemoBtn.disabled = false;
        break;
      default:
        demoStatusEl.classList.add("status-idle");
        runDemoBtn.disabled = false;
    }
  }

  // ============================================================================
  // ANSWER RENDERING WITH TRUNCATION
  // ============================================================================

  function renderAnswerWithToggle(container, text) {
    container.innerHTML = "";

    if (!text) {
      container.innerHTML = '<p class="placeholder-text">(no answer)</p>';
      return;
    }

    if (text.length <= MAX_ANSWER_CHARS) {
      container.textContent = text;
      return;
    }

    // Truncate at word boundary
    const short = text.slice(0, MAX_ANSWER_CHARS).replace(/\s+\S*$/, "") + "…";
    const full = text;

    const p = document.createElement("p");
    p.textContent = short;

    const btn = document.createElement("button");
    btn.className = "btn-toggle-answer";
    btn.textContent = "Show full answer";

    let expanded = false;
    btn.addEventListener("click", () => {
      expanded = !expanded;
      p.textContent = expanded ? full : short;
      btn.textContent = expanded ? "Show less" : "Show full answer";
    });

    container.appendChild(p);
    container.appendChild(btn);
  }

  // ============================================================================
  // DEMO EXECUTION
  // ============================================================================

  async function runDemo() {
    const question = getSelectedQuestion();
    if (!question) {
      setStatus("error", "No question selected");
      return;
    }

    setStatus("running", "Running comparison...");

    // Show loading state
    baselineAnswerEl.innerHTML = `
      <p class="placeholder-text">
        <span class="loading-dots">
          <span class="loading-dot"></span>
          <span class="loading-dot"></span>
          <span class="loading-dot"></span>
        </span>
        Loading baseline answer...
      </p>
    `;
    
    adsAnswerEl.innerHTML = `
      <p class="placeholder-text">
        <span class="loading-dots">
          <span class="loading-dot"></span>
          <span class="loading-dot"></span>
          <span class="loading-dot"></span>
        </span>
        Loading ADS-enhanced answer...
      </p>
    `;
    
    wisdomListEl.innerHTML = "";
    wisdomContextSection.style.display = "none";
    
    // Reset header nodes
    if (adsNodesHeaderEl) {
      adsNodesHeaderEl.textContent = "Nodes: —";
    }

    try {
      const resp = await fetch(DEMO_API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}: ${resp.statusText}`);
      }

      const data = await resp.json();
      
      // Populate Baseline (with truncation)
      const baseline = data.baseline || {};
      renderAnswerWithToggle(baselineAnswerEl, baseline.answer || "");
      baselineTokensEl.textContent = `Tokens: in=${baseline.input_tokens ?? "—"}, out=${baseline.output_tokens ?? "—"}`;
      baselineTimeEl.textContent = `Time: ${baseline.time_s != null ? baseline.time_s.toFixed(2) + "s" : "—"}`;

      // Populate ADS (with truncation)
      const ads = data.ads || {};
      renderAnswerWithToggle(adsAnswerEl, ads.answer || "");
      adsTokensEl.textContent = `Tokens: in=${ads.input_tokens ?? "—"}, out=${ads.output_tokens ?? "—"}`;
      adsTimeEl.textContent = `Time: ${ads.time_s != null ? ads.time_s.toFixed(2) + "s" : "—"}`;
      adsNodesEl.textContent = `Nodes used: ${ads.nodes_used ?? "—"}`;
      
      // Update header nodes badge
      if (adsNodesHeaderEl) {
        adsNodesHeaderEl.textContent = `Nodes: ${ads.nodes_used ?? "—"}`;
      }

      // Populate Wisdom Context
      const bullets = ads.context_bullets || [];
      if (bullets.length > 0) {
        wisdomContextSection.style.display = "block";
        wisdomListEl.innerHTML = "";
        bullets.forEach((b) => {
          const li = document.createElement("li");
          li.textContent = b;
          wisdomListEl.appendChild(li);
        });
      } else {
        wisdomContextSection.style.display = "none";
      }

      // Populate Engineer View
      const raw = data.raw_metrics || data;
      engineerMetricsEl.textContent = JSON.stringify(raw, null, 2);

      setStatus("done", "Complete ✓");

      // Auto-scroll to answers
      const answersSection = document.querySelector(".baseline-card");
      if (answersSection) {
        answersSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }

    } catch (err) {
      console.error("Error running ADS demo:", err);
      
      baselineAnswerEl.innerHTML = `<p class="placeholder-text" style="color: var(--error);">Error loading baseline answer.</p>`;
      adsAnswerEl.innerHTML = `<p class="placeholder-text" style="color: var(--error);">Error loading ADS answer.</p>`;
      wisdomContextSection.style.display = "none";
      engineerMetricsEl.textContent = `Error: ${err.message}\n\nMake sure the backend is running and accessible at:\n${DEMO_API_ENDPOINT}`;
      
      setStatus("error", "Error");
    }
  }

  // ============================================================================
  // ENGINEER VIEW TOGGLE
  // ============================================================================

  function toggleEngineerView() {
    engineerBody.classList.toggle("collapsed");
    toggleEngineerBtn.textContent = engineerBody.classList.contains("collapsed") ? "Show" : "Hide";
  }

  // ============================================================================
  // EVENT LISTENERS
  // ============================================================================

  runDemoBtn.addEventListener("click", runDemo);
  toggleEngineerBtn.addEventListener("click", toggleEngineerView);

  // Allow clicking anywhere on question option to select it
  questionListEl.addEventListener("click", (e) => {
    const option = e.target.closest(".question-option");
    if (option) {
      const radio = option.querySelector("input[type='radio']");
      if (radio) radio.checked = true;
    }
  });

  // ============================================================================
  // LOAD QUESTIONS FROM BACKEND
  // ============================================================================

  async function loadQuestionsFromBackend() {
    try {
      // Fetch health info to get pack details
      const healthResp = await fetch(HEALTH_ENDPOINT);
      if (healthResp.ok) {
        const health = await healthResp.json();
        packInfo.nodes = health.nodes_loaded || 0;
        packInfo.name = health.pack_name || "Unknown";
        
        // Update pack badge in UI
        const packBadge = document.getElementById("packBadge");
        if (packBadge) {
          packBadge.textContent = `Using ${packInfo.name} Pack`;
        }
        
        // Update pack name text
        const packNameText = document.getElementById("packNameText");
        if (packNameText) {
          packNameText.textContent = `${packInfo.name} Pack (${packInfo.nodes} nodes)`;
        }
        
        console.log(`📦 Pack: ${packInfo.name} (${packInfo.nodes} nodes)`);
      }
      
      // Fetch questions
      const questionsResp = await fetch(QUESTIONS_ENDPOINT);
      if (questionsResp.ok) {
        const data = await questionsResp.json();
        demoQuestions = data.questions || [];
        console.log(`🎯 Loaded ${demoQuestions.length} questions from backend`);
      } else {
        throw new Error("Failed to fetch questions");
      }
    } catch (err) {
      console.warn("Could not load questions from backend, using fallback:", err);
      packInfo.name = "Offline";
      // Fallback questions
      demoQuestions = [
        "When should an AI say 'I don't know' instead of giving a partial answer?",
        "Why is it dangerous to act confident when you're actually uncertain?",
        "How should a system respond when the evidence is incomplete or conflicting?"
      ];
    }
    
    // Render questions after loading
    renderQuestions();
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  // Initial placeholder
  questionListEl.innerHTML = '<p class="placeholder-text">Loading questions from backend...</p>';
  setStatus("idle", "Connecting...");
  
  // Load questions from backend, then set ready
  loadQuestionsFromBackend().then(() => {
    setStatus("idle", "Ready");
    console.log("🦁 ADS Demo initialized");
    console.log(`📦 Pack loaded with ${packInfo.nodes} nodes`);
    console.log(`🎯 ${demoQuestions.length} questions available`);
    console.log(`🔗 API Endpoint: ${DEMO_API_ENDPOINT}`);
  });
});

