let currentJobs = [];
let selectedJobId = null;
let includeInternships = false;

// Fonction pour obtenir la classe de couleur selon le score IA
function getScoreClass(score) {
    if (score < 0.15) return 'excellent';
    if (score < 0.2) return 'good';
    if (score < 0.3) return 'medium';
    if (score < 0.4) return 'poor';
    return 'bad';
}

// Fonction pour formater le score
function formatScore(score) {
    return score.toFixed(3);
}

// Charger les dates disponibles
async function loadDates() {
    try {
        const response = await fetch('/api/dates');
        const dates = await response.json();
        
        const selector = document.getElementById('date-selector');
        selector.innerHTML = '';
        
        dates.forEach((date, index) => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = formatDate(date);
            if (index === 0) option.selected = true;
            selector.appendChild(option);
        });
        
        // Charger les offres de la première date
        if (dates.length > 0) {
            loadJobs(dates[0]);
        }
    } catch (error) {
        console.error('Erreur lors du chargement des dates:', error);
        showError('Impossible de charger les dates disponibles');
    }
}

// Formater la date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
}

// Charger les offres pour une date donnée
async function loadJobs(date) {
    try {
        showLoading();
        const includeInternshipsParam = includeInternships ? 'true' : 'false';
        const response = await fetch(`/api/jobs?date=${encodeURIComponent(date)}&include_internships=${includeInternshipsParam}`);
        currentJobs = await response.json();
        
        displayJobList(currentJobs);
        updateJobCount(currentJobs.length);
        
        // Sélectionner automatiquement la première offre
        if (currentJobs.length > 0) {
            selectJob(currentJobs[0].id);
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des offres:', error);
        showError('Impossible de charger les offres d\'emploi');
    }
}

// Afficher la liste des offres
function displayJobList(jobs) {
    const jobList = document.getElementById('job-list');
    
    if (jobs.length === 0) {
        jobList.innerHTML = `
            <div class="empty-state">
                <p>Aucune offre disponible pour cette date</p>
            </div>
        `;
        return;
    }
    
    jobList.innerHTML = jobs.map((job, index) => `
        <div class="job-card" data-job-id="${job.id}" style="animation-delay: ${index * 0.05}s">
            <div class="job-card-header">
                <h3 class="job-card-title">${escapeHtml(job.title)}</h3>
                <span class="ai-score-badge ${getScoreClass(job.ai_score)}">
                    ${formatScore(job.ai_score)}
                </span>
            </div>
            <div class="job-card-company">
                ${job.company_logo ? `<img src="${job.company_logo}" alt="${escapeHtml(job.company)}" class="company-logo" onerror="this.style.display='none'">` : ''}
                <span>${escapeHtml(job.company)}</span>
            </div>
        </div>
    `).join('');
    
    // Ajouter les événements de clic
    document.querySelectorAll('.job-card').forEach(card => {
        card.addEventListener('click', () => {
            const jobId = card.dataset.jobId;
            selectJob(jobId);
        });
    });
}

// Sélectionner une offre
function selectJob(jobId) {
    selectedJobId = jobId;
    
    // Mettre à jour l'état actif dans la liste
    document.querySelectorAll('.job-card').forEach(card => {
        card.classList.toggle('active', card.dataset.jobId === jobId);
    });
    
    // Afficher les détails
    const job = currentJobs.find(j => j.id === jobId);
    if (job) {
        displayJobDetail(job);
    }
}

// Afficher les détails d'une offre
function displayJobDetail(job) {
    const detailPanel = document.getElementById('job-detail');
    
    const primaryLink = job.job_url_direct || job.job_url;
    const hasSecondaryLink = job.job_url_direct && job.job_url;
    
    // Template des boutons
    const applyButtons = `
        <div class="detail-section">
            <h3>Postuler</h3>
            <div class="detail-links">
                ${primaryLink ? `
                    <a href="${primaryLink}" target="_blank" rel="noopener noreferrer" class="detail-link">
                        Voir l'offre complète →
                    </a>
                ` : ''}
                ${hasSecondaryLink ? `
                    <a href="${job.job_url}" target="_blank" rel="noopener noreferrer" class="detail-link secondary">
                        Voir sur ${getSiteName(job.job_url)} →
                    </a>
                ` : ''}
            </div>
        </div>
    `;
    
    detailPanel.innerHTML = `
        <div class="detail-header">
            ${job.company_logo ? `
                <div class="detail-company">
                    <img src="${job.company_logo}" alt="${escapeHtml(job.company)}" class="detail-company-logo" onerror="this.style.display='none'">
                    <div class="detail-company-info">
                        <h3>${escapeHtml(job.company)}</h3>
                        <p>${escapeHtml(job.location || 'Localisation non spécifiée')}</p>
                    </div>
                </div>
            ` : `
                <div class="detail-company">
                    <div class="detail-company-info">
                        <h3>${escapeHtml(job.company)}</h3>
                        <p>${escapeHtml(job.location || 'Localisation non spécifiée')}</p>
                    </div>
                </div>
            `}
            
            <h1 class="detail-title">${escapeHtml(job.title)}</h1>
            
            <div class="detail-meta">
                <span class="ai-score-large ${getScoreClass(job.ai_score)}">
                    Score IA: ${formatScore(job.ai_score)}
                </span>
                ${job.job_type ? `<span class="meta-item">${escapeHtml(job.job_type)}</span>` : ''}
                ${job.date_posted ? `<span class="meta-item">Publié: ${formatDate(job.date_posted)}</span>` : ''}
            </div>
        </div>
        
        ${applyButtons}
        
        <div class="detail-section">
            <h3>Description du poste</h3>
            <div class="detail-description">${marked.parse(job.description || 'Description non disponible')}</div>
        </div>
        
        ${job.ai_skills_required ? `
            <div class="detail-section">
                <h3>Compétences requises</h3>
                <div class="detail-skills">${escapeHtml(job.ai_skills_required)}</div>
            </div>
        ` : ''}
        
        ${applyButtons}
    `;
}

// Obtenir le nom du site depuis l'URL
function getSiteName(url) {
    try {
        const hostname = new URL(url).hostname;
        if (hostname.includes('linkedin')) return 'LinkedIn';
        if (hostname.includes('indeed')) return 'Indeed';
        return hostname;
    } catch {
        return 'le site original';
    }
}

// Mettre à jour le compteur d'offres
function updateJobCount(count) {
    const jobCount = document.getElementById('job-count');
    jobCount.textContent = `${count} offre${count > 1 ? 's' : ''}`;
}

// Afficher l'état de chargement
function showLoading() {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Chargement des offres...</p>
        </div>
    `;
}

// Afficher l'état vide
function showEmptyState() {
    const detailPanel = document.getElementById('job-detail');
    detailPanel.innerHTML = `
        <div class="empty-state">
            <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
                <circle cx="60" cy="60" r="40" stroke="currentColor" stroke-width="2" opacity="0.2"/>
                <path d="M40 60L55 75L80 45" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>
            </svg>
            <h3>Aucune offre disponible</h3>
            <p>Sélectionnez une autre date pour voir les offres</p>
        </div>
    `;
}

// Afficher une erreur
function showError(message) {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = `
        <div class="empty-state">
            <h3>Erreur</h3>
            <p>${message}</p>
        </div>
    `;
}

// Échapper le HTML pour éviter les injections XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Gestionnaire de changement de date
document.addEventListener('DOMContentLoaded', () => {
    loadDates();
    
    const dateSelector = document.getElementById('date-selector');
    dateSelector.addEventListener('change', (e) => {
        const selectedDate = e.target.value;
        if (selectedDate) {
            loadJobs(selectedDate);
        }
    });
    
    // Gestionnaire pour le filtre des stages
    const internshipCheckbox = document.getElementById('internship-checkbox');
    internshipCheckbox.addEventListener('change', (e) => {
        includeInternships = e.target.checked;
        const selectedDate = dateSelector.value;
        if (selectedDate) {
            loadJobs(selectedDate);
        }
    });
});
