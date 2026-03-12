import re

with open('app.js', 'r') as f:
    content = f.read()

# Find the renderEEATPanel function and replace it
old_func_pattern = re.compile(r'  function renderEEATPanel\(data, container\) \{.*?  \}\n', re.DOTALL)

new_func = """  function renderEEATPanel(data, container) {
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
          const val = eeat[\`\${key}_score\`] || 0;
          const color = getScoreColor(val);
          const name = key.charAt(0).toUpperCase() + key.slice(1);
          return \`
            <div style="display:grid; grid-template-columns: 100px 1fr 30px; gap: 12px; align-items: center; font-size: var(--text-sm); font-weight: 600;">
              <span>\${name}</span>
              <div style="background: var(--color-surface-2); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: \${color}; width: \${val}%; height: 100%; border-radius: 4px; transition: width 1s ease-out;"></div>
              </div>
              <span style="text-align:right; color: \${color}">\${val}</span>
            </div>
          \`;
        }).join('')}
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
        ${strengthsHtml}
        ${weaknessesHtml}
      </div>
      ${actionPlanHtml}
    `;
  }
"""

content = old_func_pattern.sub(new_func, content)

with open('app.js', 'w') as f:
    f.write(content)

print("Replaced!")
