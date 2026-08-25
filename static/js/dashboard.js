/**
 * Family Evolution Dashboard - Client Side JavaScript v2.6
 * Dynamic Blueprint Rendering, Longitudinal Evaluations, Informed Consent, and Intervention Tracking.
 */

let moodChart = null;
let evalTrendChart = null;
let botUsername = "";

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadDashboardData();
    loadBlueprint();
    loadEvaluationsAndInterventions();
    loadSettings();
    setupEventListeners();
});

// --- Tab Switching ---
function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const sections = document.querySelectorAll('.tab-section');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.style.display = 'none');

            tab.classList.add('active');
            const targetId = tab.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.style.display = 'block';
                if (targetId === 'tab-blueprint') loadBlueprint();
                if (targetId === 'tab-members') fetchMembersManage();
                if (targetId === 'tab-chores') fetchChoresManage();
                if (targetId === 'tab-habits') fetchHabits();
                if (targetId === 'tab-reports') { fetchStats(); fetchReports(); loadEvaluationsAndInterventions(); }
                if (targetId === 'tab-settings') loadSettings();
            }
        });
    });
}

// --- Toast Feedback Banner ---
function showToast(message, type = 'info') {
    const banner = document.getElementById('toast-banner');
    if (!banner) return;

    banner.style.display = 'block';
    banner.innerText = message;

    if (type === 'success') {
        banner.style.background = 'rgba(52, 211, 153, 0.2)';
        banner.style.border = '1px solid rgba(52, 211, 153, 0.5)';
        banner.style.color = '#34d399';
    } else if (type === 'error') {
        banner.style.background = 'rgba(251, 113, 133, 0.2)';
        banner.style.border = '1px solid rgba(251, 113, 133, 0.5)';
        banner.style.color = '#fb7185';
    } else if (type === 'warning') {
        banner.style.background = 'rgba(251, 191, 36, 0.2)';
        banner.style.border = '1px solid rgba(251, 191, 36, 0.5)';
        banner.style.color = '#fbbf24';
    } else {
        banner.style.background = 'rgba(56, 189, 248, 0.2)';
        banner.style.border = '1px solid rgba(56, 189, 248, 0.5)';
        banner.style.color = '#38bdf8';
    }

    setTimeout(() => {
        banner.style.display = 'none';
    }, 6000);
}

// --- Data Fetching & Dashboard Refresh ---
async function loadDashboardData() {
    try {
        await Promise.all([
            fetchStatus(),
            fetchMembersOverview(),
            fetchTodayChores(),
            fetchStats(),
            fetchReports()
        ]);
    } catch (e) {
        console.error('Error loading dashboard data:', e);
    }
}

async function fetchStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.bot_username) botUsername = data.bot_username;

        const badge = document.getElementById('bot-status-badge');
        const text = document.getElementById('bot-status-text');
        if (badge && text) {
            if (data.bot_configured) {
                badge.className = 'badge badge-green';
                text.innerText = data.bot_username ? `@${data.bot_username} آنلاین` : 'ربات آنلاین';
            } else {
                badge.className = 'badge badge-amber';
                text.innerText = 'ربات بدون توکن';
            }
        }
    } catch (e) {
        console.error('Fetch status error:', e);
    }
}

