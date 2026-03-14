/* ============================================
   ALIANZA SEARCH READINESS DASHBOARD — app.js
   Routing, API, DOM manipulation, animations
   ============================================ */

(function () {
  'use strict';

  const CGI_BIN = '/cgi-bin';

  // ==========================================
  // DOM REFERENCES
  // ==========================================

  const views = {
    landing: document.getElementById('landingView'),
    loading: document.getElementById('loadingView'),
    error: document.getElementById('errorView'),
    dashboard: document.getElementById('dashboardView'),
    comparison: document.getElementById('comparisonView'),
  };
  const els = {
    // Views
    landingView: document.getElementById('landingView'),
    dashboardView: document.getElementById('dashboardView'),
    comparisonView: document.getElementById('comparisonView'),
    loadingView: document.getElementById('loadingView'),
    errorView: document.getElementById('errorView'),

    // Forms
    urlForm: document.getElementById('urlForm'),
    urlInput: document.getElementById('urlInput'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    competitorToggle: document.getElementById('competitorToggle'),
    competitorExpand: document.getElementById('competitorExpand'),
    competitorUrlInput: document.getElementById('competitorUrlInput'),

    // Loading & Error
    loadingBar: document.getElementById('loadingBar'),
    loadingUrl: document.getElementById('loadingUrl'),
    loadingStatus: document.getElementById('loadingStatus'),
    errorMessage: document.getElementById('errorMessage'),
    errorTitle: document.getElementById('errorTitle'),
    errorIcon: document.getElementById('errorIcon'),
    tryAgainBtn: document.getElementById('tryAgainBtn'),
    cacheBanner: document.getElementById('cacheBanner'),
    cacheTime: document.getElementById('cacheTime'),

    // Rate Limit display
    rateLimitTimer: document.getElementById('rateLimitTimer'),
    rateLimitCountdown: document.getElementById('rateLimitCountdown'),

    // Dashboard Items
    headerMeta: document.getElementById('headerMeta'),
    logoLink: document.getElementById('logoLink'),
    reportMeta: document.getElementById('reportMeta'),
    overallScoreNumber: document.getElementById('overallScoreNumber'),
    overallGrade: document.getElementById('overallGrade'),
    overallVerdict: document.getElementById('overallVerdict'),
    heroSummary: document.getElementById('heroSummary'),
    heroLocation: document.getElementById('heroLocation'),
    scoreCards: document.getElementById('scoreCards'),
    detailSections: document.getElementById('detailSections'),
    newPanelSections: document.getElementById('newPanelSections'), // New container for new panels
    performanceSection: document.getElementById('performanceSection'),
    eeatSection: document.getElementById('eeatSection'),
    serpSection: document.getElementById('serpSection'),
    geoSection: document.getElementById('geoSection'),
    statsGrid: document.getElementById('statsGrid'),
    shareBtn: document.getElementById('shareBtn'),
    pdfBtn: document.getElementById('pdfBtn'),
    shareToast: document.getElementById('shareToast'),

    // Comparison view elements
    compOverallA: document.getElementById('compOverallA'),
    compOverallB: document.getElementById('compOverallB'),
    compVerdictA: document.getElementById('compVerdictA'),
    compVerdictB: document.getElementById('compVerdictB'),
    compSiteLabelA: document.getElementById('compSiteLabelA'),
    compSiteLabelB: document.getElementById('compSiteLabelB'),
    comparisonBarsGrid: document.getElementById('comparisonBarsGrid'),
    compScoreCards: document.getElementById('compScoreCards'),
    compDetailSections: document.getElementById('compDetailSections'),
    compStatsGrid: document.getElementById('compStatsGrid'),
    compShareBtn: document.getElementById('compShareBtn'),
    compPdfBtn: document.getElementById('compPdfBtn'),
    compPerformanceSection: document.getElementById('compPerformanceSection'),
    compEeatSection: document.getElementById('compEeatSection'),
    compSerpSection: document.getElementById('compSerpSection'),
    compGeoSection: document.getElementById('compGeoSection'),
    compCacheBanner: document.getElementById('compCacheBanner'),
    compCacheTime: document.getElementById('compCacheTime'),

    // Lead capture modal
    leadCaptureModal: document.getElementById('leadCaptureModal'),
    leadCaptureForm: document.getElementById('leadCaptureForm'),
    lcName: document.getElementById('lcName'),
    lcEmail: document.getElementById('lcEmail'),
    lcPhone: document.getElementById('lcPhone'),
    lcRole: document.getElementById('lcRole'),
    lcCloseBtn: document.getElementById('lcCloseBtn'),
  };

  // ==========================================
  // STATE
  // ==========================================

  let currentReport = null;
  let currentComparisonData = null;
  let animationFrameId = null;

  // Pending scan URLs (set when user submits URL form, used after lead capture)
  let pendingScanUrl = null;
  let pendingCompetitorUrl = null;

  // Contact info captured from lead form
  let contactInfo = { name: '', email: '', phone: '', role: '' };

  // ==========================================
  // ROUTING
  // ==========================================

  function showView(name) {
    Object.values(views).forEach(v => v.classList.remove('active'));
    if (views[name]) views[name].classList.add('active');
    window.scrollTo({ top: 0 });
  }

  function handleRoute() {
    const hash = window.location.hash;
    if (!hash || hash === '#' || hash === '#home') {
      showView('landing');
      const metaUrl = els.headerMeta.querySelector('.header-meta-url');
      if (metaUrl) metaUrl.remove();
    } else if (hash.startsWith('#report=')) {
      const reportId = hash.replace('#report=', '');
      loadReport(reportId);
    } else if (hash.startsWith('#analyzing=')) {
      const url = decodeURIComponent(hash.replace('#analyzing=', ''));
      runAnalysis(url);
    } else if (hash.startsWith('#comparing=')) {
      const parts = decodeURIComponent(hash.replace('#comparing=', '')).split(',');
      const url = parts[0];
      const competitorUrl = parts[1] || '';
      runComparison(url, competitorUrl);
    } else if (hash.startsWith('#comparison=')) {
      const parts = hash.replace('#comparison=', '').split(',');
      const reportId = parts[0];
      const competitorReportId = parts[1] || '';
      loadComparison(reportId, competitorReportId);
    }
  }

  window.addEventListener('hashchange', handleRoute);

  // ==========================================
  // FORM HANDLING
  // ==========================================

  els.urlForm.addEventListener('submit', function (e) {
    e.preventDefault();
    let url = els.urlInput.value.trim();
    if (!url) return;
    // Add protocol if missing
    if (!/^https?:\/\//i.test(url)) {
      url = 'https://' + url;
    }

    let competitorUrl = els.competitorUrlInput ? els.competitorUrlInput.value.trim() : '';
    if (competitorUrl && !/^https?:\/\//i.test(competitorUrl)) {
      competitorUrl = 'https://' + competitorUrl;
    }

    // Store pending URLs and show lead capture modal instead of scanning immediately
    pendingScanUrl = url;
    pendingCompetitorUrl = competitorUrl;
    showLeadCaptureModal();
  });

  // ---- Lead capture modal logic ----

  function showLeadCaptureModal() {
    if (els.leadCaptureModal) {
      els.leadCaptureModal.classList.add('active');
      // Focus first field for accessibility
      if (els.lcName) els.lcName.focus();
    }
  }

  function hideLeadCaptureModal() {
    if (els.leadCaptureModal) {
      els.leadCaptureModal.classList.remove('active');
    }
  }

  // Close button
  if (els.lcCloseBtn) {
    els.lcCloseBtn.addEventListener('click', function () {
      hideLeadCaptureModal();
      pendingScanUrl = null;
      pendingCompetitorUrl = null;
    });
  }

  // Close on backdrop click
  if (els.leadCaptureModal) {
    els.leadCaptureModal.addEventListener('click', function (e) {
      if (e.target === els.leadCaptureModal || e.target.classList.contains('lc-backdrop')) {
        hideLeadCaptureModal();
        pendingScanUrl = null;
        pendingCompetitorUrl = null;
      }
    });
  }

  // Lead capture form submit
  if (els.leadCaptureForm) {
    els.leadCaptureForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Clear previous error states
      [els.lcName, els.lcEmail, els.lcPhone, els.lcRole].forEach(function (el) {
        if (el) el.classList.remove('lc-input-error');
      });

      // Validate all fields
      var name = els.lcName ? els.lcName.value.trim() : '';
      var email = els.lcEmail ? els.lcEmail.value.trim() : '';
      var phone = els.lcPhone ? els.lcPhone.value.trim() : '';
      var role = els.lcRole ? els.lcRole.value.trim() : '';

      var valid = true;
      if (!name) { if (els.lcName) els.lcName.classList.add('lc-input-error'); valid = false; }
      if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        if (els.lcEmail) els.lcEmail.classList.add('lc-input-error');
        valid = false;
      }
      if (!phone) { if (els.lcPhone) els.lcPhone.classList.add('lc-input-error'); valid = false; }
      if (!role) { if (els.lcRole) els.lcRole.classList.add('lc-input-error'); valid = false; }

      if (!valid) return;

      // Store contact info for API calls
      contactInfo = { name: name, email: email, phone: phone, role: role };

      hideLeadCaptureModal();

      // Proceed with scan
      if (pendingCompetitorUrl) {
        window.location.hash = '#comparing=' + encodeURIComponent(pendingScanUrl) + ',' + encodeURIComponent(pendingCompetitorUrl);
      } else {
        window.location.hash = '#analyzing=' + encodeURIComponent(pendingScanUrl);
      }
    });
  }

  // Competitor toggle expand/collapse
  if (els.competitorToggle) {
    els.competitorToggle.addEventListener('click', function () {
      const expanded = els.competitorExpand.hidden === false;
      if (expanded) {
        els.competitorExpand.hidden = true;
        els.competitorToggle.setAttribute('aria-expanded', 'false');
        els.competitorToggle.classList.remove('is-open');
        // Clear the input when closing
        if (els.competitorUrlInput) els.competitorUrlInput.value = '';
      } else {
        els.competitorExpand.hidden = false;
        els.competitorToggle.setAttribute('aria-expanded', 'true');
        els.competitorToggle.classList.add('is-open');
        if (els.competitorUrlInput) els.competitorUrlInput.focus();
      }
    });
  }

  els.tryAgainBtn.addEventListener('click', function () {
    window.location.hash = '#home';
  });

  els.logoLink.addEventListener('click', function (e) {
    e.preventDefault();
    window.location.hash = '#home';
  });

  // ==========================================
  // LOADING MESSAGES
  // ==========================================

  const loadingMessages = [
    'Fetching your website...',
    'Analyzing meta tags & structure...',
    'Checking schema markup...',
    'Evaluating heading hierarchy...',
    'Scanning for structured data...',
    'Checking AI readiness signals...',
    'Evaluating voice search factors...',
    'Analyzing local search signals...',
    'Generating your report...',
  ];

  let loadingMsgIndex = 0;
  let loadingInterval = null;

  function startLoadingMessages() {
    loadingMsgIndex = 0;
    els.loadingBar.style.width = '0%';
    els.loadingStatus.textContent = loadingMessages[0];

    let step = 0;
    loadingInterval = setInterval(function () {
      step++;
      if (step < loadingMessages.length) {
        els.loadingStatus.textContent = loadingMessages[step];
      }
      const progress = Math.min(90, (step / loadingMessages.length) * 95);
      els.loadingBar.style.width = progress + '%';
    }, 2500);
  }

  function stopLoadingMessages(success) {
    clearInterval(loadingInterval);
    if (success) {
      els.loadingBar.style.width = '100%';
      els.loadingStatus.textContent = 'Report ready!';
    }
  }

  // ==========================================
  // API CALLS
  // ==========================================

  async function runAnalysis(url) {
    showView('loading');
    els.loadingUrl.textContent = url;
    startLoadingMessages();

    try {
      const res = await fetch(CGI_BIN + '/analyze.py', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url,
          contact_name: contactInfo.name,
          contact_email: contactInfo.email,
          contact_phone: contactInfo.phone,
          contact_role: contactInfo.role,
        }),
      });

      const data = await res.json();

      if (!res.ok || data.error) {
        stopLoadingMessages(false);
        els.errorMessage.textContent = data.message || data.error || 'Something went wrong. Please try again.';

        // Handle Rate Limiting UI specifically
        if (res.status === 429 || data.rate_limited) {
          els.errorTitle.textContent = "You've Used Your Free Scan";
          els.rateLimitTimer.hidden = true;
          els.errorIcon.style.color = "var(--color-warning)";
          els.tryAgainBtn.style.display = 'none';
          els.errorMessage.style.maxWidth = "480px";
          els.errorMessage.innerHTML = escapeHtml(data.error || 'Scan limit reached.') +
            (data.days_remaining ? '<br><span style="font-size:0.9rem;color:var(--color-text-muted);">Your next free scan is available in ' + data.days_remaining + ' day' + (data.days_remaining > 1 ? 's' : '') + '.</span>' : '') +
            '<br><br>' +
            '<a href="' + escapeHtml(data.cta_url || 'mailto:hello@alianzaconnects.com?subject=Multi-Scan%20Access%20Inquiry') + '" ' +
            'style="display:inline-block;padding:12px 28px;background:var(--color-primary);color:#fff;border-radius:var(--radius-md);font-weight:700;font-size:1rem;text-decoration:none;margin-top:4px;">' +
            'Get Unlimited Scans →</a>' +
            '<br><span style="font-size:0.8rem;color:var(--color-text-faint);margin-top:8px;display:inline-block;">Multi-Scan &amp; Agency plans available. Contact us to learn more.</span>';
        } else {
          els.errorTitle.textContent = "Analysis Failed";
          els.rateLimitTimer.hidden = true;
          els.errorIcon.style.color = "var(--color-danger)";
          els.tryAgainBtn.style.display = 'inline-flex';
        }

        showView('error');
        return;
      }

      stopLoadingMessages(true);
      currentReport = data;

      // Brief pause so "Report ready!" is visible
      setTimeout(function () {
        window.location.hash = '#report=' + data.report_id;
      }, 600);

    } catch (err) {
      stopLoadingMessages(false);
      els.errorMessage.textContent = "We couldn't reach the analysis server. Please try again.";
      showView('error');
    }
  }

  async function runComparison(url, competitorUrl) {
    showView('loading');
    els.loadingUrl.textContent = url + ' vs ' + competitorUrl;
    startLoadingMessages();

    try {
      const res = await fetch(CGI_BIN + '/analyze.py', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url,
          competitor_url: competitorUrl,
          contact_name: contactInfo.name,
          contact_email: contactInfo.email,
          contact_phone: contactInfo.phone,
          contact_role: contactInfo.role,
        }),
      });

      const data = await res.json();

      if (!res.ok || data.error) {
        stopLoadingMessages(false);
        els.errorMessage.textContent = data.message || data.error || 'Something went wrong. Please try again.';

        // Handle Rate Limiting UI specifically
        if (res.status === 429 || data.rate_limited) {
          els.errorTitle.textContent = "You've Used Your Free Scan";
          els.rateLimitTimer.hidden = true;
          els.errorIcon.style.color = "var(--color-warning)";
          els.tryAgainBtn.style.display = 'none';
          els.errorMessage.style.maxWidth = "480px";
          els.errorMessage.innerHTML = escapeHtml(data.error || 'Scan limit reached.') +
            (data.days_remaining ? '<br><span style="font-size:0.9rem;color:var(--color-text-muted);">Your next free scan is available in ' + data.days_remaining + ' day' + (data.days_remaining > 1 ? 's' : '') + '.</span>' : '') +
            '<br><br>' +
            '<a href="' + escapeHtml(data.cta_url || 'mailto:hello@alianzaconnects.com?subject=Multi-Scan%20Access%20Inquiry') + '" ' +
            'style="display:inline-block;padding:12px 28px;background:var(--color-primary);color:#fff;border-radius:var(--radius-md);font-weight:700;font-size:1rem;text-decoration:none;margin-top:4px;">' +
            'Get Unlimited Scans →</a>' +
            '<br><span style="font-size:0.8rem;color:var(--color-text-faint);margin-top:8px;display:inline-block;">Multi-Scan &amp; Agency plans available. Contact us to learn more.</span>';
        } else {
          els.errorTitle.textContent = "Analysis Failed";
          els.rateLimitTimer.hidden = true;
          els.errorIcon.style.color = "var(--color-danger)";
          els.tryAgainBtn.style.display = 'inline-flex';
        }

        showView('error');
        return;
      }

      stopLoadingMessages(true);
      currentComparisonData = data;

      setTimeout(function () {
        // If the response has primary/competitor keys, it's a comparison result
        if (data.primary && data.competitor) {
          window.location.hash = '#comparison=' + data.primary.report_id + ',' + data.competitor.report_id;
        } else {
          // Fallback to single report
          currentReport = data;
          window.location.hash = '#report=' + data.report_id;
        }
      }, 600);

    } catch (err) {
      stopLoadingMessages(false);
      els.errorMessage.textContent = "We couldn't reach the analysis server. Please try again.";
      showView('error');
    }
  }

  async function loadReport(reportId) {
    // If we already have the report in memory
    if (currentReport && currentReport.report_id === reportId) {
      renderDashboard(currentReport);
      return;
    }

    // Fetch from server
    showView('loading');
    els.loadingUrl.textContent = 'Loading saved report...';
    els.loadingStatus.textContent = 'Retrieving your report...';
    els.loadingBar.style.width = '50%';

    try {
      const res = await fetch(CGI_BIN + '/analyze.py?id=' + reportId + '&t=' + Date.now());
      const data = await res.json();

      if (!res.ok || data.error) {
        els.errorMessage.textContent = data.error || 'Report not found.';
        showView('error');
        return;
      }

      els.loadingBar.style.width = '100%';
      currentReport = data;
      setTimeout(function () {
        renderDashboard(data);
      }, 300);

    } catch (err) {
      els.errorMessage.textContent = 'Could not load this report. It may have expired.';
      showView('error');
    }
  }

  async function loadComparison(reportId, competitorReportId) {
    // If we already have the comparison data in memory
    if (
      currentComparisonData &&
      currentComparisonData.primary &&
      currentComparisonData.primary.report_id === reportId
    ) {
      renderComparison(currentComparisonData);
      return;
    }

    showView('loading');
    els.loadingUrl.textContent = 'Loading comparison report...';
    els.loadingStatus.textContent = 'Retrieving comparison data...';
    els.loadingBar.style.width = '30%';

    try {
      // Fetch both reports in parallel
      const [resA, resB] = await Promise.all([
        fetch(CGI_BIN + '/analyze.py?id=' + reportId),
        competitorReportId ? fetch(CGI_BIN + '/analyze.py?id=' + competitorReportId) : Promise.resolve(null),
      ]);

      const dataA = await resA.json();
      const dataB = resB ? await resB.json() : null;

      if (!resA.ok || dataA.error) {
        els.errorMessage.textContent = dataA.error || 'Report not found.';
        showView('error');
        return;
      }

      els.loadingBar.style.width = '100%';

      const compData = { primary: dataA, competitor: dataB };
      currentComparisonData = compData;

      setTimeout(function () {
        renderComparison(compData);
      }, 300);

    } catch (err) {
      els.errorMessage.textContent = 'Could not load this comparison report. It may have expired.';
      showView('error');
    }
  }

  // ==========================================
  // RENDER DASHBOARD
  // ==========================================

  function renderDashboard(data) {
    showView('dashboard');

    // Header meta
    const dateStr = new Date(data.analyzed_at || Date.now()).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
    els.reportMeta.innerHTML = `
      <span class="report-meta-item">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        ${dateStr}
      </span>
      <span class="report-meta-item">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
        ${escapeHtml(data.url)}
      </span>
    `;

    const existingUrl = els.headerMeta.querySelector('.header-meta-url');
    if (existingUrl) existingUrl.remove();
    const urlSpan = document.createElement('span');
    urlSpan.className = 'header-meta-url';
    urlSpan.style.cssText = 'font-size:var(--text-xs);color:var(--color-text-faint)';
    urlSpan.textContent = truncate(data.url, 40);
    els.headerMeta.insertBefore(urlSpan, els.headerMeta.firstChild);

    // Overall score & Grade
    const overall = Math.round(
      (data.scores.traditional_seo + data.scores.ai_search + data.scores.voice_search + data.scores.local_search) / 4
    );
    els.overallScoreNumber.style.display = 'block';
    animateNumber(els.overallScoreNumber, overall, 1500);

    const grade = calculateGrade(overall);
    els.overallGrade.textContent = grade.text;
    els.overallGrade.style.color = grade.color;

    // Verdict
    const verdict = getVerdict(overall);
    els.overallVerdict.className = 'overall-verdict verdict-' + verdict.class;
    els.overallVerdict.textContent = verdict.label;

    // Summary & Location
    if (data.summary) {
        if (els.heroSummary) els.heroSummary.textContent = data.summary.website_summary || '';
        if (els.heroLocation) els.heroLocation.textContent = data.summary.location || '';
    }


    // Score cards
    renderScoreCards(data);

    // Legacy Detail sections (Traditional SEO, Voice Search, Local Search)
    const legacyCategories = categories.filter(c => c.key !== 'ai_search');
    renderDetailSectionsExplicit(data, els.detailSections, legacyCategories);

    // New API Panels
    if (data.performance) renderPerformancePanel(data, els.performanceSection);
    if (data.eeat_analysis) renderEEATPanel(data, els.eeatSection);
    if (data.serp_analysis) renderSERPPanel(data, els.serpSection);
    if (data.geo_analysis) renderAISearchPanel(data, els.geoSection);

    // Handle cache display
    if (data.from_cache && data.analyzed_at) {
      els.cacheBanner.hidden = false;
      els.cacheTime.textContent = new Date(data.analyzed_at).toLocaleString();
    } else {
      els.cacheBanner.hidden = true;
    }

    // Stats
    renderStats();

    // Share button
    els.shareBtn.onclick = function () {
      const shareUrl = window.location.origin + window.location.pathname + '#report=' + data.report_id;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(function () {
          showToast();
        });
      } else {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = shareUrl;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast();
      }
    };

    // PDF button
    if (els.pdfBtn) {
      els.pdfBtn.onclick = function () {
        window.open(CGI_BIN + '/report.py?id=' + data.report_id + '&print=1', '_blank');
      };
    }

    // Setup intersection observer for fade-ins
    setupScrollObserver();
  }

  // ==========================================
  // RENDER COMPARISON
  // ==========================================

  function renderComparison(data) {
    showView('comparison');

    const primary = data.primary;
    const competitor = data.competitor;

    // Update header URL display
    const existingUrl = els.headerMeta.querySelector('.header-meta-url');
    if (existingUrl) existingUrl.remove();
    const urlSpan = document.createElement('span');
    urlSpan.className = 'header-meta-url';
    urlSpan.style.cssText = 'font-size:var(--text-xs);color:var(--color-text-faint)';
    urlSpan.textContent = truncate(primary.url, 30) + ' vs ' + truncate((competitor && competitor.url) || '', 30);
    els.headerMeta.insertBefore(urlSpan, els.headerMeta.firstChild);

    // Site labels
    els.compSiteLabelA.textContent = truncate(primary.url.replace(/^https?:\/\//i, ''), 35);
    els.compSiteLabelB.textContent = competitor ? truncate(competitor.url.replace(/^https?:\/\//i, ''), 35) : 'Competitor';

    // Overall scores
    const overallA = calcOverall(primary.scores);
    const overallB = competitor ? calcOverall(competitor.scores) : 0;

    animateNumber(els.compOverallA, overallA, 1500);
    animateNumber(els.compOverallB, overallB, 1500);

    els.compOverallA.style.color = getScoreColor(overallA);
    els.compOverallB.style.color = getScoreColor(overallB);

    const verdictA = getVerdict(overallA);
    const verdictB = getVerdict(overallB);
    els.compVerdictA.className = 'comparison-overall-verdict verdict-' + verdictA.class;
    els.compVerdictA.textContent = verdictA.label;
    els.compVerdictB.className = 'comparison-overall-verdict verdict-' + verdictB.class;
    els.compVerdictB.textContent = verdictB.label;

    // Winner highlight on header scores
    els.compOverallA.classList.remove('comp-winner', 'comp-loser');
    els.compOverallB.classList.remove('comp-winner', 'comp-loser');
    if (overallA > overallB) {
      els.compOverallA.classList.add('comp-winner');
      els.compOverallB.classList.add('comp-loser');
    } else if (overallB > overallA) {
      els.compOverallB.classList.add('comp-winner');
      els.compOverallA.classList.add('comp-loser');
    }

    // Category bars
    renderComparisonBars(primary, competitor);

    // Full detail for primary site (reuse existing renderers with comp containers)
    renderScoreCardsIn(primary, els.compScoreCards);
    renderDetailSectionsIn(primary, els.compDetailSections);

    // Stats grid
    renderStatsIn(els.compStatsGrid);

    // Share button
    els.compShareBtn.onclick = function () {
      const compId = competitor ? ',' + competitor.report_id : '';
      const shareUrl = window.location.origin + window.location.pathname + '#comparison=' + primary.report_id + compId;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(showToast);
      } else {
        const ta = document.createElement('textarea');
        ta.value = shareUrl;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast();
      }
    };

    // PDF button (comparison)
    if (els.compPdfBtn) {
      els.compPdfBtn.onclick = function () {
        let pdfUrl = CGI_BIN + '/report.py?id=' + primary.report_id + '&print=1';
        if (competitor) pdfUrl += '&competitor_id=' + competitor.report_id;
        window.open(pdfUrl, '_blank');
      };
    }

    // Scroll observer
    setupScrollObserver();
  }

  function calcOverall(scores) {
    return Math.round(
      (scores.traditional_seo + scores.ai_search + scores.voice_search + scores.local_search) / 4
    );
  }

  function renderComparisonBars(primary, competitor) {
    els.comparisonBarsGrid.innerHTML = '';
    categories.forEach(function (cat) {
      const scoreA = primary.scores[cat.key] || 0;
      const scoreB = (competitor && competitor.scores[cat.key]) || 0;
      const aWins = scoreA > scoreB;
      const bWins = scoreB > scoreA;

      const row = document.createElement('div');
      row.className = 'comp-bar-row';

      row.innerHTML = `
        <div class="comp-bar-label">
          <div class="comp-bar-icon score-card-icon--${cat.icon}">${categoryIcons[cat.icon]}</div>
          <span class="comp-bar-cat-name">${cat.name}</span>
        </div>
        <div class="comp-bar-body">
          <div class="comp-bar-side comp-bar-side--a">
            <span class="comp-bar-score ${aWins ? 'comp-score-win' : (bWins ? 'comp-score-lose' : '')}"
              style="color:${aWins ? '#22C55E' : (bWins ? '#EF4444' : 'var(--color-text-muted)')}">
              ${scoreA}
              ${aWins ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15"/></svg>' : ''}
            </span>
            <div class="comp-bar-track">
              <div class="comp-bar-fill comp-bar-fill--a" data-width="${scoreA}"
                style="background:${cat.color};width:0%"></div>
            </div>
          </div>
          <div class="comp-bar-divider"></div>
          <div class="comp-bar-side comp-bar-side--b">
            <div class="comp-bar-track">
              <div class="comp-bar-fill comp-bar-fill--b" data-width="${scoreB}"
                style="background:${cat.color};width:0%;transform-origin:left"></div>
            </div>
            <span class="comp-bar-score ${bWins ? 'comp-score-win' : (aWins ? 'comp-score-lose' : '')}"
              style="color:${bWins ? '#22C55E' : (aWins ? '#EF4444' : 'var(--color-text-muted)')}">
              ${bWins ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15"/></svg>' : ''}
              ${scoreB}
            </span>
          </div>
        </div>
        <div class="comp-bar-winner">
          ${aWins ? '<span class="comp-winner-badge comp-winner-badge--a">You win</span>' : ''}
          ${bWins ? '<span class="comp-winner-badge comp-winner-badge--b">Competitor wins</span>' : ''}
          ${!aWins && !bWins ? '<span class="comp-tie-badge">Tied</span>' : ''}
        </div>
      `;

      els.comparisonBarsGrid.appendChild(row);
    });

    // Animate bars after paint
    requestAnimationFrame(function () {
      setTimeout(function () {
        els.comparisonBarsGrid.querySelectorAll('.comp-bar-fill').forEach(function (bar) {
          bar.style.width = bar.getAttribute('data-width') + '%';
        });
      }, 150);
    });
  }

  // ==========================================
  // SCORE CARDS
  // ==========================================

  const categories = [
    { key: 'traditional_seo', name: 'Traditional SEO', icon: 'seo', color: '#3B82F6', detailId: 'detail-seo' },
    { key: 'ai_search', name: 'AI Search', icon: 'ai', color: '#A855F7', detailId: 'detail-ai' },
    { key: 'voice_search', name: 'Voice Search', icon: 'voice', color: '#22D3EE', detailId: 'detail-voice' },
    { key: 'local_search', name: 'Local Search', icon: 'local', color: '#22C55E', detailId: 'detail-local' },
  ];

  const categoryIcons = {
    seo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    ai: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 0-4 4c0 2 2 3 2 6h4c0-3 2-4 2-6a4 4 0 0 0-4-4z"/><path d="M10 18h4"/><path d="M10 22h4"/></svg>',
    voice: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/></svg>',
    local: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  };

  // Generic score card renderer (targets a given container)
  function renderScoreCardsIn(data, container) {
    container.innerHTML = '';
    
    // 1) Render the special Speed Card first
    if (data.performance && data.performance.metrics) {
      const m = data.performance.metrics;
      const card = document.createElement('div');
      card.className = 'score-card speed-card';
      // Inline styles for the Speed Card specifically to match the others but hold 3 metrics
      card.style.display = 'flex';
      card.style.flexDirection = 'column';
      card.style.justifyContent = 'space-between';
      card.style.alignItems = 'center';
      card.style.padding = 'var(--space-4)';
      
      const lcp = parseFloat(m.lcp) || 0;
      const cls = parseFloat(m.cls) || 0;
      const fcp = parseFloat(m.fcp) || 0;
      
      // Basic color logic for CWV
      const getColor = (val, good, poor) => {
        if (val <= good) return '#22C55E';
        if (val > poor) return '#EF4444';
        return '#EAB308';
      };
      
      card.innerHTML = 
        '<div class="score-card-icon" style="color:var(--color-primary); background:var(--color-primary-light);">' +
        '  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' +
        '</div>' +
        '<span class="score-card-name">Speed Index</span>' +
        '<div style="display:flex; gap:1rem; width:100%; justify-content:center; margin:1rem 0;">' +
        '  <div style="text-align:center;">' +
        '     <div style="font-size:0.75rem; color:var(--color-text-muted);">LCP</div>' +
        '     <div style="font-weight:600; color:' + getColor(lcp, 2.5, 4.0) + '">' + lcp + 's</div>' +
        '  </div>' +
        '  <div style="text-align:center;">' +
        '     <div style="font-size:0.75rem; color:var(--color-text-muted);">CLS</div>' +
        '     <div style="font-weight:600; color:' + getColor(cls, 0.1, 0.25) + '">' + cls + '</div>' +
        '  </div>' +
        '  <div style="text-align:center;">' +
        '     <div style="font-size:0.75rem; color:var(--color-text-muted);">FCP</div>' +
        '     <div style="font-weight:600; color:' + getColor(fcp, 1.8, 3.0) + '">' + fcp + 's</div>' +
        '  </div>' +
        '</div>';
      
      // Scroll to performance section on click
      card.addEventListener('click', function() {
        const target = document.getElementById('performanceSection');
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      
      container.appendChild(card);
    }
    categories.forEach(function (cat) {
      const score = data.scores[cat.key] || 0;
      const verdict = getVerdict(score);
      const circumference = 2 * Math.PI * 42;
      const offset = circumference - (score / 100) * circumference;

      const card = document.createElement('div');
      card.className = 'score-card';
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', cat.name + ': ' + score + ' out of 100');

      card.innerHTML = `
        <div class="score-card-icon score-card-icon--${cat.icon}">${categoryIcons[cat.icon]}</div>
        <span class="score-card-name">${cat.name}</span>
        <div class="score-gauge">
          <svg viewBox="0 0 100 100">
            <circle class="gauge-bg" cx="50" cy="50" r="42"/>
            <circle class="gauge-fill gauge-fill--${cat.icon}" cx="50" cy="50" r="42"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${circumference}"
              data-target-offset="${offset}"/>
          </svg>
          <div class="score-gauge-number" data-target="${score}">0</div>
        </div>
        <span class="score-card-status status-${verdict.class}">${verdict.label}</span>
      `;

      const compDetailId = cat.detailId + '-comp';
      card.addEventListener('click', function () {
        const target = container !== els.scoreCards
          ? (document.getElementById(compDetailId) || document.getElementById(cat.detailId))
          : document.getElementById(cat.detailId);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const target = container !== els.scoreCards
            ? (document.getElementById(compDetailId) || document.getElementById(cat.detailId))
            : document.getElementById(cat.detailId);
          if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });

      container.appendChild(card);
    });

    requestAnimationFrame(function () {
      setTimeout(animateGaugesIn.bind(null, container), 200);
    });
  }

  function renderScoreCards(data) {
    renderScoreCardsIn(data, els.scoreCards);
  }

  function animateGaugesIn(container) {
    container.querySelectorAll('.gauge-fill').forEach(function (el) {
      const target = el.getAttribute('data-target-offset');
      el.style.strokeDashoffset = target;
    });
    container.querySelectorAll('.score-gauge-number').forEach(function (el) {
      const target = parseInt(el.getAttribute('data-target'), 10);
      animateNumber(el, target, 1200);
    });
  }

  function animateGauges() {
    animateGaugesIn(document);
  }

  // ==========================================
  // DETAIL SECTIONS
  // ==========================================

  const educationContent = {
    traditional_seo: `<p>Think of SEO like your business's address in the Yellow Pages — except today, that address is your website, and the Yellow Pages is Google. When someone searches "plumber near me" or "best dentist in Dallas," search engines decide which businesses to show based on dozens of signals on your website.</p><p style="margin-top:var(--space-3)">Things like your page title, description, and heading structure tell Google exactly what your business does and where you do it. Without these signals, you're essentially invisible — like having a storefront with no sign.</p>`,
    ai_search: `<p>Here's what's changing FAST: When people search on Google, ChatGPT, or Siri, AI is now reading your website and deciding whether to recommend your business. But AI doesn't read websites the way humans do.</p><p style="margin-top:var(--space-3)">It looks for structured data — special code that labels your business name, services, hours, location, and reviews in a way machines can instantly understand. Think of it like translating your website into a language that AI speaks. Businesses without this "translation" are being skipped over by AI assistants — and this is already happening today, not in the future.</p>`,
    voice_search: `<p>"Hey Google, who's the best plumber near me?" — Over 50% of searches are now done by voice. When someone asks their phone or smart speaker a question, the device doesn't read them a list of 10 links. It picks ONE answer.</p><p style="margin-top:var(--space-3)">Voice search looks for websites that answer questions directly, load fast, and are easy to read aloud. If your website doesn't have clear, conversational answers to common questions about your services, you're missing out on a rapidly growing channel.</p>`,
    local_search: `<p>For home service and professional service businesses, local search is everything. When someone searches "emergency plumber near me" at 11pm, Google uses very specific signals to decide who shows up in that map pack at the top.</p><p style="margin-top:var(--space-3)">Your website needs to clearly communicate WHERE you operate, WHAT you do, and HOW to contact you — not just to humans, but in the code itself. We check for things like local business markup, consistent contact info, and geographic signals that tell search engines "yes, this business serves THIS area."</p>`,
  };

  // Generic detail sections renderer (targets a given container)
  function renderDetailSectionsIn(data, container, categoryList) {
    container.innerHTML = '';
    const isComp = container !== els.detailSections;
    const catsToRender = categoryList || categories;

    catsToRender.forEach(function (cat) {
      const checks = data.checks[cat.key] || [];
      const score = data.scores[cat.key] || 0;
      const recs = buildRecommendations(checks, cat.key);

      const section = document.createElement('section');
      section.className = 'detail-section';
      section.id = isComp ? (cat.detailId + '-comp') : cat.detailId;

      const scoreColor = getScoreColor(score);

      section.innerHTML = `
        <div class="section-header">
          <div class="section-icon score-card-icon--${cat.icon}">${categoryIcons[cat.icon]}</div>
          <h2 class="section-title">${cat.name}</h2>
          <div class="section-score" style="color:${scoreColor}">${score}/100</div>
        </div>
        <div class="detail-panels">
          <div class="panel">
            <div class="panel-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
              What We Found
            </div>
            <ul class="audit-list" role="list">
              ${checks.map(renderCheckItem).join('')}
            </ul>
          </div>
          <div class="panel">
            <div class="panel-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              Why This Matters
            </div>
            <div class="education-text">
              ${educationContent[cat.key]}
            </div>
          </div>
          ${recs.length > 0 ? `
          <div class="panel recommendations-panel">
            <div class="panel-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
              What To Do Next
            </div>
            <ul class="rec-list" role="list">
              ${recs.map(renderRecItem).join('')}
            </ul>
            <div class="cta-card">
              <div class="cta-card-title">Need help implementing these changes?</div>
              <p class="cta-card-text">Alianza Connects specializes in making businesses visible across every search channel — Traditional, AI, Voice, and Local.</p>
              <a href="https://alianzaconnects.com" target="_blank" rel="noopener noreferrer" class="btn-primary" style="text-decoration:none;display:inline-flex;">Schedule a Free Strategy Call</a>
            </div>
          </div>
          ` : ''}
        </div>
      `;

      container.appendChild(section);
    });
  }

  function renderDetailSectionsExplicit(data, container, categoryList) {
    const originalCategories = categories;
    // Temporarily swap categories for this call
    // (A bit hacky, but avoids rewriting the whole generic renderer right now)
    const oldCategories = window.categories || categories;
    // We'll just pass the list to renderDetailSectionsIn and modify it
    renderDetailSectionsIn(data, container, categoryList);
  }

  function renderDetailSections(data) {
    renderDetailSectionsIn(data, els.detailSections);
  }

  function renderCheckItem(check) {
    let iconClass = 'audit-pass';
    let iconSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>';

    if (check.status === 'fail') {
      iconClass = 'audit-fail';
      iconSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    } else if (check.status === 'warn') {
      iconClass = 'audit-warn';
      iconSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M12 9v4"/><path d="M12 17h.01"/></svg>';
    }

    return `
      <li class="audit-item">
        <span class="audit-icon ${iconClass}">${iconSvg}</span>
        <div>
          <span class="audit-label">${escapeHtml(check.label)}</span>
          <span class="audit-detail"> — ${escapeHtml(check.detail)}</span>
        </div>
      </li>
    `;
  }

  function buildRecommendations(checks, category) {
    const recs = [];
    checks.forEach(function (check) {
      if (check.status === 'fail' || check.status === 'warn') {
        recs.push({
          priority: check.status === 'fail' ? 'high' : 'medium',
          title: check.fix_title || ('Fix: ' + check.label),
          why: check.fix_why || 'This affects your visibility in search.',
          impact: check.impact || 'Medium',
        });
      }
    });
    // Sort: high first
    recs.sort(function (a, b) {
      if (a.priority === 'high' && b.priority !== 'high') return -1;
      if (a.priority !== 'high' && b.priority === 'high') return 1;
      return 0;
    });
    return recs;
  }

  function renderRecItem(rec) {
    return `
      <li class="rec-item">
        <span class="rec-priority priority-${rec.priority}">${rec.priority}</span>
        <div class="rec-content">
          <div class="rec-title">${escapeHtml(rec.title)}</div>
          <div class="rec-why">${escapeHtml(rec.why)}</div>
        </div>
        </div>
        <div class="rec-impact">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          ${escapeHtml(rec.impact)} impact
        </div>
      </li>
    `;
  }

  // ==========================================
  // NEW PANELS (PERFORMANCE, EEAT, SERP, GEO)
  // ==========================================

  function renderPerformancePanel(data, container) {
    if (!data.performance || !data.performance.metrics) return;
    const m = data.performance.metrics;

    function getCWVStatus(val, limit1, limit2) {
      const v = parseFloat(val);
      if (isNaN(v)) return { text: 'Unknown', color: 'var(--color-text-muted)' };
      if (v > limit2) return { text: 'Poor', color: 'var(--color-danger)' };
      if (v > limit1) return { text: 'Needs Improvement', color: 'var(--color-warning)' };
      return { text: 'Good', color: 'var(--color-success)' };
    }

    const st_lcp = getCWVStatus(m.lcp, 2.5, 4.0);
    const st_cls = getCWVStatus(m.cls, 0.1, 0.25);
    const st_fcp = getCWVStatus(m.fcp, 1.8, 3.0);

    container.innerHTML = `
      <div class="section-header">
        <div class="section-icon score-card-icon--seo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <h2 class="section-title">Speed &amp; Core Web Vitals</h2>
      </div>
      <p style="color:var(--color-text-muted); margin: -10px 0 20px 0; max-width: 800px; font-size: 0.95rem;">
        Google explicitly ranks sites higher if they load quickly and maintain visual stability. Core Web Vitals measure the real-world user experience of your page. Fast sites have lower bounce rates and higher conversion rates.
      </p>
      <div class="metrics-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-4);">
        <div class="metric-card" style="border-bottom: 3px solid ${st_lcp.color}; padding: 1.5rem; background: var(--color-surface); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm);">
          <div style="display:flex; justify-content: space-between; align-items:flex-start; margin-bottom: 0.5rem;">
            <div class="metric-label" style="font-weight: 600; color: var(--color-text-main);">Largest Contentful Paint</div>
            <div style="color: ${st_lcp.color}; font-size: 0.8rem; font-weight: 600; background: ${st_lcp.color}15; padding: 2px 8px; border-radius: 12px;">${st_lcp.text}</div>
          </div>
          <div class="metric-value" style="font-size: 2rem; font-weight: 800; color: var(--color-text-main); margin-bottom: 0.5rem;">${escapeHtml(m.lcp || '-')}s</div>
          <p style="font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.4; margin: 0;">Measures loading performance. It marks the point when the page's main content has likely loaded. A fast LCP helps reassure the user that the page is useful.</p>
        </div>
        <div class="metric-card" style="border-bottom: 3px solid ${st_cls.color}; padding: 1.5rem; background: var(--color-surface); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm);">
          <div style="display:flex; justify-content: space-between; align-items:flex-start; margin-bottom: 0.5rem;">
            <div class="metric-label" style="font-weight: 600; color: var(--color-text-main);">Cumulative Layout Shift</div>
            <div style="color: ${st_cls.color}; font-size: 0.8rem; font-weight: 600; background: ${st_cls.color}15; padding: 2px 8px; border-radius: 12px;">${st_cls.text}</div>
          </div>
          <div class="metric-value" style="font-size: 2rem; font-weight: 800; color: var(--color-text-main); margin-bottom: 0.5rem;">${escapeHtml(m.cls || '-')}</div>
          <p style="font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.4; margin: 0;">Measures visual stability. It quantifies how much the page layout shifts around as it loads. A low CLS ensures your page is delightful to interact with.</p>
        </div>
        <div class="metric-card" style="border-bottom: 3px solid ${st_fcp.color}; padding: 1.5rem; background: var(--color-surface); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm);">
           <div style="display:flex; justify-content: space-between; align-items:flex-start; margin-bottom: 0.5rem;">
            <div class="metric-label" style="font-weight: 600; color: var(--color-text-main);">First Contentful Paint</div>
            <div style="color: ${st_fcp.color}; font-size: 0.8rem; font-weight: 600; background: ${st_fcp.color}15; padding: 2px 8px; border-radius: 12px;">${st_fcp.text}</div>
          </div>
          <div class="metric-value" style="font-size: 2rem; font-weight: 800; color: var(--color-text-main); margin-bottom: 0.5rem;">${escapeHtml(m.fcp || '-')}s</div>
          <p style="font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.4; margin: 0;">Measures how long it takes for the browser to render the first piece of DOM content. A fast FCP reassures users that something is happening.</p>
        </div>
      </div>
    `;
  }

  function renderEEATPanel(data, container) {
    if (!data.eeat_analysis) return;
    const eeat = data.eeat_analysis;

    let strengthsHtml = '';
    if (eeat.strengths && eeat.strengths.length > 0) {
      strengthsHtml = `
        <div class="eeat-card" style="background: var(--color-surface); padding: 1.5rem; border-radius: var(--radius-lg); border-left: 4px solid var(--color-success); box-shadow: var(--shadow-sm);">
          <div style="display:flex; align-items:center; gap: 0.5rem; text-transform:uppercase; font-size: 0.8rem; font-weight: 700; color: var(--color-success); margin-bottom: 1rem;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            Current Strengths
          </div>
          <ul style="margin: 0; padding-left: 1.2rem; display: flex; flex-direction: column; gap: 0.5rem;">
            ${eeat.strengths.slice(0, 3).map(s => `<li style="color:var(--color-text-main); font-size:0.9rem; line-height:1.4">${escapeHtml(s)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    let weaknessesHtml = '';
    if (eeat.weaknesses && eeat.weaknesses.length > 0) {
      weaknessesHtml = `
        <div class="eeat-card" style="background: var(--color-surface); padding: 1.5rem; border-radius: var(--radius-lg); border-left: 4px solid var(--color-danger); box-shadow: var(--shadow-sm);">
          <div style="display:flex; align-items:center; gap: 0.5rem; text-transform:uppercase; font-size: 0.8rem; font-weight: 700; color: var(--color-danger); margin-bottom: 1rem;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Critical Weaknesses
          </div>
          <ul style="margin: 0; padding-left: 1.2rem; display: flex; flex-direction: column; gap: 0.5rem;">
            ${eeat.weaknesses.slice(0, 3).map(w => `<li style="color:var(--color-text-main); font-size:0.9rem; line-height:1.4">${escapeHtml(w)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    let actionPlanHtml = '';
    if (eeat.action_plan && eeat.action_plan.length > 0) {
      actionPlanHtml = `
        <div class="eeat-card" style="background: var(--color-primary-light); padding: 1.5rem; border-radius: var(--radius-lg); border-left: 4px solid var(--color-primary); margin-top: 1rem;">
          <div style="display:flex; align-items:center; gap: 0.5rem; text-transform:uppercase; font-size: 0.8rem; font-weight: 700; color: var(--color-primary); margin-bottom: 1rem;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
            Recommended Action Plan
          </div>
          <ol style="margin: 0; padding-left: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; color: var(--color-text-main);">
            ${eeat.action_plan.map(a => `<li style="font-size:0.9rem; line-height:1.4">${escapeHtml(a)}</li>`).join('')}
          </ol>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="section-header" style="margin-top: var(--space-8)">
        <div class="section-icon score-card-icon--ai">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <h2 class="section-title">E-E-A-T Quality Analysis</h2>
      </div>
      <p style="color:var(--color-text-muted); margin: -10px 0 20px 0; max-width: 800px; font-size: 0.95rem;">
        Google uses "Experience, Expertise, Authoritativeness, and Trustworthiness" (E-E-A-T) to evaluate content quality. Websites lacking these signals are actively demoted in search results and ignored by Generative AI.
      </p>

      <div class="eeat-scores" style="display:grid; grid-template-columns: 1fr; gap: var(--space-3); margin-bottom: var(--space-6); max-width: 500px; padding: 1.5rem; background: var(--color-surface); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
        <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--color-text-muted); margin-bottom: 0.5rem;">Core Signal Scores</div>
        ${['experience', 'expertise', 'authority', 'trust'].map(key => {
          const val = eeat[`${key}_score`] || 0;
          const color = getScoreColor(val);
          const name = key.charAt(0).toUpperCase() + key.slice(1);
          return `
            <div style="display:grid; grid-template-columns: 100px 1fr 30px; gap: 12px; align-items: center; font-size: var(--text-sm); font-weight: 600;">
              <span>${name}</span>
              <div style="background: ${color}; width: ${val}%; height: 100%; border-radius: 4px; transition: width 1s ease-out;"></div>
              <span style="text-align:right; color: ${color}">${val}</span>
            </div>
          `;
        }).join('')}
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
        ${strengthsHtml}
        ${weaknessesHtml}
      </div>
      ${actionPlanHtml}
    `;
  }

  function renderSERPPanel(data, container) {
    if (!data.serp_analysis || !data.serp_analysis.rankings || data.serp_analysis.rankings.length === 0) return;

    container.innerHTML = `
      <div class="section-header" style="margin-top: var(--space-8)">
        <div class="section-icon score-card-icon--local">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        </div>
        <h2 class="section-title">SERP Keyword Visibility</h2>
      </div>
      <p style="color:var(--color-text-muted); margin: -10px 0 20px 0; max-width: 600px;">
        Live Google search rankings for competitive queries. Keywords below #10 represent "content gaps" where competitors outrank you.
      </p>

      <div class="table-container" style="overflow-x: auto; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg);">
        <table class="checks-table" style="width: 100%; text-align: left; border-collapse: collapse;">
          <thead>
            <tr style="border-bottom: 1px solid var(--color-border); background: var(--color-surface-2);">
              <th style="padding: var(--space-3) var(--space-4); font-weight: 600;">Query</th>
              <th style="padding: var(--space-3) var(--space-4); font-weight: 600; width: 100px;">Position</th>
              <th style="padding: var(--space-3) var(--space-4); font-weight: 600;">Top Competitors</th>
            </tr>
          </thead>
          <tbody>
            ${data.serp_analysis.rankings.map(r => {
              const inTop10 = typeof r.position === 'number' && r.position <= 10;
              const badgeStyle = inTop10
                ? 'background: var(--color-success-highlight); color: var(--color-success); border: 1px solid rgba(34, 197, 94, 0.2);'
                : 'background: var(--color-surface-2); color: var(--color-text-muted); border: 1px solid var(--color-border);';
              const comps = r.competitors ? r.competitors.slice(0,3).map(c => escapeHtml(c)).join(', ') : '-';

              return `
                <tr style="border-bottom: 1px solid var(--color-divider);">
                  <td style="padding: var(--space-3) var(--space-4); font-weight: 500;">${escapeHtml(r.query)}</td>
                  <td style="padding: var(--space-3) var(--space-4);">
                    <span style="${badgeStyle} padding: 2px 8px; border-radius: 12px; font-size: var(--text-xs); font-weight: 700;">
                      ${r.position}
                    </span>
                  </td>
                  <td style="padding: var(--space-3) var(--space-4); color: var(--color-text-muted); font-size: var(--text-sm);">
                    ${comps}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  function renderAISearchPanel(data, container) {
    if (!data.geo_analysis) return;
    const score = data.scores.ai_search || 0;
    const scoreColor = getScoreColor(score);

    // Merge standard ai_search checks with geo_analysis checks for a "complete" view
    const aiChecks = data.checks.ai_search || [];
    const geoChecks = data.geo_analysis.checks || [];
    const allChecks = [...aiChecks, ...geoChecks];
    
    // Sort so major passes/fails are grouped or just keep mixed? 
    // Let's keep them order-reflecting.
    
    const recs = buildRecommendations(allChecks, 'ai_search');

    container.innerHTML = `
      <div class="section-header" style="margin-top: var(--space-8)">
        <div class="section-icon score-card-icon--ai">${categoryIcons.ai}</div>
        <h2 class="section-title">AI Search Readiness</h2>
        <div class="section-score" style="color:${scoreColor}">${score}/100</div>
      </div>
      <div class="detail-panels">
        <div class="panel">
          <div class="panel-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
            What We Found
          </div>
          <ul class="audit-list" role="list">
            ${allChecks.map(renderCheckItem).join('')}
          </ul>
        </div>
        <div class="panel">
          <div class="panel-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
            Why This Matters
          </div>
          <div class="education-text">
            ${educationContent.ai_search}
          </div>
        </div>
        ${recs.length > 0 ? `
        <div class="panel recommendations-panel">
          <div class="panel-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
            What To Do Next
          </div>
          <ul class="rec-list" role="list">
            ${recs.map(renderRecItem).join('')}
          </ul>
        </div>
        ` : ''}
      </div>
    `;
  }

  // ==========================================
  // STATS SECTION
  // ==========================================

  const statsData = [
    { number: '47%', label: 'AI Overviews now appear in Google searches' },
    { number: '50%+', label: 'of all searches are done by voice' },
    { number: '93%', label: 'of online experiences begin with a search engine' },
    { number: '46%', label: 'of all Google searches seek local information' },
    { number: '65%+', label: 'of Google searches are zero-click (no website visit)' },
  ];

  function renderStats() {
    renderStatsIn(els.statsGrid);
  }

  function renderStatsIn(container) {
    container.innerHTML = '';
    statsData.forEach(function (stat, i) {
      const card = document.createElement('div');
      card.className = 'stat-card';
      card.innerHTML = `
        <div class="stat-number">${stat.number}</div>
        <div class="stat-label">${stat.label}</div>
      `;
      container.appendChild(card);
    });
  }

  // ==========================================
  // SCROLL ANIMATIONS
  // ==========================================

  function setupScrollObserver() {
    const targets = document.querySelectorAll('.detail-section, .stat-card');
    if (!('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('visible'); });
      return;
    }

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    targets.forEach(function (el) {
      observer.observe(el);
    });
  }

  // ==========================================
  // UTILITIES
  // ==========================================

  function animateNumber(el, target, duration) {
    const start = performance.now();
    const initial = 0;

    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(initial + (target - initial) * eased);
      el.textContent = current;
      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        el.textContent = target;
      }
    }
    requestAnimationFrame(tick);
  }

  function calculateGrade(score) {
    if (score >= 97) return { text: 'A+', color: '#22C55E' };
    if (score >= 93) return { text: 'A', color: '#22C55E' };
    if (score >= 90) return { text: 'A-', color: '#22C55E' };
    if (score >= 87) return { text: 'B+', color: '#84CC16' };
    if (score >= 83) return { text: 'B', color: '#84CC16' };
    if (score >= 80) return { text: 'B-', color: '#84CC16' };
    if (score >= 77) return { text: 'C+', color: '#EAB308' };
    if (score >= 73) return { text: 'C', color: '#EAB308' };
    if (score >= 70) return { text: 'C-', color: '#EAB308' };
    if (score >= 67) return { text: 'D+', color: '#F97316' };
    if (score >= 65) return { text: 'D', color: '#F97316' };
    if (score >= 60) return { text: 'D-', color: '#F97316' };
    return { text: 'F', color: '#EF4444' };
  }

  function getVerdict(score) {
    if (score <= 30) return { label: 'Critical', class: 'critical' };
    if (score <= 50) return { label: 'Needs Work', class: 'needs-work' };
    if (score <= 70) return { label: 'Getting There', class: 'getting-there' };
    if (score <= 85) return { label: 'Strong', class: 'strong' };
    return { label: 'Excellent', class: 'excellent' };
  }

  function getScoreColor(score) {
    if (score <= 30) return '#EF4444';
    if (score <= 50) return '#F97316';
    if (score <= 70) return '#F59E0B';
    if (score <= 85) return '#22D3EE';
    return '#22C55E';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function truncate(str, len) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
  }

  function showToast() {
    els.shareToast.classList.add('show');
    setTimeout(function () {
      els.shareToast.classList.remove('show');
    }, 2500);
  }

  // ==========================================
  // INIT
  // ==========================================

  handleRoute();

})();
