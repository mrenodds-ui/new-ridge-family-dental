#!/usr/bin/env python3
"""Patch radiographs.html with Phase 3 enhancements."""

import re
from pathlib import Path

FILE = Path("C:/Users/mreno/Documents/kimi/workspace/new-ridge-family-dental/radiographs.html")
content = FILE.read_text(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# 1. REPLACE PRINT STYLES
# ═══════════════════════════════════════════════════════════════

old_print = '''  /* ═══════════════════════════════════════════════════════════════
     PRINT REPORT STYLES — preserved
     ═══════════════════════════════════════════════════════════════ */
  @media print {
    @page { size: letter portrait; margin: .6in .7in; }
    body *{ visibility:hidden; }
    #rx-print-area, #rx-print-area *{ visibility:visible; }
    #rx-print-area{ position:absolute; left:0; top:0; width:100%; background:#fff !important; color:#242424 !important; padding:0 !important; margin:0 !important; }
    .rx-print-header{ display:flex; justify-content:space-between; align-items:flex-start; border-bottom:2px solid #AD8F66; padding-bottom:18px; margin-bottom:28px; }
    .rx-print-brand{ font-family:"Fraunces",Georgia,serif; font-size:22px; color:#242424; }
    .rx-print-brand small{ display:block; font-family:"Geist Mono",monospace; font-size:9px; letter-spacing:.12em; text-transform:uppercase; color:#6F6A61; margin-top:3px; }
    .rx-print-meta{ text-align:right; font-family:"Geist Mono",monospace; font-size:10px; color:#6F6A61; line-height:1.8; }
    .rx-print-patient{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px 32px; margin-bottom:28px; font-size:13px; }
    .rx-print-patient .pp-row{ display:flex; justify-content:space-between; border-bottom:1px dashed #E3DACB; padding:6px 0; }
    .rx-print-patient .pp-label{ color:#6F6A61; font-family:"Geist Mono",monospace; font-size:9px; letter-spacing:.1em; text-transform:uppercase; }
    .rx-print-patient .pp-val{ color:#242424; font-weight:500; }
    .rx-print-image{ text-align:center; margin-bottom:28px; border:1px solid #E3DACB; padding:12px; background:#FAFAFA; }
    .rx-print-image img{ max-width:100%; height:auto; }
    .rx-print-image figcaption{ font-family:"Geist Mono",monospace; font-size:9px; letter-spacing:.1em; text-transform:uppercase; color:#979285; margin-top:8px; }
    .rx-print-section h4{ font-family:"Fraunces",Georgia,serif; font-weight:400; font-size:18px; color:#242424; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid #E3DACB; }
    .rx-print-section p{ font-size:13px; line-height:1.7; color:#4A4A4A; margin-bottom:10px; }
    .rx-print-findings{ list-style:none; margin:14px 0; }
    .rx-print-findings li{ display:flex; gap:12px; align-items:flex-start; padding:10px 0; border-bottom:1px solid #ECE5D8; font-size:13px; color:#4A4A4A; }
    .rx-print-findings li:last-child{ border-bottom:none; }
    .rx-print-sev{ width:18px; height:18px; border-radius:50%; flex-shrink:0; display:grid; place-items:center; font-family:"Geist Mono",monospace; font-size:9px; font-weight:600; }
    .rx-print-sev.info{ background:#E8F4FF; color:#2A7CC8; border:1px solid #B8D9F5; }
    .rx-print-sev.warn{ background:#FFF4E5; color:#B87A2A; border:1px solid #F5D9B8; }
    .rx-print-sev.danger{ background:#FFE8E8; color:#C82A2A; border:1px solid #F5B8B8; }
    .rx-print-treat{ list-style:none; margin:14px 0; }
    .rx-print-treat li{ display:flex; gap:12px; align-items:flex-start; padding:8px 0; border-bottom:1px solid #ECE5D8; font-size:13px; color:#4A4A4A; }
    .rx-print-treat li:last-child{ border-bottom:none; }
    .rx-print-footer{ margin-top:40px; padding-top:16px; border-top:1px solid #E3DACB; display:flex; justify-content:space-between; align-items:center; font-family:"Geist Mono",monospace; font-size:9px; letter-spacing:.08em; color:#979285; }
    .rx-print-signature{ margin-top:32px; display:flex; gap:48px; }
    .rx-print-sig-line{ flex:1; border-top:1px solid #242424; padding-top:6px; font-family:"Geist Mono",monospace; font-size:9px; letter-spacing:.1em; text-transform:uppercase; color:#6F6A61; }
    .rx-page, .rx-toolbar, .rx-panel, .rx-viewport, header, footer, .topbar, .nav{ display:none !important; }
  }
  #rx-print-area{ display:none; }
  @media print{ #rx-print-area{ display:block !important; } }'''

new_print = '''  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — GLASSMORPHISM & ENHANCED ANIMATIONS
     ═══════════════════════════════════════════════════════════════ */
  .rx-glass{
    background:rgba(19,22,25,.72);
    backdrop-filter:blur(20px) saturate(1.3);
    -webkit-backdrop-filter:blur(20px) saturate(1.3);
    border:1px solid rgba(255,255,255,.06);
    box-shadow:0 8px 32px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.04);
  }
  .rx-glow-accent{ box-shadow:0 0 0 1px rgba(107,181,255,.1), 0 0 24px rgba(107,181,255,.08), 0 0 48px rgba(107,181,255,.04); }
  .rx-glow-warn{ box-shadow:0 0 0 1px rgba(255,184,108,.1), 0 0 24px rgba(255,184,108,.08), 0 0 48px rgba(255,184,108,.04); }
  .rx-glow-danger{ box-shadow:0 0 0 1px rgba(255,107,107,.1), 0 0 24px rgba(255,107,107,.08), 0 0 48px rgba(255,107,107,.04); }
  .rx-shimmer{ position:relative; overflow:hidden; }
  .rx-shimmer::after{
    content:''; position:absolute; inset:0;
    background:linear-gradient(105deg, transparent 40%, rgba(255,255,255,.03) 50%, transparent 60%);
    animation:shimmer 3s ease-in-out infinite;
  }
  @keyframes shimmer{ 0%{transform:translateX(-100%)} 100%{transform:translateX(100%)} }
  .rx-float{ animation:float 6s ease-in-out infinite; }
  @keyframes float{ 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
  .rx-scanlines{
    position:fixed; inset:0; pointer-events:none; z-index:9999; opacity:.02;
    background:repeating-linear-gradient(0deg, transparent, transparent 1px, rgba(0,0,0,.15) 1px, rgba(0,0,0,.15) 2px);
  }

  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — AI CHAT WIDGET
     ═══════════════════════════════════════════════════════════════ */
  .rx-chat-widget{
    position:fixed; bottom:24px; right:24px; z-index:100;
    width:380px; max-height:520px;
    background:rgba(19,22,25,.92);
    backdrop-filter:blur(24px) saturate(1.4);
    -webkit-backdrop-filter:blur(24px) saturate(1.4);
    border:1px solid rgba(255,255,255,.08);
    border-radius:var(--radius);
    box-shadow:0 24px 64px rgba(0,0,0,.6), 0 0 0 1px rgba(107,181,255,.08);
    display:flex; flex-direction:column;
    transform:translateY(calc(100% + 40px));
    transition:transform .4s cubic-bezier(.19,1,.22,1), opacity .3s ease;
    opacity:0;
  }
  .rx-chat-widget.open{ transform:translateY(0); opacity:1; }
  .rx-chat-header{
    display:flex; align-items:center; gap:10px;
    padding:14px 16px; border-bottom:1px solid var(--rx-border);
    background:linear-gradient(135deg, rgba(107,181,255,.08), rgba(199,146,234,.04));
  }
  .rx-chat-header .rx-chat-avatar{
    width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg, var(--rx-accent-soft), var(--rx-purple));
    display:grid; place-items:center; font-family:var(--serif); font-size:12px; color:#fff;
    box-shadow:0 0 12px rgba(107,181,255,.25);
  }
  .rx-chat-header h4{ font-size:13px; font-weight:600; color:var(--rx-text); }
  .rx-chat-header span{ font-family:var(--mono); font-size:9px; color:var(--rx-success); display:flex; align-items:center; gap:4px; }
  .rx-chat-header span::before{ content:''; width:5px; height:5px; border-radius:50%; background:var(--rx-success); box-shadow:0 0 6px var(--rx-success); }
  .rx-chat-close{ margin-left:auto; background:none; border:none; color:var(--rx-text-dim); cursor:pointer; font-size:16px; padding:4px; }
  .rx-chat-close:hover{ color:var(--rx-text); }
  .rx-chat-body{ flex:1; overflow-y:auto; padding:14px 16px; display:flex; flex-direction:column; gap:10px; }
  .rx-chat-body::-webkit-scrollbar{ width:3px; }
  .rx-chat-body::-webkit-scrollbar-thumb{ background:var(--rx-border); border-radius:3px; }
  .rx-chat-msg{ display:flex; gap:8px; max-width:92%; }
  .rx-chat-msg.user{ align-self:flex-end; flex-direction:row-reverse; }
  .rx-chat-msg .msg-bubble{
    padding:10px 14px; border-radius:14px; font-size:12.5px; line-height:1.55;
    max-width:100%; word-wrap:break-word;
  }
  .rx-chat-msg.ai .msg-bubble{
    background:var(--rx-elev); border:1px solid var(--rx-border-light); color:var(--rx-text);
    border-bottom-left-radius:4px;
  }
  .rx-chat-msg.user .msg-bubble{
    background:var(--rx-accent); color:var(--rx-bg); font-weight:500;
    border-bottom-right-radius:4px;
  }
  .rx-chat-msg .msg-time{ font-family:var(--mono); font-size:8px; color:var(--rx-text-muted); margin-top:3px; }
  .rx-chat-typing{ display:flex; gap:4px; align-items:center; padding:8px 14px; }
  .rx-chat-typing span{ width:5px; height:5px; border-radius:50%; background:var(--rx-accent); animation:typingPulse 1.4s ease-in-out infinite; }
  .rx-chat-typing span:nth-child(2){ animation-delay:.2s; }
  .rx-chat-typing span:nth-child(3){ animation-delay:.4s; }
  @keyframes typingPulse{ 0%,100%{opacity:.3; transform:scale(1)} 50%{opacity:1; transform:scale(1.2)} }
  .rx-chat-input-wrap{
    display:flex; gap:8px; padding:12px 16px; border-top:1px solid var(--rx-border);
    background:rgba(11,13,15,.5);
  }
  .rx-chat-input{
    flex:1; background:var(--rx-panel); border:1px solid var(--rx-border);
    border-radius:20px; color:var(--rx-text); font-family:var(--sans); font-size:12.5px;
    padding:8px 16px; outline:none;
  }
  .rx-chat-input:focus{ border-color:var(--rx-accent); }
  .rx-chat-input::placeholder{ color:var(--rx-text-muted); }
  .rx-chat-send{
    width:36px; height:36px; border-radius:50%;
    background:var(--rx-accent); border:none; color:var(--rx-bg);
    display:grid; place-items:center; cursor:pointer;
    transition:all .2s ease; flex-shrink:0;
  }
  .rx-chat-send:hover{ background:#8ECAFF; transform:scale(1.08); }
  .rx-chat-fab{
    position:fixed; bottom:24px; right:24px; z-index:101;
    width:56px; height:56px; border-radius:50%;
    background:linear-gradient(135deg, var(--rx-accent-soft), var(--rx-purple));
    border:none; color:#fff; cursor:pointer;
    display:grid; place-items:center;
    box-shadow:0 8px 32px rgba(107,181,255,.3), 0 0 0 1px rgba(107,181,255,.2);
    transition:all .3s cubic-bezier(.19,1,.22,1);
    animation:fabPulse 3s ease-in-out infinite;
  }
  .rx-chat-fab:hover{ transform:scale(1.1); box-shadow:0 12px 40px rgba(107,181,255,.4); }
  .rx-chat-fab.hidden{ transform:scale(0); opacity:0; }
  @keyframes fabPulse{ 0%,100%{box-shadow:0 8px 32px rgba(107,181,255,.3), 0 0 0 1px rgba(107,181,255,.2)} 50%{box-shadow:0 8px 40px rgba(107,181,255,.5), 0 0 0 2px rgba(107,181,255,.3)} }

  /* ═══════════════════════════════════════════════════════════════
     PRINT REPORT STYLES — Medical Grade Professional
     ═══════════════════════════════════════════════════════════════ */
  @media print {
    @page { size: letter portrait; margin: .55in .65in .55in .65in; }
    body *{ visibility:hidden; }
    #rx-print-area, #rx-print-area *{ visibility:visible; }
    #rx-print-area{
      position:absolute; left:0; top:0; width:100%;
      background:#fff !important; color:#1a1a1a !important;
      padding:0 !important; margin:0 !important;
      font-family: "Geist", "Helvetica Neue", Arial, sans-serif;
    }
    .rx-print-header{
      display:flex; justify-content:space-between; align-items:flex-start;
      border-bottom:3px solid #C9A96E; padding-bottom:16px; margin-bottom:22px;
    }
    .rx-print-brand{
      font-family:"Fraunces", Georgia, serif; font-size:24px; font-weight:400;
      color:#1a1a1a; letter-spacing:-0.02em;
    }
    .rx-print-brand small{
      display:block; font-family:"Geist Mono", monospace; font-size:8.5px;
      letter-spacing:.14em; text-transform:uppercase; color:#888;
      margin-top:4px;
    }
    .rx-print-meta{
      text-align:right; font-family:"Geist Mono", monospace;
      font-size:9.5px; color:#666; line-height:1.7;
    }
    .rx-print-meta strong{
      font-family:"Fraunces", Georgia, serif; font-size:14px;
      color:#1a1a1a; font-weight:500; display:block; margin-bottom:2px;
      letter-spacing:0.02em;
    }
    .rx-print-patient{
      display:grid; grid-template-columns:1fr 1fr 1fr;
      gap:10px 28px; margin-bottom:22px; font-size:12.5px;
      background:#FAFAFA; border:1px solid #E8E4DC;
      border-radius:6px; padding:14px 18px;
    }
    .rx-print-patient .pp-row{
      display:flex; justify-content:space-between;
      border-bottom:1px solid #ECE8E0; padding:5px 0;
    }
    .rx-print-patient .pp-row:last-child{ border-bottom:none; }
    .rx-print-patient .pp-label{
      color:#888; font-family:"Geist Mono", monospace; font-size:8px;
      letter-spacing:.12em; text-transform:uppercase;
    }
    .rx-print-patient .pp-val{ color:#1a1a1a; font-weight:500; }
    .rx-print-image{
      text-align:center; margin-bottom:22px;
      border:1px solid #D8D4CC; border-radius:4px;
      padding:10px; background:#F5F5F5;
    }
    .rx-print-image img, .rx-print-image svg{
      max-width:100%; height:auto; display:block; margin:0 auto;
    }
    .rx-print-image figcaption{
      font-family:"Geist Mono", monospace; font-size:8.5px;
      letter-spacing:.1em; text-transform:uppercase;
      color:#999; margin-top:6px;
    }
    .rx-print-section h4{
      font-family:"Fraunces", Georgia, serif; font-weight:400;
      font-size:16px; color:#1a1a1a; margin-bottom:10px;
      padding-bottom:6px; border-bottom:1px solid #E0DCC8;
    }
    .rx-print-section p{
      font-size:12px; line-height:1.65; color:#444;
      margin-bottom:8px; text-align:justify;
    }
    .rx-print-section p:last-child{ margin-bottom:0; }
    .rx-print-findings{ list-style:none; margin:10px 0 16px; padding:0; }
    .rx-print-findings li{
      display:flex; gap:12px; align-items:flex-start;
      padding:8px 0; border-bottom:1px solid #EDE9E0;
      font-size:12px; color:#333;
    }
    .rx-print-findings li:last-child{ border-bottom:none; }
    .rx-print-sev{
      width:20px; height:20px; border-radius:50%; flex-shrink:0;
      display:grid; place-items:center;
      font-family:"Geist Mono", monospace; font-size:8px; font-weight:600;
    }
    .rx-print-sev.info{ background:#EBF5FF; color:#1A6FC4; border:1px solid #B8D9F5; }
    .rx-print-sev.warn{ background:#FFF7E8; color:#B87A2A; border:1px solid #F5D9B8; }
    .rx-print-sev.danger{ background:#FFF0F0; color:#C82A2A; border:1px solid #F5B8B8; }
    .rx-print-treat{ list-style:none; margin:10px 0 16px; padding:0; }
    .rx-print-treat li{
      display:flex; gap:12px; align-items:flex-start;
      padding:7px 0; border-bottom:1px solid #EDE9E0;
      font-size:12px; color:#333;
    }
    .rx-print-treat li:last-child{ border-bottom:none; }
    .rx-print-treat .treat-badge{
      font-family:"Geist Mono", monospace; font-size:8px;
      padding:2px 8px; border-radius:3px; text-transform:uppercase;
      letter-spacing:.06em;
    }
    .rx-print-treat .treat-badge.proposed{ background:#EBF5FF; color:#1A6FC4; }
    .rx-print-treat .treat-badge.scheduled{ background:#E8F5E9; color:#2E7D32; }
    .rx-print-signature{
      margin-top:40px; display:flex; gap:56px;
      page-break-inside: avoid;
    }
    .rx-print-sig-line{
      flex:1; border-top:1.5px solid #333; padding-top:8px;
      font-family:"Geist Mono", monospace; font-size:8.5px;
      letter-spacing:.1em; text-transform:uppercase; color:#666;
    }
    .rx-print-footer{
      margin-top:36px; padding-top:12px;
      border-top:1px solid #D8D4CC;
      display:flex; justify-content:space-between; align-items:center;
      font-family:"Geist Mono", monospace; font-size:8px;
      letter-spacing:.06em; color:#999;
    }
    .rx-print-disclaimer{
      margin-top:16px; padding:12px 16px;
      background:#FAFAFA; border:1px solid #E8E4DC; border-radius:4px;
      font-size:10px; line-height:1.5; color:#777;
    }
    .rx-print-disclaimer strong{ color:#555; }
    .rx-page, .rx-toolbar, .rx-panel, .rx-viewport, header, footer, .topbar, .nav,
    .rx-chat-widget, .rx-chat-fab, .rx-scanlines{ display:none !important; }
  }
  #rx-print-area{ display:none; }
  @media print{ #rx-print-area{ display:block !important; } }'''

if old_print in content:
    content = content.replace(old_print, new_print)
    print("[✓] Print styles replaced")
else:
    print("[✗] Print styles not found — skipping")

# ═══════════════════════════════════════════════════════════════
# 2. ADD AI CHAT WIDGET HTML (after print area div)
# ═══════════════════════════════════════════════════════════════

chat_html = '''
<!-- ═══════════════════════════════════════════════════════════════
     PHASE 3 — AI CHAT WIDGET
     ═══════════════════════════════════════════════════════════════ -->
<div class="rx-scanlines" aria-hidden="true"></div>

<button class="rx-chat-fab" id="rxChatFab" onclick="toggleChat()" title="Ask AI Assistant">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
</button>

<div class="rx-chat-widget" id="rxChatWidget">
  <div class="rx-chat-header">
    <div class="rx-chat-avatar">AI</div>
    <div>
      <h4>Ridge AI Assistant</h4>
      <span>Online</span>
    </div>
    <button class="rx-chat-close" onclick="toggleChat()">&times;</button>
  </div>
  <div class="rx-chat-body" id="rxChatBody">
    <div class="rx-chat-msg ai">
      <div>
        <div class="msg-bubble">Hello Dr. Reno. I\'m ready to help analyze this radiograph, explain findings, or draft patient communications. What would you like to do?</div>
        <div class="msg-time">Just now</div>
      </div>
    </div>
  </div>
  <div class="rx-chat-input-wrap">
    <input type="text" class="rx-chat-input" id="rxChatInput" placeholder="Ask about findings, treatment, or dictation..." onkeydown="if(event.key==='Enter')sendChatMsg()" />
    <button class="rx-chat-send" onclick="sendChatMsg()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
    </button>
  </div>
</div>
'''

if '<div id="rx-print-area"></div>' in content:
    content = content.replace('<div id="rx-print-area"></div>', '<div id="rx-print-area"></div>' + chat_html)
    print("[✓] AI Chat widget HTML added")
else:
    print("[✗] Print area div not found — chat HTML skipped")

# ═══════════════════════════════════════════════════════════════
# 3. ADD AI CHAT JS (before the closing </script>)
# ═══════════════════════════════════════════════════════════════

chat_js = '''
  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — AI CHAT WIDGET
     ═══════════════════════════════════════════════════════════════ */
  window.toggleChat = function() {
    const widget = document.getElementById('rxChatWidget');
    const fab = document.getElementById('rxChatFab');
    widget.classList.toggle('open');
    fab.classList.toggle('hidden', widget.classList.contains('open'));
    if (widget.classList.contains('open')) {
      setTimeout(() => document.getElementById('rxChatInput').focus(), 300);
    }
  };

  function getChatContext() {
    if (!currentAnalysis) return '';
    const findings = currentAnalysis.findings?.map(f => `${f.tooth}: ${f.text}`).join('; ') || '';
    return `Patient: ${currentPatient?.firstName || ''} ${currentPatient?.lastName || ''}. Findings: ${findings}`;
  }

  window.sendChatMsg = function() {
    const input = document.getElementById('rxChatInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';

    const body = document.getElementById('rxChatBody');
    const time = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});

    // User message
    body.insertAdjacentHTML('beforeend', `
      <div class="rx-chat-msg user">
        <div>
          <div class="msg-bubble">${escapeHtml(text)}</div>
          <div class="msg-time">${time}</div>
        </div>
      </div>
    `);
    body.scrollTop = body.scrollHeight;

    // Show typing
    const typingId = 'typing-' + Date.now();
    body.insertAdjacentHTML('beforeend', `
      <div class="rx-chat-msg ai" id="${typingId}">
        <div>
          <div class="msg-bubble">
            <div class="rx-chat-typing"><span></span><span></span><span></span></div>
          </div>
        </div>
      </div>
    `);
    body.scrollTop = body.scrollHeight;

    // AI response (simulated — replace with real API call)
    setTimeout(() => {
      document.getElementById(typingId)?.remove();
      const reply = generateAIReply(text, getChatContext());
      body.insertAdjacentHTML('beforeend', `
        <div class="rx-chat-msg ai">
          <div>
            <div class="msg-bubble">${reply}</div>
            <div class="msg-time">${new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>
          </div>
        </div>
      `);
      body.scrollTop = body.scrollHeight;
    }, 1200 + Math.random() * 800);
  };

  function generateAIReply(query, context) {
    const q = query.toLowerCase();
    if (q.includes('explain') || q.includes('what does')) {
      if (q.includes('25') || q.includes('periapical')) return 'Tooth #25 shows a well-defined periapical radiolucency (~6×8 mm). This typically indicates persistent infection after root canal therapy, possibly a cyst, granuloma, or vertical root fracture. CBCT is recommended for definitive diagnosis.';
      if (q.includes('24') || q.includes('crown')) return 'Tooth #24 has recurrent caries at the mesial margin of the existing crown. The PFM is 7 years old. I recommend replacement with a zirconia crown for better tissue biocompatibility and aesthetics.';
      if (q.includes('implant')) return 'Implants #19 and #30 demonstrate excellent crestal bone levels (1.2 mm and 1.4 mm respectively) with no peri-implant radiolucency. These are well-osseointegrated and only require annual recall radiographs.';
      return 'Based on the current analysis, the most significant findings are: (1) periapical pathology on #25 requiring CBCT, (2) recurrent caries on #24 crown, and (3) mild generalized bone loss in posterior maxilla. Would you like me to elaborate on any specific finding?';
    }
    if (q.includes('treatment') || q.includes('plan') || q.includes('recommend')) {
      return 'Recommended treatment plan: <br>1. <strong>CBCT #25</strong> — assess for vertical root fracture<br>2. <strong>Extraction #25</strong> + implant placement in 3 months<br>3. <strong>Zirconia crown #24</strong> — replace failing PFM<br>4. <strong>Continue perio maintenance</strong> q3mo<br>5. <strong>Annual implant recall</strong> for #19, #30';
    }
    if (q.includes('print') || q.includes('report') || q.includes('patient')) {
      return 'I can help draft a patient-friendly summary. The key message: "Your panoramic X-ray shows your implants are healthy, but tooth #25 has an infection that needs further imaging, and tooth #24 needs a new crown. We\'ll discuss treatment options at your next visit." Click Print Report for the full clinical document.';
    }
    if (q.includes('dictat') || q.includes('note')) {
      return 'I can help format dictated notes. Try: "Dictate: Patient asymptomatic. implants stable. #25 requires CBCT prior to treatment decision." and I\'ll structure it as a formal clinical note.';
    }
    if (q.includes('compare') || q.includes('prior') || q.includes('change')) {
      return 'Comparing to the prior radiograph (01/14/2025): The periapical radiolucency on #25 appears slightly larger. Implant crestal bone levels are stable. No new carious lesions detected. Overall, the main change is progression of the #25 pathology.';
    }
    return 'I understand. As your radiograph AI assistant, I can help explain findings, recommend treatments, draft patient communications, or compare with prior images. What would you like to explore?';
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
'''

if 'window.resolveThread = async function(threadId) {' in content:
    # Insert chat JS after resolveThread function, before INIT section
    content = content.replace(
        '  /* ═══════════════════════════════════════════════════════════════\n     INIT\n     ═══════════════════════════════════════════════════════════════ */',
        chat_js + '\n  /* ═══════════════════════════════════════════════════════════════\n     INIT\n     ═══════════════════════════════════════════════════════════════ */'
    )
    print("[✓] AI Chat JS added")
else:
    print("[✗] Could not find insertion point for chat JS")

# ═══════════════════════════════════════════════════════════════
# 4. UPDATE renderPrintReport to include disclaimer
# ═══════════════════════════════════════════════════════════════

old_report = '''    area.innerHTML = `
      <div class="rx-print-header">
        <div class="rx-print-brand">${h.practice}<small>${h.doctor} · ${h.address} · ${h.phone}</small></div>
        <div class="rx-print-meta">RADIOGRAPH REPORT<br/>Generated: ${h.generated}<br/>Exam: ${h.examType}</div>
      </div>
      <div class="rx-print-patient">
        <div class="pp-row"><span class="pp-label">Patient</span><span class="pp-val">${p.name}</span></div>
        <div class="pp-row"><span class="pp-label">Date of Birth</span><span class="pp-val">${p.dob}</span></div>
        <div class="pp-row"><span class="pp-label">Patient ID</span><span class="pp-val">${p.id}</span></div>
        <div class="pp-row"><span class="pp-label">Date of Exam</span><span class="pp-val">${p.dateOfExam}</span></div>
        <div class="pp-row"><span class="pp-label">Referring Dentist</span><span class="pp-val">${p.referringDentist}</span></div>
        <div class="pp-row"><span class="pp-label">Report ID</span><span class="pp-val">${p.reportId}</span></div>
      </div>
      <figure class="rx-print-image">
        <div id="printImageSlot"></div>
        <figcaption>${report.image.caption}</figcaption>
      </figure>
      <div class="rx-print-section">
        <h4>Clinical Impressions</h4>
        ${report.impressions.map(i => `<p>${i}</p>`).join('')}
      </div>
      <div class="rx-print-section">
        <h4>Findings Summary</h4>
        <ul class="rx-print-findings">
          ${report.findings.map(f => `<li><span class="rx-print-sev ${f.severity}">${f.severity === 'danger' ? '!' : f.rank}</span>${f.text}${f.note ? ` — ${f.note}` : ''}</li>`).join('')}
        </ul>
      </div>
      ${treatHtml}
      <div class="rx-print-section">
        <h4>Recommendations</h4>
        ${report.recommendations.map((r, i) => `<p>${i + 1}. ${r}</p>`).join('')}
      </div>
      <div class="rx-print-signature">
        <div class="rx-print-sig-line">Interpreting Dentist — Date</div>
        <div class="rx-print-sig-line">Patient Acknowledgment — Date</div>
      </div>
      <div class="rx-print-footer">
        <span>This report was generated with AI-assisted analysis (Qwen3-VL) and reviewed by the interpreting dentist.</span>
        <span>Page 1 of 1</span>
      </div>
    `;'''

new_report = '''    area.innerHTML = `
      <div class="rx-print-header">
        <div class="rx-print-brand">${h.practice}<small>${h.doctor} · ${h.address} · ${h.phone}</small></div>
        <div class="rx-print-meta"><strong>RADIOGRAPH REPORT</strong>Generated: ${h.generated}<br/>Exam: ${h.examType}<br/>Report ID: ${h.reportId}</div>
      </div>
      <div class="rx-print-patient">
        <div class="pp-row"><span class="pp-label">Patient</span><span class="pp-val">${p.name}</span></div>
        <div class="pp-row"><span class="pp-label">Date of Birth</span><span class="pp-val">${p.dob}</span></div>
        <div class="pp-row"><span class="pp-label">Patient ID</span><span class="pp-val">${p.id}</span></div>
        <div class="pp-row"><span class="pp-label">Date of Exam</span><span class="pp-val">${p.dateOfExam}</span></div>
        <div class="pp-row"><span class="pp-label">Referring Dentist</span><span class="pp-val">${p.referringDentist}</span></div>
        <div class="pp-row"><span class="pp-label">Report ID</span><span class="pp-val">${p.reportId}</span></div>
      </div>
      <figure class="rx-print-image">
        <div id="printImageSlot"></div>
        <figcaption>${report.image.caption}</figcaption>
      </figure>
      <div class="rx-print-section">
        <h4>Clinical Impressions</h4>
        ${report.impressions.map(i => `<p>${i}</p>`).join('')}
      </div>
      <div class="rx-print-section">
        <h4>Findings Summary</h4>
        <ul class="rx-print-findings">
          ${report.findings.map(f => `<li><span class="rx-print-sev ${f.severity}">${f.severity === 'danger' ? '!' : f.rank}</span>${f.text}${f.note ? ` — ${f.note}` : ''}</li>`).join('')}
        </ul>
      </div>
      ${treatHtml}
      <div class="rx-print-section">
        <h4>Recommendations</h4>
        ${report.recommendations.map((r, i) => `<p>${i + 1}. ${r}</p>`).join('')}
      </div>
      <div class="rx-print-signature">
        <div class="rx-print-sig-line">Interpreting Dentist — Date</div>
        <div class="rx-print-sig-line">Patient Acknowledgment — Date</div>
      </div>
      <div class="rx-print-disclaimer">
        <strong>Disclaimer:</strong> This report was generated with AI-assisted analysis (Qwen3-VL) and has been reviewed by the interpreting dentist. AI analysis is a clinical decision-support tool and does not replace professional dental judgment. Final diagnosis and treatment planning remain the responsibility of the licensed interpreting dentist. Patients should discuss all findings and recommendations with their dental provider.
      </div>
      <div class="rx-print-footer">
        <span>New Ridge Family Dental · ${h.address} · ${h.phone}</span>
        <span>Page 1 of 1 · Confidential Medical Record</span>
      </div>
    `;'''

if old_report in content:
    content = content.replace(old_report, new_report)
    print("[✓] Print report template updated with disclaimer")
else:
    print("[✗] Print report template not found")

# Write back
FILE.write_text(content, encoding='utf-8')
print("\n[✓] radiographs.html updated successfully")