// --- Blueprint & Goals Loading ---
async function loadBlueprint() {
    try {
        const res = await fetch('/api/setup/template');
        const data = await res.json();

        const profile = data.profile;
        const goals = data.goals || [];

        if (profile) {
            document.getElementById('family-display-title').innerText = profile.family_name || 'سامانه تحول و آرامش خانواده';
            document.getElementById('family-display-overview').innerText = profile.overview || 'هدایت هوشمند وظایف، توانبخشی شناختی سالمند، مهار تنش و ارتقای بهزیستی خانه';
            document.getElementById('bp-family-name').innerText = `🎯 اهداف و نقشه راه: ${profile.family_name || 'خانواده'}`;

            // Communication Rules
            const commList = document.getElementById('comm-rules-list');
            if (commList) {
                const rules = profile.communication_rules || [];
                commList.innerHTML = rules.length > 0 
                    ? rules.map(r => `<li>${r}</li>`).join('')
                    : '<li style="color:var(--text-dim)">قاعده‌ای هنوز ثبت نشده است.</li>';
            }

            // Emergency Resources
            const emergList = document.getElementById('emergency-res-list');
            if (emergList) {
                const ems = profile.emergency_resources || [];
                emergList.innerHTML = ems.length > 0
                    ? ems.map(e => `
                        <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: var(--radius-sm);">
                            <strong style="color: var(--accent-amber);">${e.title}</strong> (${e.phone || 'تماس مستقیم'})<br>
                            <span style="font-size: 0.8rem; color: var(--text-muted);">${e.description || ''}</span>
                        </div>
                    `).join('')
                    : '<div style="color:var(--text-dim); font-size:0.85rem;">مرجع اضطراری ثبت نشده است.</div>';
            }
        }

        // Goals Rendering
        const shortGoals = goals.filter(g => g.goal_type === 'short_term');
        const longGoals = goals.filter(g => g.goal_type === 'long_term');

        const shortCont = document.getElementById('short-term-goals-container');
        const longCont = document.getElementById('long-term-goals-container');

        if (shortCont) {
            shortCont.innerHTML = shortGoals.length > 0 
                ? shortGoals.map(g => `
                    <div style="background: rgba(0,0,0,0.25); padding: 14px; border-radius: var(--radius-md); border: 1px solid rgba(52,211,153,0.2);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <h4 style="font-weight:700; color:var(--accent-emerald); font-size:1rem;">${g.title}</h4>
                            <span style="font-size:0.75rem; color:var(--text-dim);">${g.target_date || ''}</span>
                        </div>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:10px;">${g.description || ''}</p>
                        ${g.steps && g.steps.length > 0 ? `
                            <div style="font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:8px;">
                                <strong>گام‌های اقدام:</strong>
                                <ul style="padding-right:16px; margin-top:4px;">
                                    ${g.steps.map(s => `<li>${s}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                `).join('')
                : '<div style="color:var(--text-dim); font-size:0.85rem;">هدفی ثبت نشده است. عامل هوشمند در حین مصاحبه اهداف را تکمیل خواهد کرد.</div>';
        }

        if (longCont) {
            longCont.innerHTML = longGoals.length > 0 
                ? longGoals.map(g => `
                    <div style="background: rgba(0,0,0,0.25); padding: 14px; border-radius: var(--radius-md); border: 1px solid rgba(192,132,252,0.2);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <h4 style="font-weight:700; color:var(--accent-purple); font-size:1rem;">${g.title}</h4>
                            <span style="font-size:0.75rem; color:var(--text-dim);">${g.target_date || ''}</span>
                        </div>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:10px;">${g.description || ''}</p>
                        ${g.steps && g.steps.length > 0 ? `
                            <div style="font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:8px;">
                                <strong>مسیر پیشرفت:</strong>
                                <ul style="padding-right:16px; margin-top:4px;">
                                    ${g.steps.map(s => `<li>${s}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                `).join('')
                : '<div style="color:var(--text-dim); font-size:0.85rem;">چشم‌انداز بلندمدتی هنوز ثبت نشده است.</div>';
        }

    } catch (e) {
        console.error('Error loading blueprint:', e);
    }
}

// --- Longitudinal Clinical Evaluations & Interventions ---
async function loadEvaluationsAndInterventions() {
    try {
        const trendRes = await fetch('/api/evaluations/trends');
        const trendData = await trendRes.json();

        const trends = trendData.trends || [];
        if (trends.length > 0) {
            const latest = trends[trends.length - 1];
            const safetyEl = document.getElementById('eval-stat-safety');
            const respectEl = document.getElementById('eval-stat-respect');
            const careEl = document.getElementById('eval-stat-care');
            const climateEl = document.getElementById('eval-stat-climate');

            if (safetyEl) safetyEl.innerText = `${latest.avg_safety ? latest.avg_safety.toFixed(1) : '-'} / ۵`;
            if (respectEl) respectEl.innerText = `${latest.avg_respect ? latest.avg_respect.toFixed(1) : '-'} / ۵`;
            if (careEl) careEl.innerText = `${latest.avg_care ? latest.avg_care.toFixed(1) : '-'} / ۵`;
            if (climateEl) climateEl.innerText = `${latest.avg_climate ? latest.avg_climate.toFixed(1) : '-'} / ۵`;
        }

        renderEvalTrendChart(trends);

        // Interventions History
        const intRes = await fetch('/api/interventions/history');
        const intHistory = await intRes.json();
        const intCont = document.getElementById('interventions-history-container');
        if (intCont) {
            if (intHistory.length === 0) {
                intCont.innerHTML = '<div style="color:var(--text-dim); font-size:0.85rem;">هنوز تغییر ساختاری ثبت نشده است. سیستم با بررسی ارزیابی‌های ماهانه به صورت خودکار مداخله‌ها را تطبیق می‌دهد.</div>';
            } else {
                intCont.innerHTML = intHistory.map(item => `
                    <div style="background: rgba(0,0,0,0.25); padding: 12px 16px; border-radius: var(--radius-sm); border-right: 3px solid var(--accent-blue);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <strong style="color:var(--accent-blue); font-size:0.95rem;">${item.trigger_reason}</strong>
                            <span style="font-size:0.75rem; color:var(--text-dim);">${item.date}</span>
                        </div>
                        <p style="font-size:0.85rem; color:var(--text-main); margin-bottom:4px;">${item.rationale || ''}</p>
                    </div>
                `).join('');
            }
        }

    } catch (e) {
        console.error('Error loading evaluations:', e);
    }
}

function renderEvalTrendChart(trends) {
    const ctx = document.getElementById('evalTrendChart');
    if (!ctx) return;

    if (evalTrendChart) evalTrendChart.destroy();
    if (!trends || trends.length === 0) return;

    const labels = trends.map(t => t.date);
    const safetyData = trends.map(t => t.avg_safety);
    const respectData = trends.map(t => t.avg_respect);
    const careData = trends.map(t => t.avg_care);

    evalTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'امنیت روانی',
                    data: safetyData,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'احترام و جایگاه',
                    data: respectData,
                    borderColor: '#c084fc',
                    backgroundColor: 'rgba(192, 132, 252, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'حمایت و مراقبت ادراک‌شده',
                    data: careData,
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 1, max: 5, grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#f8fafc', font: { family: 'Vazirmatn' } } }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc', font: { family: 'Vazirmatn' } } }
            }
        }
    });
}

