"""
Módulo de Consola de Administración (/admin) para Asesor Virtual de Auto - Caja de Ahorros.
Proporciona:
  - Autenticación por passcode (cda2026 o ADMIN_PASSCODE en .env)
  - Configuración dinámica de proveedores de IA (Gemini, OpenAI, Claude, Local) y API Keys
  - Visualizador de logs en tiempo real (Servidor, AI Requests, Auditoría) con badges de éxito/error
  - Exportación de Leads a CSV (cruzando session_id y pase_digital) y Chats a JSON
"""

import os
import io
import csv
import json
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from database.db_manager import (
    obtener_config,
    guardar_config,
    obtener_logs,
    obtener_todos_los_clientes,
    obtener_todas_las_conversaciones,
    registrar_log_auditoria,
    registrar_log_servidor
)

def get_admin_passcode() -> str:
    """Retorna el passcode de administrador configurado o el predeterminado 'cda2026'."""
    return (os.getenv("ADMIN_PASSCODE") or "cda2026").strip()


def check_auth(request: Request) -> bool:
    """Verifica si la petición cuenta con el passcode válido (vía Header, Cookie o Query param)."""
    valid_pass = get_admin_passcode()
    
    # 1. Header
    auth_header = request.headers.get("X-Admin-Passcode") or request.headers.get("x-admin-passcode")
    if auth_header and auth_header.strip() == valid_pass:
        return True
        
    # 2. Query param (útil para enlaces de descarga directa de archivos)
    query_pass = request.query_params.get("passcode")
    if query_pass and query_pass.strip() == valid_pass:
        return True
        
    # 3. Cookie
    cookie_pass = request.cookies.get("cda_admin_auth")
    if cookie_pass and cookie_pass.strip() == valid_pass:
        return True
        
    return False


