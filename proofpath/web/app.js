let currentCaseData = null;
let graphAnimationId = null;

// File Selection Handler
function handleFileSelection(input) {
  const fileList = document.getElementById("fileList");
  if (input.files && input.files.length > 0) {
    const names = Array.from(input.files).map(f => f.name).join(", ");
    fileList.textContent = `Selected (${input.files.length}): ${names}`;
  } else {
    fileList.textContent = "";
  }
}

// Drag & Drop
const dropzone = document.getElementById("dropzone");
if (dropzone) {
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "var(--primary)";
    }, false);
  });
  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "var(--border-color)";
    }, false);
  });
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    document.getElementById("fileInput").files = files;
    handleFileSelection(document.getElementById("fileInput"));
  }, false);
}

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));
  
  const targetContent = document.getElementById(tabId);
  if (targetContent) targetContent.classList.add("active");

  const btnMap = {
    'tabOverview': 0, 'tabTimeline': 1, 'tabGraph': 2, 'tabEvidence': 3,
    'tabRoadmap': 4, 'tabComplaints': 5, 'tabDownloads': 6, 'tabBenchmark': 7
  };
  const btns = document.querySelectorAll(".tab-btn");
  if (btns[btnMap[tabId]]) btns[btnMap[tabId]].classList.add("active");

  if (tabId === "tabGraph") {
    setTimeout(renderGraph, 100);
  }
}

// Form Submission
document.getElementById("evidenceForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please select or drop at least one evidence file, or choose a preloaded demo case.");
    return;
  }

  const formData = new FormData();
  formData.append("jurisdiction", document.getElementById("jurisdictionSelect").value);
  formData.append("victim_name", document.getElementById("victimName").value);
  formData.append("victim_contact", document.getElementById("victimContact").value);

  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append("files", fileInput.files[i]);
  }

  await executeCaseAnalysis(formData);
});