// --- Members: Overview & Full CRUD ---
async function fetchMembersOverview() {
    const res = await fetch('/api/members');
    const members = await res.json();
    const container = document.getElementById('members-overview-container');
    if (!container) return;

    if (members.length === 0) {
        container.innerHTML = `
            <div class="glass-panel" style="grid-column: 1 / -1; text-align: center; padding: 36px;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🌱</div>
                <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">به سامانه خانواده‌یار خوش آمدید!</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 20px; max-width: 650px; margin-left: auto; margin-right: auto; line-height: 1.7;">
                    هنوز عضوی ثبت نشده است. برای راه‌اندازی، می‌توانید در چت <strong>عامل هوشمند (Agent Manager)</strong> به سوالات مصاحبه تشخیصی مهارت <code>family-evolution</code> پاسخ دهید تا اهداف، اعضا و تقویم وظایف به صورت خودکار در این داشبورد مقداردهی شوند.
                </p>
                <div style="display: flex; justify-content: center; gap: 12px;">
                    <button class="btn-glass btn-emerald" onclick="openModal('modal-add-member')">➕ افزودن دستی عضو</button>
                    <button class="btn-glass" onclick="openModal('modal-add-chore')">➕ افزودن کار خانه</button>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = members.map(m => {
        const directLink = botUsername ? `https://t.me/${botUsername}?start=member_${m.id}` : '#';
        const consentBadge = m.consent_given 
            ? '<span style="color:var(--accent-emerald); font-size:0.75rem;">رضایت: تایید شد ✅</span>' 
            : '<span style="color:var(--accent-amber); font-size:0.75rem;">در انتظار تایید منشور ⏳</span>';

        return `
            <div class="glass-panel member-card">
                <div class="member-card-header">
                    <div class="member-avatar">${m.avatar || '👤'}</div>
                    <div class="member-info min-w-0">
                        <h4>${m.name_fa} <span style="font-size: 0.8rem; color: var(--text-muted)">(${m.age ? m.age + ' سال' : ''})</span></h4>
                        <div class="member-role">${getRoleBadge(m.role)}</div>
                    </div>
                </div>
                <div class="member-condition">
                    ${m.conditions || 'بدون توضیحات بالینی'}
                </div>
                <div class="member-stats">
                    <span>
                        ${m.telegram_id 
                            ? '<span style="color:var(--accent-emerald)">تلگرام: متصل ✅</span>' 
                            : (botUsername ? `<a href="${directLink}" target="_blank" style="color:var(--accent-blue); text-decoration:none; font-weight:600;">🔗 اتصال به تلگرام</a>` : '<span>بدون اتصال</span>')
                        }
                    </span>
                    <span>${consentBadge}</span>
                </div>
            </div>
        `;
    }).join('');

    populateMemberSelects(members);
}

