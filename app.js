// ========================================
// AgriDetect - Frontend JS (corrigé & optimisé)
// ========================================
(() => {
  'use strict';

  // -------------------------
  // Configuration API
  // -------------------------
  const inferApiBase = () => {
    try {
      if (window.APP_API_BASE_URL) return String(window.APP_API_BASE_URL);
    } catch (_) {}
    if (
      location.protocol === 'file:' ||
      location.hostname === 'localhost' ||
      location.hostname === '127.0.0.1'
    ) {
      return 'http://localhost:8000';
    }
    return `${location.origin}`;
  };

  const API_BASE_URL = inferApiBase();
  const API_VERSION = '/api/v1';
  const REQUEST_TIMEOUT = 45000; // 45s

  // -------------------------
  // Helpers DOM & Utils
  // -------------------------
  const $ = (id) => document.getElementById(id);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function createEl(tag, className) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    return el;
  }

  function h(tag, attrs = {}, text = undefined) {
    const el = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => {
      if (v === undefined || v === null) return;
      if (k in el) el[k] = v;
      else el.setAttribute(k, v);
    });
    if (text !== undefined) el.textContent = String(text);
    return el;
  }

  function toPercent(value, digits = 1) {
    const v = Number(value);
    if (!isFinite(v)) return '—';
    if (v <= 1) return `${(v * 100).toFixed(digits)}%`;
    return `${v.toFixed(digits)}%`;
  }

  function safeText(text, fallback = '—') {
    return text === null || text === undefined || text === '' ? fallback : String(text);
  }

  function setVisible(el, visible) {
    if (el) el.style.display = visible ? '' : 'none';
  }

  // -------------------------
  // HTTP avec timeout
  // -------------------------
  async function safeFetch(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(
      () => controller.abort(),
      options.timeout || REQUEST_TIMEOUT
    );

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          Accept: 'application/json',
          ...options.headers
        }
      });

      if (!response.ok) {
        let errorMessage = `Erreur HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          const text = await response.text().catch(() => '');
          if (text) errorMessage += `: ${text.substring(0, 120)}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Délai de requête dépassé. Vérifiez votre connexion.');
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  // -------------------------
  // Session & langue
  // -------------------------
  function getOrCreateSessionId() {
    const key = 'agridetect_session_id';
    let id = localStorage.getItem(key);
    if (!id) {
      id = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
      localStorage.setItem(key, id);
    }
    return id;
  }
  const sessionId = getOrCreateSessionId();

  function getSelectedLanguage() {
    const el = $('languageSelect');
    if (!el) return null;
    const val = (el.value || '').toLowerCase();
    if (!val || val === 'auto') return null;
    return ['fr', 'wo', 'pu'].includes(val) ? val : null;
  }

  // -------------------------
  // Upload & analyse
  // -------------------------
  const imageInput = $('imageInput');
  const uploadBox = $('uploadBox');

  if (imageInput) {
    imageInput.addEventListener('change', (e) => {
      const file = e.target.files?.[0];
      if (file) displayImagePreview(file);
    });
  }

  if (uploadBox) {
    uploadBox.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadBox.classList.add('drag-active');
    });
    uploadBox.addEventListener('dragleave', (e) => {
      e.preventDefault();
      uploadBox.classList.remove('drag-active');
    });
    uploadBox.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadBox.classList.remove('drag-active');
      const file = e.dataTransfer.files?.[0];
      if (file && file.type?.startsWith('image/')) {
        if (imageInput) imageInput.files = e.dataTransfer.files;
        displayImagePreview(file);
      } else {
        showError('Veuillez déposer un fichier image valide (JPG, PNG, WebP).');
      }
    });
  }

  function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      setVisible(uploadBox, false);
      setVisible($('imagePreview'), true);
      const img = $('previewImg');
      if (img) {
        img.src = e.target.result;
        img.alt = `Aperçu de ${file.name}`;
      }
      setVisible($('errorSection'), false);
      setVisible($('resultsSection'), false);
    };
    reader.onerror = () => showError('Erreur lors de la lecture du fichier.');
    reader.readAsDataURL(file);
  }

  function resetUpload() {
    if (imageInput) imageInput.value = '';
    setVisible(uploadBox, true);
    setVisible($('imagePreview'), false);
    setVisible($('loadingSection'), false);
    setVisible($('resultsSection'), false);
    setVisible($('errorSection'), false);
  }

  async function analyzeImage() {
    const file = imageInput?.files?.[0];
    const analyzeBtn = document.querySelector('.image-preview .btn-primary');

    if (!file) {
      showError('Veuillez sélectionner une image');
      return;
    }

    const MAX_MB = 10;
    const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!ALLOWED_TYPES.includes(file.type)) {
      showError('Format non supporté. Utilisez JPG, PNG ou WebP.');
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      showError(`L'image dépasse ${MAX_MB} Mo. Veuillez la compresser.`);
      return;
    }

    if (analyzeBtn) {
      analyzeBtn.setAttribute('disabled', 'true');
      analyzeBtn.textContent = "Analyse en cours...";
    }

    setVisible($('imagePreview'), false);
    setVisible($('loadingSection'), true);
    setVisible($('resultsSection'), false);
    setVisible($('errorSection'), false);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const cropSelect = $('cropSelect');
      if (cropSelect && cropSelect.value) {
        formData.append('crop_type', cropSelect.value);
      }

      const lang = getSelectedLanguage();
      if (lang) formData.append('language', lang);

      const data = await safeFetch(`${API_BASE_URL}${API_VERSION}/detect-disease`, {
        method: 'POST',
        body: formData,
        timeout: 45000
      });

      displayResults(data);
    } catch (error) {
      console.error('Erreur analyse:', error);
      handleAnalysisError(error);
    } finally {
      if (analyzeBtn) {
        analyzeBtn.removeAttribute('disabled');
        analyzeBtn.textContent = "Analyser l'image";
      }
      setVisible($('loadingSection'), false);
    }
  }

  function handleAnalysisError(error) {
    const message = String(error.message || error);
    const errorMap = {
      '413': "Fichier trop volumineux. Réduisez la taille de l'image.",
      '415': "Format d'image non supporté.",
      '422': "Image invalide ou corrompue.",
      '500': "Erreur serveur. Réessayez dans quelques instants.",
      '503': "Service temporairement indisponible."
    };
    const statusCode = Object.keys(errorMap).find((code) => message.includes(code));
    const userMessage = statusCode ? errorMap[statusCode] : message;
    showError(userMessage);
  }

  function displayResults(data) {
    if (!data || typeof data !== 'object') {
      showError('Données de réponse invalides.');
      return;
    }

    // ton backend renvoie: disease_name, confidence, severity, affected_crop
    const diseaseName = safeText(data.disease_name, 'Maladie non identifiée');
    const confidence = Number(data.confidence ?? 0);
    const severity = safeText(data.severity, 'Inconnue');
    const affectedCrop = safeText(data.affected_crop, 'Non spécifié');

    const dn = $('diseaseName');
    if (dn) dn.textContent = diseaseName;
    const cf = $('confidence');
    if (cf) cf.textContent = toPercent(confidence, 1);
    const sv = $('severity');
    if (sv) sv.textContent = severity;
    const ac = $('affectedCrop');
    if (ac) ac.textContent = affectedCrop;

    if (cf) {
      cf.style.color =
        confidence >= 0.8
          ? 'var(--success-color)'
          : confidence >= 0.6
          ? 'var(--warning-color)'
          : 'var(--danger-color)';
    }

    const treatmentsContainer = $('treatments');
    if (treatmentsContainer) {
      treatmentsContainer.innerHTML = '';
      const treatments = Array.isArray(data.treatments) ? data.treatments : [];
      const isHealthy = /healthy|sain|aucun/i.test(diseaseName.toLowerCase());

      if (isHealthy) {
        treatmentsContainer.appendChild(
          h(
            'p',
            { className: 'healthy-message' },
            '✅ Aucun traitement nécessaire. Continuez les bonnes pratiques culturales.'
          )
        );
      } else if (treatments.length > 0) {
        treatments.forEach((treatment, index) => {
          const item = createEl('div', 'treatment-item');

          if (treatment && typeof treatment === 'object') {
            const title = h('h4', {}, safeText(treatment.name, `Traitement ${index + 1}`));
            const description = h(
              'p',
              {},
              safeText(treatment.description, 'Description non disponible.')
            );
            item.appendChild(title);
            item.appendChild(description);

            if (treatment.application) {
              item.appendChild(h('p', { className: 'treatment-app' }, treatment.application));
            }

            if (treatment.organic) {
              item.appendChild(h('span', { className: 'organic-badge' }, '🌱 Biologique'));
            }
          } else {
            item.appendChild(h('p', {}, safeText(treatment, 'Traitement non spécifié')));
          }

          treatmentsContainer.appendChild(item);
        });
      } else {
        treatmentsContainer.appendChild(
          h(
            'p',
            { className: 'no-treatment' },
            'ℹ️ Aucun traitement spécifique disponible pour le moment.'
          )
        );
      }
    }

    const preventionList = $('preventionTips');
    if (preventionList) {
      preventionList.innerHTML = '';
      const tips = Array.isArray(data.prevention_tips) ? data.prevention_tips : [];
      if (tips.length > 0) {
        tips.forEach((tip, i) => {
          const li = h('li', {}, safeText(tip, `Conseil ${i + 1}`));
          preventionList.appendChild(li);
        });
      } else {
        preventionList.appendChild(h('li', {}, 'ℹ️ Aucun conseil de prévention disponible.'));
      }
    }

    setVisible($('resultsSection'), true);

    setTimeout(() => {
      $('resultsSection')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  function showError(message) {
    const msg = $('errorMessage');
    if (msg) {
      msg.textContent = message;
      msg.setAttribute('role', 'alert');
    }
    setVisible($('errorSection'), true);
    setVisible($('loadingSection'), false);
    setVisible($('imagePreview'), false);

    setTimeout(() => $('errorSection')?.focus(), 100);
  }

  // -------------------------
  // Chatbot
  // -------------------------
  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  async function sendMessage() {
    const input = $('chatInput');
    if (!input) return;
    const message = input.value.trim();
    if (!message) {
      showChatError('Veuillez saisir un message.');
      return;
    }
    if (message.length > 1000) {
      showChatError('Message trop long (max 1000 caractères).');
      return;
    }

    displayMessage(message, 'user');
    input.value = '';

    input.setAttribute('disabled', 'true');
    const sendBtn = document.querySelector('.chat-input button');
    if (sendBtn) sendBtn.setAttribute('disabled', 'true');

    try {
      const payload = {
        message,
        context: {
          session_id: sessionId,
          timestamp: new Date().toISOString()
        }
      };

      const language = getSelectedLanguage();
      if (language) payload.language = language;

      const data = await safeFetch(`${API_BASE_URL}${API_VERSION}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        timeout: 15000
      });

      const botResponse = safeText(
        data?.response || data?.text || data?.message,
        "Désolé, je n'ai pas pu traiter votre demande."
      );
      const suggestions = Array.isArray(data?.suggestions) ? data.suggestions : [];

      displayMessage(botResponse, 'bot');
      if (suggestions.length > 0) {
        updateSuggestions(suggestions);
      }
    } catch (error) {
      console.error('Erreur chat:', error);
      displayMessage('❌ Désolé, une erreur s’est produite. Veuillez réessayer.', 'bot');
    } finally {
      input.removeAttribute('disabled');
      const sendBtn2 = document.querySelector('.chat-input button');
      if (sendBtn2) sendBtn2.removeAttribute('disabled');
      input.focus();
    }
  }

  function showChatError(message) {
    const container = $('chatMessages');
    if (!container) return;
    const errorMsg = createEl('div', 'message system-message');
    errorMsg.textContent = message;
    container.appendChild(errorMsg);
    container.scrollTop = container.scrollHeight;
  }

  function sendSuggestion(text) {
    const input = $('chatInput');
    if (!input) return;
    input.value = text;
    sendMessage();
  }

  function displayMessage(text, type) {
    const container = $('chatMessages');
    if (!container) return;

    const messageEl = createEl('div', `message ${type}-message`);
    const avatar = type === 'user' ? '👤' : '🤖';
    const time = new Date().toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });

    const avatarEl = h(
      'div',
      {
        className: 'message-avatar',
        'aria-hidden': 'true'
      },
      avatar
    );

    const contentEl = createEl('div', 'message-content');
    const textEl = h('p', {}, text);
    const timeEl = h('span', { className: 'message-time' }, time);

    contentEl.appendChild(textEl);
    contentEl.appendChild(timeEl);
    messageEl.appendChild(avatarEl);
    messageEl.appendChild(contentEl);

    container.appendChild(messageEl);
    container.scrollTop = container.scrollHeight;
  }

  function updateSuggestions(suggestions) {
    const list = document.querySelector('.suggestions-list');
    if (!list) return;
    list.innerHTML = '';

    suggestions.slice(0, 4).forEach((suggestion) => {
      const button = createEl('button', 'suggestion-btn');
      button.type = 'button';
      button.textContent = suggestion;
      button.onclick = () => sendSuggestion(suggestion);
      list.appendChild(button);
    });
  }

  // -------------------------
  // Dashboard
  // -------------------------
  async function loadDashboardStats() {
    try {
      const data = await safeFetch(`${API_BASE_URL}${API_VERSION}/statistics/dashboard`, {
        timeout: 10000
      });

      if ($('totalDetections')) $('totalDetections').textContent = safeText(data.total_detections, '0');
      if ($('activeUsers')) $('activeUsers').textContent = safeText(data.active_users, '0');
      if ($('diseaseTypes')) $('diseaseTypes').textContent = safeText(data.diseases_detected, '0');

      const successRate = Number(data.success_rate ?? 0);
      if ($('successRate')) {
        $('successRate').textContent =
          successRate > 1 ? `${Math.min(100, successRate).toFixed(1)}%` : toPercent(successRate, 1);
      }

      displayTopDiseasesFromArray(data.top_diseases || []);
    } catch (error) {
      console.error('Erreur dashboard:', error);
      setDashboardErrorState();
    }
  }

  function setDashboardErrorState() {
    ['totalDetections', 'activeUsers', 'diseaseTypes', 'successRate'].forEach((id) => {
      const el = $(id);
      if (el) el.textContent = '—';
    });
    const container = $('topDiseases');
    if (container) {
      container.innerHTML =
        '<p style="text-align:center;color:var(--text-light);">Données non disponibles</p>';
    }
  }

  function displayTopDiseasesFromArray(arr) {
    const container = $('topDiseases');
    if (!container) return;
    container.innerHTML = '';

    if (!Array.isArray(arr) || arr.length === 0) {
      container.innerHTML =
        '<p style="text-align:center;color:var(--text-light);">Aucune donnée disponible</p>';
      return;
    }

    const sorted = [...arr]
      .filter((item) => item && item.name)
      .sort((a, b) => Number(b.count || 0) - Number(a.count || 0))
      .slice(0, 5);

    const maxCount = Math.max(...sorted.map((item) => Number(item.count || 0)), 1);

    sorted.forEach(({ name, count }) => {
      const barEl = createEl('div', 'chart-bar');
      const countValue = Number(count || 0);
      const percentage = Math.max(5, (countValue / maxCount) * 100);

      const labelEl = createEl('div', 'chart-label');
      labelEl.appendChild(h('span', { className: 'disease-name' }, safeText(name, 'Maladie')));
      labelEl.appendChild(h('span', { className: 'disease-count' }, `${countValue} détections`));

      const progressEl = createEl('div', 'progress-bar');
      progressEl.setAttribute('role', 'progressbar');
      progressEl.setAttribute('aria-valuenow', String(countValue));
      progressEl.setAttribute('aria-valuemin', '0');
      progressEl.setAttribute('aria-valuemax', String(maxCount));

      const fillEl = createEl('div', 'progress-fill');
      fillEl.style.width = `${percentage}%`;
      progressEl.appendChild(fillEl);

      barEl.appendChild(labelEl);
      barEl.appendChild(progressEl);
      container.appendChild(barEl);
    });
  }

  // -------------------------
  // Maladies communes
  // -------------------------
  async function loadCommonDiseases() {
    try {
      const cropSelect = $('cropFilter');
      const query =
        cropSelect && cropSelect.value ? `?crop_type=${encodeURIComponent(cropSelect.value)}` : '';
      const data = await safeFetch(`${API_BASE_URL}${API_VERSION}/diseases/common${query}`, {
        timeout: 10000
      });
      displayCommonDiseases(data.diseases || []);
    } catch (error) {
      console.error('Erreur maladies communes:', error);
      const container = $('diseasesList');
      if (container) {
        container.innerHTML =
          '<p style="text-align:center;color:var(--text-light);">Erreur de chargement</p>';
      }
    }
  }

  function displayCommonDiseases(diseases) {
    const container = $('diseasesList');
    if (!container) return;
    container.innerHTML = '';

    if (!Array.isArray(diseases) || diseases.length === 0) {
      container.innerHTML =
        '<p style="text-align:center;color:var(--text-light);">Aucune maladie disponible</p>';
      return;
    }

    diseases.forEach((disease) => {
      if (!disease || !disease.name) return;

      const itemEl = createEl('div', 'disease-item');

      const leftEl = createEl('div', 'disease-info');
      const nameEl = h('div', { className: 'disease-name' }, safeText(disease.name, 'Maladie'));

      const crops = Array.isArray(disease.crops_affected)
        ? disease.crops_affected.join(', ')
        : 'Diverses cultures';
      const season = safeText(disease.season, 'Toute saison');
      const metaEl = h('small', { className: 'disease-meta' }, `${crops} — ${season}`);

      leftEl.appendChild(nameEl);
      leftEl.appendChild(metaEl);

      const rightEl = createEl('div', 'disease-severity');
      rightEl.textContent = safeText(disease.severity, '—');

      itemEl.appendChild(leftEl);
      itemEl.appendChild(rightEl);
      container.appendChild(itemEl);
    });
  }

  // -------------------------
  // Health ping & init
  // -------------------------
  async function healthPing() {
    const badge = $('apiStatus');
    try {
      const data = await safeFetch(`${API_BASE_URL}/health`, { timeout: 5000 });
      console.log('%c🌾 AgriDetect', 'color:#2ecc71;font-size:20px;font-weight:bold;');
      console.log('%c✅ API Connectée', 'color:#27ae60;font-weight:bold;', data);
      if (badge) {
        badge.textContent = 'API: Connectée';
        badge.className = 'api-status connected';
      }
    } catch (error) {
      console.log('%c🌾 AgriDetect', 'color:#2ecc71;font-size:20px;font-weight:bold;');
      console.warn('%c⚠️ API Non joignable', 'color:#e67e22;font-weight:bold;');
      if (badge) {
        badge.textContent = 'API: Déconnectée';
        badge.className = 'api-status disconnected';
      }
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    if ($('totalDetections') || $('topDiseases')) {
      loadDashboardStats();
    }
    if ($('diseasesList')) {
      loadCommonDiseases();
    }
    healthPing();

    console.log("%cProjet de Fin d'Étude - 2025", 'color:#95a5a6;font-size:14px;');
    console.log('%c🔗 API Base URL:', 'color:#3498db;font-weight:bold;', API_BASE_URL);
    console.log('%c🆔 Session:', 'color:#9b59b6;font-weight:bold;', sessionId);
  });

  // Exposition globale
  window.analyzeImage = analyzeImage;
  window.resetUpload = resetUpload;
  window.handleKeyPress = handleKeyPress;
  window.sendMessage = sendMessage;
  window.sendSuggestion = sendSuggestion;
  window.loadCommonDiseases = loadCommonDiseases;
  window.loadDashboardStats = loadDashboardStats;
})();