async function executeCaseAnalysis(formData) {
  const spinner = document.getElementById("loadingSpinner");
  const submitBtn = document.getElementById("submitBtn");
  spinner.style.display = "inline";
  submitBtn.disabled = true;

  try {
    const res = await fetch("/api/cases/analyze", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}: ${await res.text()}`);
    }
    const data = await res.json();
    currentCaseData = data;
    renderResults(data);
  } catch (err) {
    alert("Analysis error: " + err.message);
  } finally {
    spinner.style.display = "none";
    submitBtn.disabled = false;
  }
}

// Render Results to UI
function renderResults(data) {
  document.getElementById("resultsSection").style.display = "block";
  document.getElementById("resultsSection").scrollIntoView({ behavior: "smooth" });

  // Stats Grid
  document.getElementById("statLoss").textContent = `${data.total_loss_currency} ${Number(data.total_loss_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  document.getElementById("statRisk").textContent = `${data.risk_assessment.risk_level} (${Math.round(data.risk_assessment.risk_score)}/100)`;
  document.getElementById("statPattern").textContent = data.risk_assessment.primary_scam_pattern;
  document.getElementById("statSyndicate").textContent = data.syndicate_matches.length > 0
    ? `${data.syndicate_matches.length} Syndicate Match (${data.syndicate_matches[0].known_alias})`
    : "No Cataloged Match";

  // Summary
  document.getElementById("summaryText").textContent = data.summary;

  // Contradictions
  const contraDiv = document.getElementById("contradictionsList");
  contraDiv.innerHTML = "";
  if (data.risk_assessment.contradictions && data.risk_assessment.contradictions.length > 0) {
    data.risk_assessment.contradictions.forEach(c => {
      const item = document.createElement("div");
      item.className = "contradiction-item";
      item.innerHTML = `
        <h4>[${c.severity}] ${c.title}</h4>
        <p>${c.description}</p>
        <span style="font-size: 11px; color: var(--text-muted);">Sources: ${c.evidence_item_a} ${c.evidence_item_b ? ' / ' + c.evidence_item_b : ''}</span>
      `;
      contraDiv.appendChild(item);
    });
  } else {
    contraDiv.innerHTML = "<p style='font-size: 13px; color: #94a3b8;'>No cross-document contradictions detected.</p>";
  }

  // Red Flags
  const redFlagsList = document.getElementById("redFlagsList");
  redFlagsList.innerHTML = "";
  (data.risk_assessment.red_flags || []).forEach(rf => {
    const li = document.createElement("li");
    li.textContent = rf;
    redFlagsList.appendChild(li);
  });

  // Timeline
  const timelineDiv = document.getElementById("timelineContainer");
  timelineDiv.innerHTML = "";
  (data.chronology || []).forEach(ev => {
    const evDiv = document.createElement("div");
    evDiv.className = "timeline-event";
    evDiv.innerHTML = `
      <div class="timeline-time">${ev.timestamp || 'Recorded Sequence #' + ev.sequence_number} &bull; ${ev.event_type}</div>
      <div class="timeline-desc">${ev.description}</div>
      <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px;">Sources: ${ev.evidence_sources.join(', ')}</div>
    `;
    timelineDiv.appendChild(evDiv);
  });

  // Evidence Table
  const tableBody = document.getElementById("evidenceTableBody");
  tableBody.innerHTML = "";
  (data.evidence_items || []).forEach((it, idx) => {
    const letter = String.fromCharCode(65 + idx);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><b>Exhibit ${letter}</b></td>
      <td><code>${it.filename}</code></td>
      <td>${it.evidence_type}</td>
      <td><code>${it.sha256_hash.substring(0, 16)}...</code></td>
      <td><span class="badge badge-risk-medium">VERIFIED</span></td>
    `;
    tableBody.appendChild(row);
  });

  // Roadmap
  const roadmapDiv = document.getElementById("roadmapList");
  roadmapDiv.innerHTML = "";
  (data.procedural_roadmap || []).forEach(s => {
    const card = document.createElement("div");
    card.className = "content-card";
    card.style.borderLeft = "4px solid var(--primary)";
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="font-weight:700; font-size:14px; color:#60a5fa;">Step ${s.step_number}: ${s.authority_name}</span>
        <span class="badge badge-risk-high">${s.timeline_window}</span>
      </div>
      <p style="font-size:12px; color:var(--text-muted); margin-bottom:6px;"><b>Desk / Contact:</b> ${s.contact_channel}</p>
      <p style="font-size:12px; color:#cbd5e1; margin-bottom:6px;"><b>Statutory Basis:</b> <i>${s.statutory_reference}</i></p>
      <p style="font-size:13px; color:var(--text-main); margin-bottom:8px;">${s.instructions}</p>
      <p style="font-size:11.5px; color:var(--cyan);"><b>Mandatory Exhibits:</b> ${s.required_evidence.join(', ')}</p>
    `;
    roadmapDiv.appendChild(card);
  });

  // Complaints
  const compDiv = document.getElementById("complaintsContainer");
  compDiv.innerHTML = "";
  (data.complaint_drafts || []).forEach((c, idx) => {
    const card = document.createElement("div");
    card.className = "content-card";
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <span style="font-weight:600; font-size:14px;">Authority: ${c.target_authority}</span>
        <button class="btn-secondary" onclick="copyComplaintText(${idx})">📋 Copy Formal Application</button>
      </div>
      <p style="font-size:12px; color:var(--text-muted); margin-bottom:8px;"><b>Subject:</b> ${c.subject}</p>
      <div class="complaint-box" id="complaintBox_${idx}">${c.body}</div>
    `;
    compDiv.appendChild(card);
  });

  // Download Links & In-Browser PDF Preview
  document.getElementById("btnDownloadPdf").href = `/api/cases/${data.case_id}/pdf`;
  document.getElementById("btnDownloadZip").href = `/api/cases/${data.case_id}/zip`;
  const pdfIframe = document.getElementById("pdfPreviewIframe");
  if (pdfIframe) {
    pdfIframe.src = `/api/cases/${data.case_id}/pdf`;
    const previewStatus = document.getElementById("pdfPreviewStatus");
    if (previewStatus) {
      previewStatus.textContent = `Case Dossier: ${data.case_id} • Loaded`;
    }
  }
}

// Copy to Clipboard
function copyComplaintText(idx) {
  const box = document.getElementById(`complaintBox_${idx}`);
  if (box) {
    navigator.clipboard.writeText(box.textContent);
    alert("Complaint application text copied to clipboard!");
  }
}

// Interactive Network Graph Canvas State & Engine
const graphState = {
  nodes: [],
  edges: [],
  nodeMap: new Map(),
  draggingNode: null,
  hoveredNode: null,
  selectedNode: null,
  dragOffsetX: 0,
  dragOffsetY: 0,
  listenersAttached: false,
};

async function renderGraph() {
  const canvas = document.getElementById("graphCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const containerW = canvas.parentElement ? canvas.parentElement.clientWidth : 700;
  canvas.width = Math.max(640, containerW - 40);
  canvas.height = 480;

  let graphData = null;
  try {
    const res = await fetch("/api/intelligence/graph");
    graphData = await res.json();
  } catch (err) {
    console.error("Failed to fetch graph data", err);
    return;
  }

  const newNodes = graphData.nodes || [];
  const newEdges = graphData.edges || [];

  // Preserve existing node positions if already laid out
  const oldPosMap = new Map();
  graphState.nodes.forEach(n => oldPosMap.set(n.id, { x: n.x, y: n.y }));

  const width = canvas.width;
  const height = canvas.height;
  const centerX = width / 2;
  const centerY = height / 2;

  // Concentric ring layout: syndicates at center, cases in mid ring, indicators in outer ring
  const syndicates = newNodes.filter(n => n.type === 'syndicate');
  const cases = newNodes.filter(n => n.type === 'case');
  const indicators = newNodes.filter(n => n.type !== 'syndicate' && n.type !== 'case');

  syndicates.forEach((n, idx) => {
    const old = oldPosMap.get(n.id);
    if (old) { n.x = old.x; n.y = old.y; }
    else {
      const angle = (idx / Math.max(syndicates.length, 1)) * 2 * Math.PI;
      const r = syndicates.length > 1 ? 70 : 0;
      n.x = centerX + r * Math.cos(angle);
      n.y = centerY + r * Math.sin(angle);
    }
    n.radius = 14;
  });

  cases.forEach((n, idx) => {
    const old = oldPosMap.get(n.id);
    if (old) { n.x = old.x; n.y = old.y; }
    else {
      const angle = (idx / Math.max(cases.length, 1)) * 2 * Math.PI + 0.3;
      n.x = centerX + 150 * Math.cos(angle);
      n.y = centerY + 130 * Math.sin(angle);
    }
    n.radius = 10;
  });

  indicators.forEach((n, idx) => {
    const old = oldPosMap.get(n.id);
    if (old) { n.x = old.x; n.y = old.y; }
    else {
      const angle = (idx / Math.max(indicators.length, 1)) * 2 * Math.PI + 0.6;
      n.x = centerX + 230 * Math.cos(angle);
      n.y = centerY + 190 * Math.sin(angle);
    }
    n.radius = 8;
  });

  graphState.nodes = newNodes;
  graphState.edges = newEdges;
  graphState.nodeMap.clear();
  newNodes.forEach(n => graphState.nodeMap.set(n.id, n));

  // Attach interactive mouse listeners once
  if (!graphState.listenersAttached) {
    attachGraphCanvasListeners(canvas);
    graphState.listenersAttached = true;
  }

  drawGraphFrame(ctx, canvas);
}

function attachGraphCanvasListeners(canvas) {
  const getMousePos = (e) => {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) * (canvas.width / rect.width),
      y: (e.clientY - rect.top) * (canvas.height / rect.height),
    };
  };

  const findNodeAt = (pos) => {
    for (let i = graphState.nodes.length - 1; i >= 0; i--) {
      const n = graphState.nodes[i];
      const dx = n.x - pos.x;
      const dy = n.y - pos.y;
      if (Math.sqrt(dx * dx + dy * dy) <= (n.radius + 6)) {
        return n;
      }
    }
    return null;
  };

  canvas.addEventListener("mousedown", (e) => {
    const pos = getMousePos(e);
    const hit = findNodeAt(pos);
    if (hit) {
      graphState.draggingNode = hit;
      graphState.selectedNode = hit;
      graphState.dragOffsetX = hit.x - pos.x;
      graphState.dragOffsetY = hit.y - pos.y;
      canvas.style.cursor = "grabbing";
    } else {
      graphState.selectedNode = null;
    }
    drawGraphFrame(canvas.getContext("2d"), canvas);
  });

  canvas.addEventListener("mousemove", (e) => {
    const pos = getMousePos(e);
    if (graphState.draggingNode) {
      graphState.draggingNode.x = Math.max(20, Math.min(canvas.width - 20, pos.x + graphState.dragOffsetX));
      graphState.draggingNode.y = Math.max(20, Math.min(canvas.height - 20, pos.y + graphState.dragOffsetY));
      drawGraphFrame(canvas.getContext("2d"), canvas);
    } else {
      const hit = findNodeAt(pos);
      if (hit !== graphState.hoveredNode) {
        graphState.hoveredNode = hit;
        canvas.style.cursor = hit ? "pointer" : "default";
        drawGraphFrame(canvas.getContext("2d"), canvas);
      }
    }
  });

  window.addEventListener("mouseup", () => {
    if (graphState.draggingNode) {
      graphState.draggingNode = null;
      canvas.style.cursor = "default";
      drawGraphFrame(canvas.getContext("2d"), canvas);
    }
  });

  canvas.addEventListener("mouseleave", () => {
    graphState.hoveredNode = null;
    if (!graphState.draggingNode) {
      drawGraphFrame(canvas.getContext("2d"), canvas);
    }
  });
}

function drawGraphFrame(ctx, canvas) {
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  // Background subtle grid
  ctx.strokeStyle = "rgba(30, 41, 59, 0.4)";
  ctx.lineWidth = 1;
  const gridSize = 40;
  for (let x = 0; x < width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  for (let y = 0; y < height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  const activeFocus = graphState.selectedNode || graphState.hoveredNode;
  const connectedNodeIds = new Set();
  if (activeFocus) {
    connectedNodeIds.add(activeFocus.id);
    graphState.edges.forEach(e => {
      if (e.source === activeFocus.id) connectedNodeIds.add(e.target);
      if (e.target === activeFocus.id) connectedNodeIds.add(e.source);
    });
  }

  // Draw edges
  graphState.edges.forEach(e => {
    const u = graphState.nodeMap.get(e.source);
    const v = graphState.nodeMap.get(e.target);
    if (!u || !v) return;

    const isConnected = activeFocus && (
      (e.source === activeFocus.id && connectedNodeIds.has(e.target)) ||
      (e.target === activeFocus.id && connectedNodeIds.has(e.source))
    );

    ctx.beginPath();
    ctx.moveTo(u.x, u.y);
    ctx.lineTo(v.x, v.y);

    if (isConnected) {
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 2.5;
    } else if (activeFocus) {
      ctx.strokeStyle = "rgba(71, 85, 105, 0.15)";
      ctx.lineWidth = 0.8;
    } else {
      ctx.strokeStyle = "rgba(100, 116, 139, 0.45)";
      ctx.lineWidth = 1.2;
    }
    ctx.stroke();
  });

  // Draw nodes
  graphState.nodes.forEach(n => {
    const isFocused = activeFocus && (n.id === activeFocus.id);
    const isNeighbor = activeFocus && connectedNodeIds.has(n.id) && !isFocused;

    ctx.beginPath();
    const r = n.radius || (n.type === 'syndicate' ? 14 : (n.type === 'case' ? 10 : 8));
    ctx.arc(n.x, n.y, isFocused ? r + 3 : r, 0, 2 * Math.PI);

    ctx.fillStyle = n.color || "#3b82f6";
    ctx.fill();

    // Halo / stroke
    if (isFocused) {
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 3.5;
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 7, 0, 2 * Math.PI);
      ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
      ctx.lineWidth = 2;
      ctx.stroke();
    } else if (isNeighbor) {
      ctx.strokeStyle = "#fef08a";
      ctx.lineWidth = 2;
      ctx.stroke();
    } else {
      ctx.strokeStyle = "#0f172a";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // Node label
    ctx.font = isFocused ? "bold 11px sans-serif" : "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillStyle = isFocused ? "#38bdf8" : (isNeighbor ? "#fef08a" : "#cbd5e1");
    const displayLabel = n.label.length > 22 ? n.label.substring(0, 20) + "…" : n.label;
    ctx.fillText(displayLabel, n.x, n.y + r + 13);
  });

  // Floating HUD Tooltip on hover or selection
  if (activeFocus) {
    const tip = activeFocus;
    const padding = 10;
    const lines = [
      `Entity: ${tip.label}`,
      `Type: ${tip.type.toUpperCase()} | Degree: ${tip.degree || 'N/A'}`,
      `ID: ${tip.id}`,
    ];
    if (tip.metadata && tip.metadata.loss) {
      lines.push(`Reported Loss: ${tip.metadata.loss}`);
    }

    ctx.font = "11px monospace";
    const maxLineW = Math.max(...lines.map(l => ctx.measureText(l).width));
    const boxW = maxLineW + padding * 2;
    const boxH = lines.length * 16 + padding * 2;

    let tipX = tip.x + 18;
    let tipY = tip.y - boxH - 10;
    if (tipX + boxW > width - 10) tipX = tip.x - boxW - 14;
    if (tipY < 10) tipY = tip.y + 18;

    // Background card
    ctx.fillStyle = "rgba(15, 23, 42, 0.92)";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(tipX, tipY, boxW, boxH, 6) : ctx.rect(tipX, tipY, boxW, boxH);
    ctx.fill();
    ctx.stroke();

    // Text lines
    lines.forEach((l, idx) => {
      ctx.fillStyle = idx === 0 ? "#38bdf8" : "#e2e8f0";
      ctx.textAlign = "left";
      ctx.fillText(l, tipX + padding, tipY + padding + 12 + idx * 16);
    });
  }
}

// Preloaded Demos
async function loadDemoCase(type) {
  const formData = new FormData();
  if (type === 'BD') {
    document.getElementById("jurisdictionSelect").value = "BANGLADESH";
    document.getElementById("victimName").value = "Tanvir Hasan";
    document.getElementById("victimContact").value = "+8801712000000";

    formData.append("jurisdiction", "BANGLADESH");
    formData.append("victim_name", "Tanvir Hasan");
    formData.append("victim_contact", "+8801712000000");

    let loadedBinary = false;
    try {
      const [chatRes, receiptRes] = await Promise.all([
        fetch("/samples/whatsapp_threat_chat.png"),
        fetch("/samples/bkash_transfer_slip.png"),
      ]);
      if (chatRes.ok && receiptRes.ok) {
        const chatBlob = await chatRes.blob();
        const receiptBlob = await receiptRes.blob();
        formData.append("files", chatBlob, "whatsapp_threat_chat.png");
        formData.append("files", receiptBlob, "bkash_transfer_slip.png");
        loadedBinary = true;
      }
    } catch (err) {
      console.warn("Could not fetch binary sample files, falling back to synthetic text", err);
    }

    if (!loadedBinary) {
      const chatContent = (
        "Suspect: We are calling from Bangladesh Bank Fraud Monitoring Cell. " +
        "Immediate action required! Your bKash account is linked to suspicious gambling transactions. " +
        "Account will be locked within 30 min unless verified. " +
        "Send emergency clearance fee of BDT 25,000 to verification desk at 01719998877 immediately. " +
        "Time: 2026-10-12 11:30:00"
      );
      const receiptContent = (
        "bKash Transaction Slip\n" +
        "TrxID: BL9A2K9Z9X\n" +
        "Amount: BDT 25,000.00\n" +
        "To: 01719998877\n" +
        "Date: 2026-10-12 11:45:00\n" +
        "Status: Successful"
      );
      formData.append("files", new Blob([chatContent], {type: "text/plain"}), "threat_chat_whatsapp.txt");
      formData.append("files", new Blob([receiptContent], {type: "text/plain"}), "bkash_receipt_slip.txt");
    }
  } else if (type === 'SG') {
    document.getElementById("jurisdictionSelect").value = "SINGAPORE";
    document.getElementById("victimName").value = "Rachel Lim";
    document.getElementById("victimContact").value = "+6598760000";

    formData.append("jurisdiction", "SINGAPORE");
    formData.append("victim_name", "Rachel Lim");
    formData.append("victim_contact", "+6598760000");

    let loadedBinary = false;
    try {
      const [chatRes, receiptRes, offerRes] = await Promise.all([
        fetch("/samples/telegram_task_scam.png"),
        fetch("/samples/paynow_transfer_slip.png"),
        fetch("/samples/fake_employment_offer.pdf"),
      ]);
      if (chatRes.ok && receiptRes.ok && offerRes.ok) {
        const chatBlob = await chatRes.blob();
        const receiptBlob = await receiptRes.blob();
        const offerBlob = await offerRes.blob();
        formData.append("files", chatBlob, "telegram_task_scam.png");
        formData.append("files", receiptBlob, "paynow_transfer_slip.png");
        formData.append("files", offerBlob, "fake_employment_offer.pdf");
        loadedBinary = true;
      }
    } catch (err) {
      console.warn("Could not fetch binary sample files, falling back to synthetic text", err);
    }

    if (!loadedBinary) {
      const chatContent = (
        "[Telegram @recruit_vip_elena]\n" +
        "Elena: Hi Rachel! Shopee VIP Affiliate Task Opportunity. " +
        "Earn daily commission rebate 20% on product review tasks. " +
        "Deposit SGD 1,500 to unlock vip level.\n" +
        "PayNow to mobile +6591234567.\n" +
        "Portal: http://sg-shopee-rebates.top/login\n" +
        "Timestamp: 2026-10-11 14:00:00"
      );
      const receiptContent = (
        "PayNow Transfer Confirmation\n" +
        "Reference Number: FAST202610119882\n" +
        "Amount: SGD 1,500.00\n" +
        "To Mobile: +6591234567\n" +
        "Date: 2026-10-11 14:15:00\n" +
        "Status: Completed"
      );
      formData.append("files", new Blob([chatContent], {type: "text/plain"}), "telegram_job_offer.txt");
      formData.append("files", new Blob([receiptContent], {type: "text/plain"}), "paynow_transfer_slip.txt");
    }
  } else {
    // Backdated anomaly case
    document.getElementById("jurisdictionSelect").value = "BANGLADESH";
    const chatContent = "Customs Officer: DHL courier parcel held at airport clearance. Pay BDT 8000 fee. Contact: 2026-10-15 12:00:00";
    const receiptContent = "Payment Slip\nTxn ID: ANOMALY99\nAmount: BDT 8000\nTo: 01822334455\nDate: 2026-10-10 09:00:00"; // Backdated
    formData.append("jurisdiction", "BANGLADESH");
    formData.append("victim_name", "Imran Khan");
    formData.append("victim_contact", "+8801711223344");
    formData.append("files", new Blob([chatContent], {type: "text/plain"}), "customs_notice.txt");
    formData.append("files", new Blob([receiptContent], {type: "text/plain"}), "backdated_receipt.txt");
  }

  await executeCaseAnalysis(formData);
}

// Benchmark Runner
async function triggerBenchmark() {
  const btn = document.getElementById("btnRunBenchmark");
  const outDiv = document.getElementById("benchmarkOutput");
  btn.disabled = true;
  btn.textContent = "⏳ Executing Quantitative Benchmark Suite...";
  outDiv.style.display = "block";
  outDiv.innerHTML = "<p style='color:var(--cyan);'>Running multi-scenario test suite across extraction, contradiction detection, and syndicate matching...</p>";

  try {
    const res = await fetch("/api/benchmark/run");
    const rep = await res.json();
    outDiv.innerHTML = `
      <div style="background:#090d16; border:1px solid var(--border-color); border-radius:8px; padding:16px;">
        <h4 style="color:#60a5fa; margin-bottom:12px; font-size:16px;">🏆 Fraud-Response Evaluation Scorecard</h4>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:16px;">
          <div><b>Overall Composite Score:</b> <span style="color:#10b981; font-size:18px; font-weight:700;">${rep.overall_benchmark_score}%</span></div>
          <div><b>Extraction Accuracy:</b> ${rep.extraction_accuracy}%</div>
          <div><b>Consistency & Anomalies:</b> ${rep.consistency_detection_score}%</div>
          <div><b>Pattern Detection:</b> ${rep.pattern_detection_score}%</div>
          <div><b>Statutory Adherence:</b> ${rep.procedural_quality_score}%</div>
          <div><b>Syndicate Precision:</b> ${rep.syndicate_match_score}%</div>
        </div>
        <table class="data-table">
          <thead>
            <tr><th>Scenario</th><th>Status</th><th>Verification Checks</th></tr>
          </thead>
          <tbody>
            ${rep.case_details.map(c => `
              <tr>
                <td><b>${c.case_name}</b></td>
                <td><span class="badge ${c.passed ? 'badge-risk-medium' : 'badge-risk-critical'}">${c.passed ? 'PASSED' : 'FAILED'}</span></td>
                <td><code>${JSON.stringify(c.checks)}</code></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    outDiv.innerHTML = `<p style="color:var(--danger);">Benchmark failed: ${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Run Benchmark Suite Again";
  }
}

// Live API Health & Latency Poller
async function pollApiHealth() {
  const badge = document.getElementById("apiStatusBadge");
  if (!badge) return;
  const t0 = performance.now();
  try {
    const res = await fetch("/api/health");
    const latency = Math.round(performance.now() - t0);
    if (res.ok) {
      const data = await res.json();
      const engineMode = data.genai_sdk_available ? "Vertex AI / GenAI (Online)" : "Fallback Mode";
      badge.className = "badge badge-risk-medium";
      badge.style.background = "#064e3b";
      badge.style.color = "#34d399";
      badge.style.border = "1px solid #059669";
      badge.textContent = `API: ONLINE (${latency}ms) | Engine: ${engineMode}`;
    } else {
      badge.className = "badge badge-risk-critical";
      badge.textContent = `API: ERROR ${res.status}`;
    }
  } catch (err) {
    badge.className = "badge badge-risk-critical";
    badge.textContent = "API: OFFLINE";
  }
}

// Initial health check and periodic polling
if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", () => {
    pollApiHealth();
    setInterval(pollApiHealth, 10000);
  });
  pollApiHealth();
}