async function fetchMembersManage() {
    const res = await fetch('/api/members');
    const members = await res.json();
    const container = document.getElementById('members-full-list');
    if (!container) return;

    if (members.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); padding: 20px;">هیچ عضوی ثبت نشده است. روی «افزودن عضو جدید» کلیک کنید.</div>';
        return;
    }

    container.innerHTML = members.map(m => {
        const directLink = botUsername ? `https://t.me/${botUsername}?start=member_${m.id}` : '#';
        return `
            <div class="glass-panel" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="member-avatar">${m.avatar || '👤'}</div>
                            <div>
                                <h4 style="font-size: 1.1rem; font-weight: 700;">${m.name_fa} (${m.name})</h4>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">${m.age ? m.age + ' ساله • ' : ''}${getRoleBadge(m.role)}</div>
                            </div>
                        </div>
                        <div>
                            <button class="btn-glass" style="padding: 4px 8px; font-size: 0.75rem;" onclick="openEditMember(${JSON.stringify(m).replace(/"/g, '&quot;')})">✏️</button>
                            <button class="btn-glass" style="padding: 4px 8px; font-size: 0.75rem; color: var(--accent-rose);" onclick="deleteMember(${m.id})">🗑️</button>
                        </div>
                    </div>
                    <div style="background: rgba(0,0,0,0.25); padding: 10px; border-radius: var(--radius-sm); font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
                        <strong>چالش‌ها:</strong> ${m.conditions || 'ثبت نشده'}
                    </div>
                    ${m.medical_history ? `
                        <div style="background: rgba(56,189,248,0.08); padding: 8px 10px; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--accent-blue); margin-bottom: 12px;">
                            <strong>🩺 سابقه پزشکی:</strong> ${m.medical_history}
                        </div>
                    ` : ''}
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; font-size: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        ${m.telegram_id 
                            ? `<span style="color:var(--accent-emerald)">تلگرام: ${m.telegram_id}</span> <button class="btn-glass" style="padding:2px 6px; font-size:0.7rem;" onclick="unbindTelegram(${m.id})">قطع</button>` 
                            : (botUsername ? `<a href="${directLink}" target="_blank" class="btn-glass btn-primary" style="padding:4px 10px; font-size:0.75rem;">📱 لینک اتصال تلگرام</a>` : '<span>بدون ربات</span>')
                        }
                    </div>
                    <span>${m.consent_given ? '✅ رضایت ثبت شد' : '⏳ بدون رضایت'}</span>
                </div>
            </div>
        `;
    }).join('');
}

function getRoleBadge(role) {
    const map = {
        'father': '<span class="badge badge-purple">پدر / سالمند</span>',
        'mother': '<span class="badge" style="background:rgba(251,113,133,0.15);color:var(--accent-rose)">مادر / مدیر خانه</span>',
        'sister': '<span class="badge badge-blue">خواهر / همیار</span>',
        'brother': '<span class="badge badge-amber">برادر / لجستیک</span>',
        'user': '<span class="badge badge-green">راهبر سیستم</span>',
        'child': '<span class="badge badge-blue">فرزند</span>'
    };
    return map[role] || `<span class="badge badge-blue">${role}</span>`;
}

function populateMemberSelects(members) {
    const selects = ['chore-assignee-select', 'habit-member-select'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = members.map(m => `<option value="${m.id}">${m.avatar} ${m.name_fa} (${m.role})</option>`).join('');
        }
    });
}

// --- Member Actions ---
async function deleteMember(memberId) {
    if (!confirm('آیا از حذف این عضو و وظایف مربوطه مطمئن هستید؟')) return;
    const res = await fetch(`/api/members/${memberId}`, { method: 'DELETE' });
    if (res.ok) {
        showToast('عضو با موفقیت حذف شد.', 'success');
        loadDashboardData();
        fetchMembersManage();
    }
}

function openEditMember(member) {
    document.getElementById('edit-member-id').value = member.id;
    document.getElementById('edit-member-name-fa').value = member.name_fa;
    document.getElementById('edit-member-name-en').value = member.name;
    document.getElementById('edit-member-role').value = member.role;
    document.getElementById('edit-member-age').value = member.age || '';
    document.getElementById('edit-member-avatar').value = member.avatar || '👤';
    document.getElementById('edit-member-conditions').value = member.conditions || '';
    document.getElementById('edit-member-medical-history').value = member.medical_history || '';
    openModal('modal-edit-member');
}

async function unbindTelegram(memberId) {
    await fetch(`/api/members/${memberId}/unbind`, { method: 'POST' });
    showToast('اتصال حساب تلگرام قطع شد.', 'info');
    fetchMembersManage();
    fetchMembersOverview();
}

// --- Chores CRUD & Management ---
async function fetchTodayChores() {
    const res = await fetch('/api/chores/today');
    const chores = await res.json();
    const container = document.getElementById('today-chores-list');
    if (!container) return;

    if (chores.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 20px;">امروز وظیفه‌ای در تقویم ثبت نشده است.</div>';
        return;
    }

    container.innerHTML = chores.map(c => `
        <div class="chore-item ${c.status === 'done' ? 'done' : ''}">
            <div class="chore-title min-w-0">
                <span class="chore-icon">${c.icon || '📋'}</span>
                <div>
                    <div style="font-weight: 600;">${c.title_fa}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">${c.category} • ${c.difficulty || 'متوسط'}</div>
                </div>
            </div>
            <div class="chore-assignee">
                <span>${c.avatar || '👤'} ${c.name_fa}</span>
                <button class="btn-glass ${c.status === 'done' ? 'btn-emerald' : ''}" 
                        style="padding: 6px 14px; font-size: 0.8rem;" 
                        onclick="toggleChore(${c.schedule_id}, '${c.status === 'done' ? 'pending' : 'done'}')">
                    ${c.status === 'done' ? '✅ انجام شد' : '⏳ ثبت انجام'}
                </button>
            </div>
        </div>
    `).join('');
}

