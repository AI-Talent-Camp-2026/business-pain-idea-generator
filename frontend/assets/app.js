// API Configuration
// Hardcoded for local development
const API_BASE_URL = 'http://127.0.0.1:8000';

// Utility function to get query parameter
function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Utility function to show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    } else {
        alert(message);
    }
}

// User Story 1: Start run
async function startRun() {
    const direction = document.getElementById('optional-direction')?.value || '';
    const button = document.getElementById('start-button');

    if (button) {
        button.disabled = true;
        button.textContent = 'Запуск...';
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/runs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ optional_direction: direction || undefined })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Ошибка создания прогона');
        }

        const data = await response.json();
        window.location.href = `status.html?run_id=${data.run_id}`;
    } catch (error) {
        showError(`Ошибка: ${error.message}`);
        if (button) {
            button.disabled = false;
            button.textContent = 'Запустить прогон';
        }
    }
}

// User Story 2: Track progress
function trackProgress(runId) {
    console.log(`[Track] Starting progress tracking for run ${runId}`);
    const eventSource = new EventSource(`${API_BASE_URL}/api/runs/${runId}/progress`);

    eventSource.addEventListener('progress', (event) => {
        console.log('[Track] Progress event:', event.data);
        try {
            const data = JSON.parse(event.data);
            updateProgressUI(data);
        } catch (e) {
            console.error('[Track] Error parsing progress event:', e);
        }
    });

    eventSource.addEventListener('complete', (event) => {
        console.log('[Track] Complete event:', event.data);
        try {
            const data = JSON.parse(event.data);
            eventSource.close();
            console.log('[Track] Redirecting to results page...');
            window.location.href = `results.html?run_id=${runId}`;
        } catch (e) {
            console.error('[Track] Error parsing complete event:', e);
            eventSource.close();
            pollRunStatus(runId);
        }
    });

    eventSource.addEventListener('error', (event) => {
        console.log('[Track] Error event:', event);
        try {
            if (event.data) {
                const data = JSON.parse(event.data);
                eventSource.close();
                showError(data.error_message || 'Ошибка генерации');
            }
        } catch (e) {
            console.error('[Track] Error parsing error event:', e);
        }
    });

    eventSource.onerror = (error) => {
        console.warn('[Track] EventSource error, falling back to polling:', error);
        eventSource.close();
        // Fallback to polling
        pollRunStatus(runId);
    };
}

function updateProgressUI(data) {
    const stageElement = document.getElementById('current-stage');
    const progressBar = document.getElementById('progress-bar');

    if (stageElement && data.current_stage) {
        stageElement.textContent = data.current_stage;
    }

    if (progressBar && data.progress_percent !== undefined) {
        progressBar.style.width = `${data.progress_percent}%`;
        progressBar.textContent = `${data.progress_percent}%`;
    }
}

async function pollRunStatus(runId) {
    const maxAttempts = 120; // 10 minutes with 5s intervals
    let attempts = 0;

    const interval = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${API_BASE_URL}/api/runs/${runId}`);
            const data = await response.json();

            updateProgressUI(data);

            if (data.status === 'completed') {
                clearInterval(interval);
                window.location.href = `results.html?run_id=${runId}`;
            } else if (data.status === 'failed') {
                clearInterval(interval);
                showError(data.error_message || 'Прогон завершился с ошибкой');
            } else if (attempts >= maxAttempts) {
                clearInterval(interval);
                showError('Превышено время ожидания');
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 5000);
}

// User Story 3: Load ideas list
async function loadIdeas(runId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/runs/${runId}/ideas`);

        if (!response.ok) {
            throw new Error('Не удалось загрузить идеи');
        }

        const data = await response.json();

        // Display selected direction if available
        if (data.selected_direction) {
            const directionInfo = document.getElementById('direction-info');
            const directionText = document.getElementById('selected-direction');
            if (directionInfo && directionText) {
                directionText.textContent = data.selected_direction;
                directionInfo.classList.remove('hidden');
            }
        }

        displayIdeas(data.ideas);
    } catch (error) {
        showError(`Ошибка загрузки идей: ${error.message}`);
    }
}