HTML_ADMIN_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consola de Administración | Caja de Ahorros</title>
    <link rel="icon" type="image/x-icon" href="/favicon">
    <style>
        :root {
            --primary: #002D62;
            --primary-dark: #001A38;
            --primary-light: #0A4B94;
            --accent: #E5A823;
            --accent-hover: #D49B17;
            --bg-color: #F4F7FA;
            --card-bg: #FFFFFF;
            --text-main: #1E293B;
            --text-muted: #64748B;
            --border-color: #E2E8F0;
            --success-bg: #DCFCE7;
            --success-text: #15803D;
            --error-bg: #FEE2E2;
            --error-text: #B91C1C;
            --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--font-family);
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* HEADER */
        .admin-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: #FFFFFF;
            padding: 16px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0, 45, 98, 0.15);
        }
        .header-brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .brand-icon {
            font-size: 28px;
            background: rgba(255, 255, 255, 0.12);
            padding: 6px 12px;
            border-radius: 8px;
        }
        .header-title h1 {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.3px;
        }
        .header-title p {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.8);
        }
        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .btn-link {
            color: #FFFFFF;
            text-decoration: none;
            font-size: 13px;
            padding: 8px 14px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.15);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-link:hover {
            background: rgba(255, 255, 255, 0.25);
        }

        /* CONTAINER */
        .admin-container {
            max-width: 1320px;
            width: 100%;
            margin: 24px auto;
            padding: 0 20px;
            flex: 1;
        }

        /* LOGIN OVERLAY */
        #login-view {
            max-width: 440px;
            margin: 60px auto;
            background: var(--card-bg);
            padding: 36px 32px;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
            text-align: center;
        }
        .login-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        .login-title {
            font-size: 22px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 8px;
        }
        .login-desc {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 24px;
        }
        .form-group {
            text-align: left;
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 6px;
        }
        .form-control {
            width: 100%;
            padding: 11px 14px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 14px;
            color: var(--text-main);
            background: #FFFFFF;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .form-control:focus {
            outline: none;
            border-color: var(--primary-light);
            box-shadow: 0 0 0 3px rgba(10, 75, 148, 0.15);
        }
        .btn-primary {
            width: 100%;
            padding: 12px;
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-primary:hover {
            background: var(--primary-light);
        }
        .btn-accent {
            padding: 10px 18px;
            background: var(--accent);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }
        .btn-accent:hover {
            background: var(--accent-hover);
        }
        .btn-outline {
            padding: 9px 16px;
            background: #FFFFFF;
            color: var(--primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-outline:hover {
            background: #F1F5F9;
            border-color: #CBD5E1;
        }

        /* DASHBOARD CONTENT */
        #dashboard-view {
            display: none;
        }

        /* NAVIGATION TABS */
        .tabs-nav {
            display: flex;
            gap: 8px;
            background: #FFFFFF;
            padding: 8px 12px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            margin-bottom: 24px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }
        .tab-btn {
            padding: 10px 18px;
            border: none;
            background: transparent;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .tab-btn:hover {
            color: var(--primary);
            background: #F8FAFC;
        }
        .tab-btn.active {
            color: #FFFFFF;
            background: var(--primary);
        }

        /* CARDS & PANELS */
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
            padding: 24px;
            margin-bottom: 24px;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--border-color);
        }
        .card-title {
            font-size: 17px;
            font-weight: 700;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* BADGES */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }
        .badge-success {
            background: var(--success-bg);
            color: var(--success-text);
            border: 1px solid #BBF7D0;
        }
        .badge-error {
            background: var(--error-bg);
            color: var(--error-text);
            border: 1px solid #FECACA;
        }
        .badge-info {
            background: #E0F2FE;
            color: #0369A1;
            border: 1px solid #BAE6FD;
        }

        /* TABLES */
        .table-responsive {
            width: 100%;
            overflow-x: auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }
        th {
            background: #F8FAFC;
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }
        td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
            vertical-align: middle;
        }
        tr:last-child td {
            border-bottom: none;
        }
        tr:hover td {
            background-color: #F8FAFC;
        }
        .code-cell {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
            background: #F1F5F9;
            padding: 2px 6px;
            border-radius: 4px;
        }

        /* ALERT TOAST */
        #alert-box {
            display: none;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        #alert-box.success {
            display: block;
            background: var(--success-bg);
            color: var(--success-text);
            border: 1px solid #86EFAC;
        }
        #alert-box.error {
            display: block;
            background: var(--error-bg);
            color: var(--error-text);
            border: 1px solid #FCA5A5;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .grid-2 { grid-template-columns: 1fr; }
            .admin-header { padding: 14px 16px; flex-direction: column; gap: 12px; align-items: flex-start; }
            .header-actions { width: 100%; justify-content: space-between; }
        }
    </style>