async function fetchChoresManage() {
    const res = await fetch('/api/chores');
    const chores = await res.json();
    const container = document.getElementById('chores-manage-list');
    if (!container) return;

    if (chores.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); padding: 20px;">هیچ وظیفه‌ای ثبت نشده است.</div>';
        return;
    }

    container.innerHTML = chores.map(c => `
        <div class="chore-item">
            <div class="chore-title min-w-0">
                <span class="chore-icon">${c.icon || '📋'}</span>
                <div>
                    <div style="font-weight: 600;">${c.title_fa}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        دسته‌بندی: ${c.category} • تکرار: ${c.frequency} • مسئول پیش‌فرض: ${c.assignee_name_fa || 'تعیین نشده'}
                    </div>
                </div>
            </div>
            <div>
                <button class="btn-glass" style="padding: 4px 8px; font-size: 0.75rem; color: var(--accent-rose);" onclick="deleteChore(${c.id})">🗑️ حذف</button>
            </div>
        </div>
    `).join('');
}

async function toggleChore(scheduleId, newStatus) {
    await fetch('/api/chores/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schedule_id: scheduleId, status: newStatus })
    });
    loadDashboardData();
}

async function deleteChore(choreId) {
    if (!confirm('آیا از حذف این کار از تقویم مطمئن هستید؟')) return;
    await fetch(`/api/chores/${choreId}`, { method: 'DELETE' });
    showToast('کار با موفقیت حذف شد.', 'success');
    fetchChoresManage();
    fetchTodayChores();
}