function displayIdeas(ideas) {
    const container = document.getElementById('ideas-container');
    if (!container) return;

    container.innerHTML = '';

    ideas.forEach(idea => {
        const card = createIdeaCard(idea);
        container.appendChild(card);
    });
}

function createIdeaCard(idea) {
    const card = document.createElement('div');
    card.className = 'idea-card';
    card.onclick = () => window.location.href = `detail.html?idea_id=${idea.id}`;

    const confidenceBadge = getConfidenceBadge(idea.confidence_level);

    card.innerHTML = `
        <div class="idea-card-header">
            <h3>${escapeHtml(idea.title)}</h3>
            <span class="confidence-badge ${idea.confidence_level}">${confidenceBadge}</span>
        </div>
        <p class="idea-pain">${escapeHtml(idea.pain_description)}</p>
        <p class="idea-segment"><strong>Кому:</strong> ${escapeHtml(idea.segment)}</p>
        <input type="checkbox" class="idea-checkbox" data-idea-id="${idea.id}" onclick="event.stopPropagation()">
    `;

    return card;
}

function getConfidenceBadge(level) {
    const badges = {
        'high': 'Высокий',
        'medium': 'Средний',
        'low': 'Низкий'
    };
    return badges[level] || level;
}

// User Story 4: Load idea details
async function loadIdeaDetail(ideaId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/ideas/${ideaId}`);

        if (!response.ok) {
            throw new Error('Не удалось загрузить детали идеи');
        }

        const idea = await response.json();
        displayIdeaDetail(idea);
    } catch (error) {
        showError(`Ошибка: ${error.message}`);
    }
}

function displayIdeaDetail(idea) {
    document.getElementById('idea-title').textContent = idea.title;
    document.getElementById('confidence-level').textContent = getConfidenceBadge(idea.confidence_level);
    document.getElementById('confidence-level').className = `confidence-badge ${idea.confidence_level}`;

    document.getElementById('pain-description').textContent = idea.pain_description;
    document.getElementById('segment').textContent = idea.segment;
    document.getElementById('brief-evidence').textContent = idea.brief_evidence;

    // Analogues
    const analoguesContainer = document.getElementById('analogues-list');
    analoguesContainer.innerHTML = '';
    idea.analogues.forEach(analogue => {
        const item = document.createElement('div');
        item.className = 'analogue-item';
        item.innerHTML = `
            <h4>${escapeHtml(analogue.name)}</h4>
            <p>${escapeHtml(analogue.description)}</p>
            <a href="${escapeHtml(analogue.url)}" target="_blank" rel="noopener noreferrer">Перейти →</a>
        `;
        analoguesContainer.appendChild(item);
    });

    // Plans
    document.getElementById('plan-7days').textContent = idea.plan_7days;
    document.getElementById('plan-30days').textContent = idea.plan_30days;
}

function toggleDetailedEvidence() {
    const detailedSection = document.getElementById('detailed-evidence');
    const button = document.getElementById('toggle-evidence-button');

    if (detailedSection.style.display === 'none') {
        detailedSection.style.display = 'block';
        button.textContent = 'Скрыть детали';
    } else {
        detailedSection.style.display = 'none';
        button.textContent = 'Подробнее';
    }
}

// User Story 5: Export ideas
async function exportIdeas(runId, selectedOnly = false) {
    try {
        let ideaIds = undefined;

        if (selectedOnly) {
            const checkboxes = document.querySelectorAll('.idea-checkbox:checked');
            ideaIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.ideaId));

            if (ideaIds.length === 0) {
                alert('Выберите хотя бы одну идею');
                return;
            }
        }

        const response = await fetch(`${API_BASE_URL}/api/export/markdown`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ run_id: runId, idea_ids: ideaIds })
        });

        if (!response.ok) {
            throw new Error('Ошибка экспорта');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ideas-${runId}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showError(`Ошибка экспорта: ${error.message}`);
    }
}

// Utility: Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Expose functions globally
window.startRun = startRun;
window.trackProgress = trackProgress;
window.loadIdeas = loadIdeas;
window.loadIdeaDetail = loadIdeaDetail;
window.toggleDetailedEvidence = toggleDetailedEvidence;
window.exportIdeas = exportIdeas;