</head>
<body>

    <!-- HEADER SUPERIOR -->
    <header class="admin-header">
        <div class="header-brand">
            <span class="brand-icon">🚗</span>
            <div class="header-title">
                <h1>Caja de Ahorros | Feria de Préstamos de Auto</h1>
                <p>Consola de Gestión, Trazabilidad de Logs & Exportación</p>
            </div>
        </div>
        <div class="header-actions">
            <a href="/" class="btn-link" target="_blank">💬 Ver Chat Asesor</a>
            <button id="btn-logout" class="btn-link" style="display:none; cursor:pointer;" onclick="logout()">🔒 Salir</button>
        </div>
    </header>

    <div class="admin-container">
        <div id="alert-box"></div>

        <!-- VISTA DE LOGIN -->
        <div id="login-view">
            <div class="login-icon">🔐</div>
            <h2 class="login-title">Acceso de Administración</h2>
            <p class="login-desc">Ingrese el passcode de seguridad institucional para gestionar configuraciones y auditar eventos.</p>
            
            <form id="login-form" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label class="form-label">Passcode de Seguridad</label>
                    <input type="password" id="passcode-input" class="form-control" placeholder="Ingrese passcode (ej. cda2026)" required autofocus />
                </div>
                <button type="submit" class="btn-primary">Ingresar al Panel</button>
            </form>
        </div>

        <!-- VISTA DE DASHBOARD -->
        <div id="dashboard-view">
            <!-- NAVEGACIÓN DE PESTAÑAS -->
            <div class="tabs-nav">
                <button class="tab-btn active" onclick="switchTab('ai-config')">⚙️ Configuración IA</button>
                <button class="tab-btn" onclick="switchTab('logs')">📊 Trazabilidad & Logs</button>
                <button class="tab-btn" onclick="switchTab('leads')">👥 Leads & Exportación</button>
            </div>

            <!-- TAB 1: CONFIGURACIÓN IA -->
            <div id="tab-ai-config" class="tab-content">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">🤖 Configuración Dinámica de Inteligencia Artificial</h2>
                        <span class="badge badge-info">Persistencia en SQLite</span>
                    </div>
                    <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">
                        Seleccione el proveedor activo para el Asesor Virtual. Las credenciales se resguardan de forma segura en la base de datos sin necesidad de reiniciar el servidor. Si el proveedor seleccionado no cuenta con clave o falla, el sistema conmuta automáticamente al motor institucional de reglas locales.
                    </p>

                    <form id="ai-config-form" onsubmit="saveAiConfig(event)">
                        <div class="grid-2">
                            <div class="form-group">
                                <label class="form-label">Proveedor de Inteligencia Artificial</label>
                                <select id="ai-provider-select" class="form-control" onchange="handleProviderChange()">
                                    <option value="gemini">Google Gemini</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="claude">Anthropic Claude</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Modelo del Proveedor</label>
                                <select id="ai-model-select" class="form-control"></select>
                            </div>
                        </div>

                        <div class="form-group" id="api-key-group">
                            <label class="form-label">Clave de API (API Key)</label>
                            <div style="display: flex; gap: 8px;">
                                <input type="password" id="ai-key-input" class="form-control" placeholder="Ingrese o actualice su API Key..." />
                                <button type="button" class="btn-outline" onclick="toggleKeyVisibility()">👁️</button>
                            </div>
                            <small style="font-size: 12px; color: var(--text-muted); margin-top: 4px; display: block;">
                                Deje en blanco si desea mantener la clave actual configurada.
                            </small>
                        </div>

                        <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
                            <button type="submit" class="btn-accent">💾 Guardar Configuración</button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- TAB 2: LOGS -->
            <div id="tab-logs" class="tab-content" style="display:none;">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">📋 Registro y Trazabilidad en Tiempo Real</h2>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <select id="log-type-select" class="form-control" style="width: auto; padding: 7px 12px;" onchange="loadLogs()">
                                <option value="servidor">Servidor HTTP (logs_servidor)</option>
                                <option value="ai">Consultas de IA (logs_ai_requests)</option>
                                <option value="auditoria">Auditoría de Negocio (logs_auditoria)</option>
                            </select>
                            <button class="btn-outline" onclick="loadLogs()">🔄 Refrescar</button>
                        </div>
                    </div>

                    <div class="table-responsive">
                        <table id="logs-table">
                            <thead>
                                <tr id="logs-header-row"></tr>
                            </thead>
                            <tbody id="logs-body-row"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 3: LEADS & EXPORT -->
            <div id="tab-leads" class="tab-content" style="display:none;">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">👥 Prospectos de Feria y Pases Digitales Emitidos</h2>
                        <div style="display: flex; gap: 10px;">
                            <button class="btn-accent" onclick="exportData('leads')">📥 Descargar Leads (CSV)</button>
                            <button class="btn-outline" onclick="exportData('chats')">📥 Descargar Historial Chats (JSON)</button>
                        </div>
                    </div>

                    <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">
                        Los datos personales capturados en el formulario inicial se correlacionan directamente con el <strong>Pase Digital Prioritario (CDA-FERIA-XXXX)</strong> y el identificador único de sesión. La exportación CSV incluye codificación UTF-8 compatible de forma nativa con Microsoft Excel.
                    </p>

                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Pase Digital</th>
                                    <th>Nombre del Titular</th>
                                    <th>Cédula</th>
                                    <th>Celular</th>
                                    <th>Correo</th>
                                    <th>Perfil Laboral</th>
                                    <th>Uso Auto</th>
                                    <th>Fecha Registro</th>
                                </tr>
                            </thead>
                            <tbody id="leads-body-row"></tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        let currentPasscode = sessionStorage.getItem('cda_admin_pass') || '';

        function showAlert(msg, isSuccess = true) {
            const box = document.getElementById('alert-box');
            box.className = isSuccess ? 'success' : 'error';
            box.innerText = msg;
            box.style.display = 'block';
            setTimeout(() => { box.style.display = 'none'; }, 4000);
        }

        function toggleKeyVisibility() {
            const input = document.getElementById('ai-key-input');
            input.type = input.type === 'password' ? 'text' : 'password';
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

            if (tabId === 'ai-config') {
                event.target.classList.add('active');
                document.getElementById('tab-ai-config').style.display = 'block';
                loadAiConfig();
            } else if (tabId === 'logs') {
                event.target.classList.add('active');
                document.getElementById('tab-logs').style.display = 'block';
                loadLogs();
            } else if (tabId === 'leads') {
                event.target.classList.add('active');
                document.getElementById('tab-leads').style.display = 'block';
                loadLeads();
            }
        }

        async function handleLogin(e) {
            e.preventDefault();
            const pass = document.getElementById('passcode-input').value.trim();
            try {
                const resp = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ passcode: pass })
                });
                const data = await resp.json();
                if (resp.ok && data.ok) {
                    currentPasscode = pass;
                    sessionStorage.setItem('cda_admin_pass', pass);
                    document.cookie = `cda_admin_auth=${pass}; path=/; SameSite=Lax`;
                    document.getElementById('login-view').style.display = 'none';
                    document.getElementById('dashboard-view').style.display = 'block';
                    document.getElementById('btn-logout').style.display = 'inline-flex';
                    showAlert('Sesión iniciada correctamente', true);
                    loadAiConfig();
                } else {
                    showAlert(data.error || 'Passcode incorrecto', false);
                }
            } catch (err) {
                showAlert('Error al conectar con el servidor', false);
            }
        }

        function logout() {
            sessionStorage.removeItem('cda_admin_pass');
            document.cookie = "cda_admin_auth=; path=/; max-age=0";
            currentPasscode = '';
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('login-view').style.display = 'block';
            document.getElementById('btn-logout').style.display = 'none';
        }

        const PROVIDER_MODELS = {
            gemini: [
                { id: "gemini-2.0-flash", label: "gemini-2.0-flash (Predeterminado)" },
                { id: "gemini-1.5-flash", label: "gemini-1.5-flash" },
                { id: "gemini-1.5-pro", label: "gemini-1.5-pro" }
            ],
            openai: [
                { id: "gpt-4o-mini", label: "gpt-4o-mini (Predeterminado)" },
                { id: "gpt-4o", label: "gpt-4o" },
                { id: "gpt-3.5-turbo", label: "gpt-3.5-turbo" }
            ],
            claude: [
                { id: "claude-3-5-haiku-20241022", label: "claude-3-5-haiku (Predeterminado)" },
                { id: "claude-3-5-sonnet-20241022", label: "claude-3-5-sonnet" },
                { id: "claude-3-haiku-20240307", label: "claude-3-haiku" }
            ]
        };

        async function loadAiConfig() {
            try {
                const resp = await fetch('/api/admin/config', {
                    headers: { 'X-Admin-Passcode': currentPasscode }
                });
                if (resp.status === 401) { logout(); return; }
                const data = await resp.json();
                document.getElementById('ai-provider-select').value = data.provider || 'gemini';
                handleProviderChange(data.model);
                document.getElementById('ai-key-input').placeholder = data.api_key_masked ? `Actual: ${data.api_key_masked}` : 'Ingrese API Key...';
            } catch (err) {
                console.error(err);
            }
        }

        function handleProviderChange(selectedModel = null) {
            const provider = document.getElementById('ai-provider-select').value;
            const modelSelect = document.getElementById('ai-model-select');
            const models = PROVIDER_MODELS[provider] || [];
            
            modelSelect.innerHTML = '';
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = m.label;
                modelSelect.appendChild(opt);
            });

            if (selectedModel && models.some(m => m.id === selectedModel)) {
                modelSelect.value = selectedModel;
            } else if (models.length > 0) {
                modelSelect.value = models[0].id;
            }
        }

        async function saveAiConfig(e) {
            e.preventDefault();
            const provider = document.getElementById('ai-provider-select').value;
            const model = document.getElementById('ai-model-select').value;
            const key = document.getElementById('ai-key-input').value.trim();

            try {
                const resp = await fetch('/api/admin/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Admin-Passcode': currentPasscode
                    },
                    body: JSON.stringify({ provider, model, api_key: key })
                });
                const res = await resp.json();
                if (resp.ok && res.ok) {
                    showAlert('Configuración guardada exitosamente en SQLite', true);
                    document.getElementById('ai-key-input').value = '';
                    loadAiConfig();
                } else {
                    showAlert(res.error || 'Error al guardar configuración', false);
                }
            } catch (err) {
                showAlert('Error al contactar con el servidor', false);
            }
        }

        async function loadLogs() {
            const logType = document.getElementById('log-type-select').value;
            try {
                const resp = await fetch(`/api/admin/logs?type=${logType}&limit=50`, {
                    headers: { 'X-Admin-Passcode': currentPasscode }
                });
                if (resp.status === 401) { logout(); return; }
                const data = await resp.json();
                const thead = document.getElementById('logs-header-row');
                const tbody = document.getElementById('logs-body-row');
                thead.innerHTML = '';
                tbody.innerHTML = '';

                if (logType === 'servidor') {
                    thead.innerHTML = '<th>ID</th><th>Fecha</th><th>Nivel</th><th>Método</th><th>Endpoint</th><th>Código</th><th>Mensaje</th><th>Detalle Error</th>';
                    (data.logs || []).forEach(l => {
                        const isOk = l.codigo_estado < 400 && l.nivel !== 'ERROR';
                        const badgeClass = isOk ? 'badge-success' : 'badge-error';
                        tbody.innerHTML += `<tr>
                            <td>${l.id}</td>
                            <td>${l.timestamp}</td>
                            <td><span class="badge ${badgeClass}">${l.nivel}</span></td>
                            <td><strong>${l.metodo || 'GET'}</strong></td>
                            <td class="code-cell">${l.endpoint || '/'}</td>
                            <td><span class="badge ${badgeClass}">${l.codigo_estado || 200}</span></td>
                            <td>${l.mensaje}</td>
                            <td style="color:var(--error-text); font-size:12px;">${l.detalle_error || '-'}</td>
                        </tr>`;
                    });
                } else if (logType === 'ai') {
                    thead.innerHTML = '<th>ID</th><th>Fecha</th><th>Proveedor</th><th>Modelo</th><th>Tiempo (ms)</th><th>Estado</th><th>Detalle Error</th>';
                    (data.logs || []).forEach(l => {
                        const isOk = l.estado === 'SUCCESS';
                        const badgeClass = isOk ? 'badge-success' : 'badge-error';
                        tbody.innerHTML += `<tr>
                            <td>${l.id}</td>
                            <td>${l.timestamp}</td>
                            <td><strong>${l.proveedor.toUpperCase()}</strong></td>
                            <td class="code-cell">${l.modelo || '-'}</td>
                            <td>${l.tiempo_ms ? l.tiempo_ms + ' ms' : '-'}</td>
                            <td><span class="badge ${badgeClass}">${l.estado}</span></td>
                            <td style="color:var(--error-text); font-size:12px;">${l.error_detail || '-'}</td>
                        </tr>`;
                    });
                } else if (logType === 'auditoria') {
                    thead.innerHTML = '<th>ID</th><th>Fecha</th><th>Evento</th><th>Usuario</th><th>Detalles</th>';
                    (data.logs || []).forEach(l => {
                        tbody.innerHTML += `<tr>
                            <td>${l.id}</td>
                            <td>${l.timestamp}</td>
                            <td><span class="badge badge-info">${l.tipo_evento}</span></td>
                            <td><strong>${l.usuario_origen}</strong></td>
                            <td>${l.detalles}</td>
                        </tr>`;
                    });
                }

                if (!data.logs || data.logs.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:24px; color:var(--text-muted);">No hay registros en esta bitácora</td></tr>`;
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function loadLeads() {
            try {
                const resp = await fetch('/api/admin/leads', {
                    headers: { 'X-Admin-Passcode': currentPasscode }
                });
                if (resp.status === 401) { logout(); return; }
                const data = await resp.json();
                const tbody = document.getElementById('leads-body-row');
                tbody.innerHTML = '';
                (data.leads || []).forEach(l => {
                    const pase = l.pase_digital || 'N/A';
                    tbody.innerHTML += `<tr>
                        <td><span class="code-cell" style="font-weight:700; color:var(--primary);">${pase}</span></td>
                        <td><strong>${l.nombre}</strong></td>
                        <td>${l.cedula}</td>
                        <td>${l.celular}</td>
                        <td>${l.correo}</td>
                        <td>${l.sector_laboral || '-'}</td>
                        <td>${l.uso_vehiculo || '-'}</td>
                        <td>${l.fecha_registro}</td>
                    </tr>`;
                });
                if (!data.leads || data.leads.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:24px; color:var(--text-muted);">Aún no hay prospectos registrados</td></tr>`;
                }
            } catch (err) {
                console.error(err);
            }
        }

        function exportData(type) {
            if (!currentPasscode) { logout(); return; }
            if (type === 'leads') {
                window.location.href = `/api/admin/export/leads?passcode=${encodeURIComponent(currentPasscode)}`;
            } else if (type === 'chats') {
                window.location.href = `/api/admin/export/chats?passcode=${encodeURIComponent(currentPasscode)}`;
            }
        }

        // Auto-login si ya existe token en sessionStorage
        window.addEventListener('DOMContentLoaded', () => {
            if (currentPasscode) {
                document.getElementById('login-view').style.display = 'none';
                document.getElementById('dashboard-view').style.display = 'block';
                document.getElementById('btn-logout').style.display = 'inline-flex';
                loadAiConfig();
            }
        });
    </script>
</body>
</html>
"""


admin_router = APIRouter()


@admin_router.get("/admin", response_class=HTMLResponse)
async def get_admin_dashboard(request: Request):
    registrar_log_servidor(
        nivel="INFO",
        endpoint="/admin",
        metodo="GET",
        codigo_estado=200,
        mensaje="Acceso a la consola de administración",
        ip_origen=request.client.host if request.client else "127.0.0.1"
    )
    return HTMLResponse(content=HTML_ADMIN_TEMPLATE)


@admin_router.post("/api/admin/login")
async def admin_login(request: Request):
    data = await request.json()
    passcode = (data.get("passcode") or "").strip()
    client_ip = request.client.host if request.client else "127.0.0.1"

    if passcode == get_admin_passcode():
        registrar_log_auditoria(
            tipo_evento="LOGIN_ADMIN_EXITOSO",
            detalles=f"Autenticación exitosa desde {client_ip}",
            usuario_origen="admin"
        )
        return {"ok": True, "message": "Acceso concedido"}
    
    registrar_log_auditoria(
        tipo_evento="LOGIN_ADMIN_FALLIDO",
        detalles=f"Intento con clave incorrecta desde {client_ip}",
        usuario_origen="anonimo"
    )
    return JSONResponse(status_code=401, content={"ok": False, "error": "Passcode incorrecto"})


@admin_router.get("/api/admin/config")
async def get_config_endpoint(request: Request):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"ok": False, "error": "No autorizado"})
    
    provider = obtener_config("ai_provider", "gemini")
    model = obtener_config("ai_model", "gemini-2.0-flash")
    raw_key = obtener_config("ai_api_key", os.getenv("GEMINI_API_KEY", ""))
    
    masked_key = ""
    if raw_key:
        if len(raw_key) > 8:
            masked_key = f"{raw_key[:4]}...{raw_key[-4:]}"
        else:
            masked_key = "********"

    return {
        "ok": True,
        "provider": provider,
        "model": model,
        "api_key_masked": masked_key
    }


@admin_router.post("/api/admin/config")
async def update_config_endpoint(request: Request):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"ok": False, "error": "No autorizado"})
    
    data = await request.json()
    provider = (data.get("provider") or "").strip().lower()
    model = (data.get("model") or "").strip()
    api_key = (data.get("api_key") or "").strip()

    if provider:
        guardar_config("ai_provider", provider)
    if model:
        guardar_config("ai_model", model)
    if api_key:
        guardar_config("ai_api_key", api_key)

    client_ip = request.client.host if request.client else "127.0.0.1"
    registrar_log_auditoria(
        tipo_evento="CAMBIO_CONFIG_AI",
        detalles=f"Proveedor: {provider}, Modelo: {model}, ClaveActualizada: {bool(api_key)} desde {client_ip}",
        usuario_origen="admin"
    )

    return {"ok": True, "message": "Configuración guardada exitosamente"}


@admin_router.get("/api/admin/logs")
async def get_logs_endpoint(request: Request, type: str = "servidor", limit: int = 50):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"ok": False, "error": "No autorizado"})
    
    logs = obtener_logs(tipo_log=type, limite=limit)
    return {"ok": True, "logs": logs}


@admin_router.get("/api/admin/leads")
async def get_leads_endpoint(request: Request):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"ok": False, "error": "No autorizado"})
    
    leads = obtener_todos_los_clientes()
    return {"ok": True, "leads": leads}


@admin_router.get("/api/admin/export/leads")
async def export_leads_csv(request: Request):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"ok": False, "error": "No autorizado"})

    client_ip = request.client.host if request.client else "127.0.0.1"
    registrar_log_auditoria(
        tipo_evento="EXPORT_LEADS_CSV",
        detalles=f"Descarga de CSV de leads solicitada desde {client_ip}",
        usuario_origen="admin"
    )

    leads = obtener_todos_los_clientes()
    output = io.StringIO()
    # Escribir UTF-8 BOM para apertura nativa e inmediata con acentos en Excel
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        "ID", "Session ID", "Pase Digital Prioritario", "Nombre del Titular", 
        "Cédula", "Celular", "Correo Electrónico", "Perfil Laboral", 
        "Uso del Vehículo", "Tipo de Abono", "Momento de Compra", 
        "Temperatura Lead", "Fecha de Registro", "Última Actividad"
    ])
    for lead in leads:
        writer.writerow([
            lead.get("id"),
            lead.get("session_id"),
            lead.get("pase_digital") or "N/A",
            lead.get("nombre"),
            lead.get("cedula"),
            lead.get("celular"),
            lead.get("correo"),
            lead.get("sector_laboral") or "",
            lead.get("uso_vehiculo") or "",
            lead.get("tipo_abono") or "",
            lead.get("momento_compra") or "",
            lead.get("temperatura_lead") or "",
            lead.get("fecha_registro"),
            lead.get("ultima_actividad")
        ])

    csv_content = output.getvalue()
    response = Response(content=csv_content, media_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=leads_feria_cda.csv"
    return response


@admin_router.get("/api/admin/export/chats")
async def export_chats_json(request: Request):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"ok": False, "error": "No autorizado"})

    client_ip = request.client.host if request.client else "127.0.0.1"
    registrar_log_auditoria(
        tipo_evento="EXPORT_CHATS_JSON",
        detalles=f"Descarga de JSON de conversaciones solicitada desde {client_ip}",
        usuario_origen="admin"
    )

    chats = obtener_todas_las_conversaciones()
    json_content = json.dumps(chats, ensure_ascii=False, indent=2)
    response = Response(content=json_content, media_type="application/json; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=conversaciones_feria_cda.json"
    return response


def setup_admin_routes(app: FastAPI):
    """Registra los endpoints y vistas de administración en la aplicación FastAPI con alta prioridad."""
    inc = next((x for x in app.routes if hasattr(x, "original_router")), None)
    if inc and hasattr(inc, "original_router") and inc.original_router.routes:
        # Remover temporalmente el catch-all /{full_path:path} para que las rutas de admin tengan prioridad
        last_route = inc.original_router.routes.pop()
        inc.original_router.include_router(admin_router)
        inc.original_router.routes.append(last_route)
    else:
        app.include_router(admin_router)