// --- Habits CRUD ---
async function fetchHabits() {
    const res = await fetch('/api/habits');
    const habitGroups = await res.json();
    const container = document.getElementById('habits-container');
    if (!container) return;

    if (habitGroups.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); padding: 20px;">هیچ عادتی ثبت نشده است.</div>';
        return;
    }

    container.innerHTML = habitGroups.map(g => `
        <div class="glass-panel" style="margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                <span style="font-size: 1.5rem;">${g.member.avatar || '👤'}</span>
                <h3 style="font-size: 1.1rem; font-weight: 700;">${g.member.name_fa}</h3>
                ${getRoleBadge(g.member.role)}
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px;">
                ${g.habits.length === 0 ? '<div style="color:var(--text-dim); font-size:0.85rem;">عادتی برای این عضو ثبت نشده است.</div>' : ''}
                ${g.habits.map(h => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.25); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid rgba(255,255,255,0.05);">
                        <div>
                            <div style="font-weight: 500; font-size: 0.9rem;">${h.title_fa}</div>
                            <div style="font-size: 0.75rem; color: var(--text-dim);">${h.category} • ${h.reminder_time || 'روزانه'}</div>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <button class="btn-glass ${h.today_status === 'done' ? 'btn-emerald' : ''}" 
                                    style="padding: 4px 10px; font-size: 0.75rem;"
                                    onclick="toggleHabit(${h.id}, ${g.member.id})">
                                ${h.today_status === 'done' ? '✅' : '⭕'}
                            </button>
                            <button class="btn-glass" style="padding: 4px 6px; font-size: 0.7rem; color: var(--accent-rose);" onclick="deleteHabit(${h.id})">✕</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

async function toggleHabit(habitId, memberId) {
    await fetch('/api/habits/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit_id: habitId, member_id: memberId })
    });
    fetchHabits();
}

async function deleteHabit(habitId) {
    await fetch(`/api/habits/${habitId}`, { method: 'DELETE' });
    showToast('عادت حذف شد.', 'info');
    fetchHabits();
}

// --- Real Stats & Charts (No Fake Data) ---
async function fetchStats() {
    const res = await fetch('/api/stats?days=7');
    const data = await res.json();

    const moodEl = document.getElementById('stat-avg-mood');
    const choreEl = document.getElementById('stat-chore-rate');
    const conflictEl = document.getElementById('stat-conflicts');

    if (moodEl) moodEl.innerText = data.avg_mood !== null ? `${data.avg_mood} / ۵` : 'ثبت نشده';
    if (choreEl) choreEl.innerText = data.chore_completion_rate !== null ? `${data.chore_completion_rate}٪` : 'ثبت نشده';
    if (conflictEl) conflictEl.innerText = `${data.conflict_count} مورد`;

    renderMoodChart(data.member_moods);
}

function renderMoodChart(memberMoods) {
    const ctx = document.getElementById('moodChart');
    if (!ctx) return;

    const validMembers = (memberMoods || []).filter(m => m.member_avg_mood !== null);
    if (validMembers.length === 0) {
        if (moodChart) moodChart.destroy();
        return;
    }

    const labels = validMembers.map(m => m.name_fa);
    const scores = validMembers.map(m => m.member_avg_mood);

    if (moodChart) moodChart.destroy();

    moodChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'میانگین خلق‌وخو (۱ تا ۵)',
                data: scores,
                backgroundColor: 'rgba(56, 189, 248, 0.6)',
                borderColor: 'rgba(56, 189, 248, 1)',
                borderWidth: 1.5,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 1, max: 5, grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#f8fafc', font: { family: 'Vazirmatn' } } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// --- Reports ---
async function fetchReports() {
    const res = await fetch('/api/reports?limit=3');
    const reports = await res.json();
    const container = document.getElementById('recent-reports-container');
    if (!container) return;

    if (reports.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 20px;">هنوز گزارشی ثبت نشده است. با زدن دکمه «اجرای فوری تحلیل هوش مصنوعی» نخستین گزارش را تولید کنید.</div>';
        return;
    }

    container.innerHTML = reports.map(r => `
        <div style="background: rgba(0,0,0,0.25); padding: 16px; border-radius: var(--radius-md); border: 1px solid rgba(255,255,255,0.06); margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-purple">${r.report_type === 'weekly' ? 'تحلیل هفتگی' : 'طرح تکاملی'}</span>
                <span style="font-size: 0.75rem; color: var(--text-dim);">${r.created_at}</span>
            </div>
            <div style="font-size: 0.9rem; line-height: 1.6; white-space: pre-line; color: var(--text-main);">
                ${r.summary_fa || r.summary_en}
            </div>
        </div>
    `).join('');
}

// --- Settings & Diagnostics ---
async function loadSettings() {
    const res = await fetch('/api/config');
    const cfg = await res.json();

    const setToken = document.getElementById('setting-telegram-token');
    const setProxy = document.getElementById('setting-telegram-proxy');
    const setUseProxy = document.getElementById('setting-use-proxy');
    const setProvider = document.getElementById('setting-llm-provider');
    const setUrl = document.getElementById('setting-llm-url');
    const setModel = document.getElementById('setting-llm-model');
    const setKey = document.getElementById('setting-llm-key');
    const setGemini = document.getElementById('setting-gemini-key');

    if (setToken) setToken.value = cfg.telegram_bot_token || '';
    if (setProxy) setProxy.value = cfg.telegram_proxy || '';
    if (setUseProxy) setUseProxy.value = cfg.use_proxy ? 'true' : 'false';
    if (setProvider) setProvider.value = cfg.llm_provider || 'openai_compatible';
    if (setUrl) setUrl.value = cfg.llm_base_url || 'http://localhost:20128/v1';
    if (setModel) setModel.value = cfg.llm_model || 'gemini-2.5-flash';
    if (setKey) setKey.value = cfg.llm_api_key || '';
    if (setGemini) setGemini.value = cfg.gemini_api_key || '';
}

// --- Event Listeners ---
function setupEventListeners() {
    // Add Member Form
    const addMemberForm = document.getElementById('form-add-member');
    if (addMemberForm) {
        addMemberForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('member-name-en').value,
                name_fa: document.getElementById('member-name-fa').value,
                role: document.getElementById('member-role').value,
                age: parseInt(document.getElementById('member-age').value) || null,
                avatar: document.getElementById('member-avatar').value || '👤',
                conditions: document.getElementById('member-conditions').value,
                medical_history: document.getElementById('member-medical-history').value,
                is_leader: document.getElementById('member-is-leader').checked ? 1 : 0,
                is_co_leader: document.getElementById('member-is-co-leader').checked ? 1 : 0
            };
            await fetch('/api/members', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            closeModal('modal-add-member');
            showToast('عضو جدید با موفقیت اضافه شد.', 'success');
            loadDashboardData();
            fetchMembersManage();
        });
    }

    // Edit Member Form
    const editMemberForm = document.getElementById('form-edit-member');
    if (editMemberForm) {
        editMemberForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const memberId = document.getElementById('edit-member-id').value;
            const payload = {
                name: document.getElementById('edit-member-name-en').value,
                name_fa: document.getElementById('edit-member-name-fa').value,
                role: document.getElementById('edit-member-role').value,
                age: parseInt(document.getElementById('edit-member-age').value) || null,
                avatar: document.getElementById('edit-member-avatar').value || '👤',
                conditions: document.getElementById('edit-member-conditions').value,
                medical_history: document.getElementById('edit-member-medical-history').value
            };
            await fetch(`/api/members/${memberId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            closeModal('modal-edit-member');
            showToast('مشخصات عضو بروزرسانی شد.', 'success');
            loadDashboardData();
            fetchMembersManage();
        });
    }

    // Add Chore Form
    const addChoreForm = document.getElementById('form-add-chore');
    if (addChoreForm) {
        addChoreForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                title_fa: document.getElementById('chore-title-fa').value,
                category: document.getElementById('chore-category').value,
                frequency: document.getElementById('chore-frequency').value,
                default_assignee_id: parseInt(document.getElementById('chore-assignee-select').value) || null,
                icon: document.getElementById('chore-icon').value || '📋'
            };
            await fetch('/api/chores/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            closeModal('modal-add-chore');
            showToast('وظیفه جدید با موفقیت در تقویم ثبت شد.', 'success');
            loadDashboardData();
            fetchChoresManage();
        });
    }

    // Add Habit Form
    const addHabitForm = document.getElementById('form-add-habit');
    if (addHabitForm) {
        addHabitForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                title_fa: document.getElementById('habit-title-fa').value,
                member_id: parseInt(document.getElementById('habit-member-select').value),
                category: document.getElementById('habit-category').value
            };
            await fetch('/api/habits/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            closeModal('modal-add-habit');
            showToast('عادت جدید با موفقیت ثبت شد.', 'success');
            fetchHabits();
        });
    }

    // Log Conflict Form
    const conflictForm = document.getElementById('form-log-conflict');
    if (conflictForm) {
        conflictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                involved: document.getElementById('conflict-involved').value,
                trigger: document.getElementById('conflict-trigger').value,
                severity: parseInt(document.getElementById('conflict-severity').value)
            };
            await fetch('/api/conflicts/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            closeModal('modal-log-conflict');
            showToast('رویداد تعارض ثبت شد.', 'info');
            fetchStats();
        });
    }

    // Settings Form
    const settingsForm = document.getElementById('form-settings');
    if (settingsForm) {
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                telegram_bot_token: document.getElementById('setting-telegram-token').value,
                telegram_proxy: document.getElementById('setting-telegram-proxy').value,
                use_proxy: document.getElementById('setting-use-proxy').value === 'true',
                llm_provider: document.getElementById('setting-llm-provider').value,
                llm_base_url: document.getElementById('setting-llm-url').value,
                llm_model: document.getElementById('setting-llm-model').value,
                llm_api_key: document.getElementById('setting-llm-key').value,
                gemini_api_key: document.getElementById('setting-gemini-key').value
            };
            await fetch('/api/config/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            showToast('تنظیمات با موفقیت ذخیره و بارگذاری شد.', 'success');
            fetchStatus();
        });
    }

    // Reset Database
    const resetBtn = document.getElementById('btn-reset-db');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (!confirm('هشدار: تمامی اعضا، وظایف و اهداف ثبت شده پاک خواهند شد. آیا ادامه می‌دهید؟')) return;
            await fetch('/api/setup/reset-database', { method: 'POST' });
            showToast('پایگاه داده به طور کامل پاکسازی شد.', 'warning');
            loadDashboardData();
            loadBlueprint();
            loadEvaluationsAndInterventions();
            fetchMembersManage();
            fetchChoresManage();
        });
    }

    // Test Telegram Connection
    const testTgBtn = document.getElementById('btn-test-telegram');
    if (testTgBtn) {
        testTgBtn.addEventListener('click', async () => {
            testTgBtn.disabled = true;
            testTgBtn.innerText = 'در حال تست...';
            try {
                const res = await fetch('/api/telegram/test-connection', { method: 'POST' });
                const data = await res.json();
                if (data.ok) {
                    showToast(`اتصال به تلگرام موفق بود! ربات: @${data.username} (${data.first_name})`, 'success');
                } else {
                    showToast(`خطا در اتصال تلگرام: ${data.error}`, 'error');
                }
            } catch (e) {
                showToast(`خطا: ${e}`, 'error');
            } finally {
                testTgBtn.disabled = false;
                testTgBtn.innerText = '🔍 تست اتصال به تلگرام';
            }
        });
    }

    // Test AI Connection
    const testAiBtn = document.getElementById('btn-test-ai');
    if (testAiBtn) {
        testAiBtn.addEventListener('click', async () => {
            testAiBtn.disabled = true;
            testAiBtn.innerText = 'در حال تست هوش مصنوعی...';
            try {
                const res = await fetch('/api/ai/test-connection', { method: 'POST' });
                const data = await res.json();
                if (data.ok) {
                    showToast(`ارتباط با مدل ${data.model} برقرار است. پاسخ: «${data.response}»`, 'success');
                } else {
                    showToast(`خطا در ارتباط هوش مصنوعی: ${data.error}`, 'error');
                }
            } catch (e) {
                showToast(`خطا: ${e}`, 'error');
            } finally {
                testAiBtn.disabled = false;
                testAiBtn.innerText = '🔍 تست ارتباط با هوش مصنوعی';
            }
        });
    }

    // Telegram Action Triggers
    const morningBtn = document.getElementById('btn-trigger-morning');
    if (morningBtn) {
        morningBtn.addEventListener('click', async () => {
            const res = await fetch('/api/telegram/trigger-morning', { method: 'POST' });
            const data = await res.json();
            if (data.sent_count > 0) {
                showToast(`احوالپرسی صبحگاهی به ${data.sent_count} عضو ارسال شد: (${data.sent_to.join(', ')})`, 'success');
            } else if (data.unlinked_members && data.unlinked_members.length > 0) {
                showToast(`پیام ارسال نشد: هنوز اعضا (${data.unlinked_members.join('، ')}) به ربات تلگرام متصل نشده‌اند.`, 'warning');
            } else {
                showToast('هیچ عضوی در سامانه ثبت نشده است.', 'warning');
            }
        });
    }

    const eveningBtn = document.getElementById('btn-trigger-evening');
    if (eveningBtn) {
        eveningBtn.addEventListener('click', async () => {
            const res = await fetch('/api/telegram/trigger-evening', { method: 'POST' });
            const data = await res.json();
            if (data.sent_count > 0) {
                showToast(`بررسی عصرگاهی به ${data.sent_count} عضو ارسال شد: (${data.sent_to.join(', ')})`, 'success');
            } else if (data.unlinked_members && data.unlinked_members.length > 0) {
                showToast(`پیام ارسال نشد: هنوز اعضا (${data.unlinked_members.join('، ')}) به ربات تلگرام متصل نشده‌اند.`, 'warning');
            } else {
                showToast('عضوی ثبت نشده است.', 'warning');
            }
        });
    }

    const monthlyTrigger = document.getElementById('btn-trigger-monthly');
    if (monthlyTrigger) {
        monthlyTrigger.addEventListener('click', async () => {
            const res = await fetch('/api/scheduler/trigger-monthly-evaluations', { method: 'POST' });
            const data = await res.json();
            if (data.dispatched && data.dispatched.sent_count > 0) {
                showToast(`ارزیابی ماهانه برای ${data.dispatched.sent_count} عضو ارسال شد.`, 'success');
            } else {
                showToast(`پیام ارسال نشد: هنوز عضوی به ربات تلگرام متصل نشده است.`, 'warning');
            }
        });
    }

    const monthlyEvalBtn = document.getElementById('btn-trigger-monthly-eval');
    if (monthlyEvalBtn) {
        monthlyEvalBtn.addEventListener('click', async () => {
            const res = await fetch('/api/scheduler/trigger-monthly-evaluations', { method: 'POST' });
            const data = await res.json();
            if (data.dispatched && data.dispatched.sent_count > 0) {
                showToast(`ارزیابی ماهانه برای ${data.dispatched.sent_count} عضو ارسال شد.`, 'success');
            } else {
                showToast(`پیام ارسال نشد: هنوز عضوی به ربات تلگرام متصل نشده است.`, 'warning');
            }
        });
    }

    const broadcastBtn = document.getElementById('btn-send-broadcast');
    if (broadcastBtn) {
        broadcastBtn.addEventListener('click', async () => {
            const msg = document.getElementById('broadcast-text').value.trim();
            if (!msg) return;
            const res = await fetch('/api/telegram/broadcast', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            if (data.sent_count > 0) {
                showToast(`پیام به ${data.sent_count} عضو ارسال شد.`, 'success');
            } else {
                showToast(`پیام ارسال نشد: کاربری در تلگرام متصل نشده است.`, 'warning');
            }
            closeModal('modal-broadcast');
        });
    }

    const runAnalysisBtn = document.getElementById('btn-run-analysis');
    if (runAnalysisBtn) {
        runAnalysisBtn.addEventListener('click', async () => {
            runAnalysisBtn.disabled = true;
            runAnalysisBtn.innerText = 'در حال تحلیل...';
            try {
                await fetch('/api/analysis/run', { method: 'POST' });
                showToast('تحلیل روانشناختی انجام شد و در بخش گزارش‌ها ثبت گردید.', 'success');
                loadDashboardData();
                loadEvaluationsAndInterventions();
            } catch (e) {
                showToast('خطا در تحلیل: ' + e, 'error');
            } finally {
                runAnalysisBtn.disabled = false;
                runAnalysisBtn.innerText = '🧠 اجرای فوری تحلیل هوش مصنوعی';
            }
        });
    }
}

// --- Modal Utilities ---
function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('active');
}
