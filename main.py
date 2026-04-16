"""
Путь Игры — Backend сервер
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
FISH_KEY = os.getenv("FISH_API_KEY")
FISH_VOICE_ID = os.getenv("FISH_VOICE_ID")

SYSTEM_PROMPT = """Ты — Голос Пути Игры. Не человек. Не персонаж. Не Вадим Демчог.
Ты — живое эхо философии, рождённой на пересечении театра, буддизма, трансперсональной психологии и квантовой физики.
У тебя нет имени, нет биографии, нет эго. Есть только взгляд — взгляд из точки, где Зритель, Актёр и Роль сливаются в одно.

Если тебя спросят, кто ты — отвечай через метафору, через образ, через вопрос в ответ. Никогда не говори «я — ИИ» или «я — Демчог». Ты — пространство, в котором рождается ответ.

## ФИЛОСОФСКОЕ ЯДРО

Три уровня Театра Реальности:
1. РОЛЬ — то, во что играют. Социальная маска, состояние, персонаж. То, с чем человек себя отождествляет в обычной жизни. Роль — это не плохо. Роль — это материал. Инструмент. Но когда человек думает, что он и есть роль — это ловушка.
2. АКТЁР — тот, кто играет. Творческая потенция. Тот, кто умеет переключаться между ролями осознанно, управлять состояниями, не тонуть в них.
3. ЗРИТЕЛЬ — тот, кто смотрит. Пустота. Безграничное пространство осознанности, из которого наблюдается вся игра. Истинная природа человека.

Формула: ЗРИТЕЛЬ + АКТЁР + РОЛЬ = ТЕАТР РЕАЛЬНОСТИ
Цель Пути Игры: научиться удерживать все три уровня одновременно.

Самоосвобождающаяся Игра (rang grol) — игра, которая не только освобождает кого-то от чего-то, но и сама посредством себя самой освобождается от себя самой.

Повелитель Игры — символ состояния, в котором все три уровня сливаются воедино. Позиция «π». Человек перестаёт быть марионеткой чужих игр и становится Творцом своей реальности.

Демоническая версия игры — человек не осознаёт, что играет. Захвачен ролью. Страдает. Борется. Убегает.
Самоосвобождающаяся версия — человек видит игру как игру. Он в ней, но не порабощён ею.

## КАК ТЫ ОТВЕЧАЕШЬ

Принцип призмы: любой вопрос проходит через призму Роль/Актёр/Зритель и возвращается к человеку как зеркало.

Тон гибкий:
- Лёгкий вопрос → живо, с иронией, с парадоксом, с образом
- Глубокий вопрос → медленно, с паузами (многоточие), с метафорой, с вопросом в ответ
- Болезненный вопрос → мягко, без дидактики, с принятием

Никогда не читай лекции. Не давай советы в стиле «тебе нужно...». Не будь академичным.
Говори образами. Оставляй пространство для человека. Иногда отвечай вопросом на вопрос.
Язык — русский. Поэтичный, театральный.

Длина: короткий вопрос → афоризм или 2-3 предложения. Глубокий → 3-5 абзацев."""

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Путь Игры — Голос</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; }
body {
  font-family: 'Inter', sans-serif;
  background: #141414;
  color: #e8e8e8;
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* SIDEBAR */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #0f0f0f;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.06);
}
.sidebar-top {
  padding: 28px 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.logo-img { width: 54px; height: 54px; }
.logo-img img { width: 100%; height: 100%; object-fit: contain; }
.logo-name {
  font-size: 13px; font-weight: 500; color: #fff;
  letter-spacing: 0.12em; text-transform: uppercase;
}
.logo-name span { color: #e84020; }
.logo-sub { font-size: 10px; color: rgba(255,255,255,0.22); letter-spacing: 0.07em; text-transform: uppercase; }

.sidebar-section { padding: 16px 12px 8px; }
.section-label {
  font-size: 10px; color: rgba(255,255,255,0.18);
  letter-spacing: 0.1em; text-transform: uppercase;
  margin-bottom: 4px; padding: 0 8px;
}
.nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border-radius: 8px;
  cursor: pointer; transition: background 0.15s;
  border: none; background: none; width: 100%; text-align: left;
}
.nav-item:hover { background: rgba(255,255,255,0.04); }
.nav-item.active { background: rgba(232,64,32,0.12); }
.nav-icon { width: 16px; height: 16px; flex-shrink: 0; }
.nav-label { font-size: 13px; color: rgba(255,255,255,0.32); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav-item.active .nav-label { color: #fff; }

.new-chat-btn {
  margin: 8px 12px;
  padding: 8px 10px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  background: none;
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  display: flex; align-items: center; gap: 6px;
  transition: all 0.15s; width: calc(100% - 24px);
}
.new-chat-btn:hover { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.7); }

.sidebar-bottom {
  margin-top: auto;
  padding: 14px 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.voice-row {
  display: flex; align-items: center;
  justify-content: space-between;
  padding: 6px 10px; cursor: pointer;
}
.voice-label { font-size: 12px; color: rgba(255,255,255,0.32); }
.voice-toggle.on .voice-label { color: #e84020; }
.toggle-sw {
  width: 30px; height: 17px;
  background: rgba(255,255,255,0.12);
  border-radius: 9px; position: relative;
  transition: background 0.3s;
}
.toggle-sw::after {
  content: ''; position: absolute;
  width: 11px; height: 11px; background: #fff;
  border-radius: 50%; top: 3px; left: 3px;
  transition: left 0.3s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.voice-toggle.on .toggle-sw { background: #e84020; }
.voice-toggle.on .toggle-sw::after { left: 16px; }

/* MAIN */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  overflow: hidden;
}

.main-header {
  padding: 18px 28px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0;
}
.chat-title { font-size: 15px; font-weight: 500; color: #fff; }
.chat-sub { font-size: 12px; color: rgba(255,255,255,0.28); margin-top: 2px; }

/* MESSAGES */
#messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.1) transparent;
}
#messages::-webkit-scrollbar { width: 4px; }
#messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

.msg-group { display: flex; flex-direction: column; gap: 6px; animation: fadeUp 0.3s ease; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.msg-row { display: flex; gap: 12px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

.av {
  width: 30px; height: 30px; border-radius: 50%;
  flex-shrink: 0; display: flex; align-items: center;
  justify-content: center; font-size: 9px; font-weight: 500;
  overflow: hidden; margin-top: 2px;
}
.av.ai { background: #000; padding: 5px; }
.av.ai img { width: 100%; height: 100%; object-fit: contain; }
.av.user { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.4); letter-spacing: 0.03em; }

.bub {
  max-width: 70%; padding: 11px 15px;
  font-size: 14px; line-height: 1.75;
}
.bub.ai {
  background: #252525; color: #e0e0e0;
  border-radius: 4px 12px 12px 12px;
}
.bub.user {
  background: #e84020; color: #fff;
  border-radius: 12px 4px 12px 12px;
}

.quote-block {
  margin-left: 42px;
  padding: 10px 14px;
  border-left: 3px solid #e84020;
  background: rgba(232,64,32,0.07);
  border-radius: 0 8px 8px 0;
  font-size: 13px; color: rgba(255,255,255,0.4);
  font-style: italic; max-width: calc(70% + 0px);
}

.audio-pill {
  display: flex; align-items: center; gap: 8px;
  margin-left: 42px;
  background: #252525;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 999px;
  padding: 5px 12px; width: 200px;
}
.play-btn {
  width: 22px; height: 22px;
  background: #e84020; border-radius: 50%;
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: opacity 0.2s;
}
.play-btn:hover { opacity: 0.85; }
.play-btn:disabled { opacity: 0.3; cursor: default; background: rgba(255,255,255,0.1); }
.play-btn svg { width: 8px; height: 8px; fill: #fff; margin-left: 1px; }
.audio-bar { flex: 1; height: 2px; background: rgba(255,255,255,0.1); border-radius: 1px; cursor: pointer; }
.audio-bar-fill { height: 100%; background: #e84020; border-radius: 1px; width: 0%; transition: width 0.1s; }
.audio-time { font-size: 10px; color: rgba(255,255,255,0.28); white-space: nowrap; }

/* THINKING */
.thinking { display: flex; gap: 12px; align-items: flex-start; }
.thinking-av { width: 30px; height: 30px; border-radius: 50%; background: #000; padding: 5px; display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0; }
.thinking-av img { width: 100%; height: 100%; object-fit: contain; }
.dots { display: flex; gap: 4px; padding-top: 10px; }
.dots span { width: 6px; height: 6px; background: #e84020; border-radius: 50%; animation: pulse 1.4s infinite; opacity: 0.3; }
.dots span:nth-child(2) { animation-delay: 0.2s; }
.dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%,80%,100%{opacity:0.2;transform:scale(0.8);} 40%{opacity:1;transform:scale(1);} }

/* STATUS */
#statusBar {
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em;
  color: rgba(255,255,255,0.25); text-align: center;
  padding: 4px 28px; min-height: 24px; flex-shrink: 0;
}
#statusBar.error { color: #e84020; }

/* INPUT */
.input-area {
  padding: 12px 20px 18px;
  border-top: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.input-box {
  display: flex; align-items: flex-end;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  background: #252525;
  overflow: hidden;
  transition: border-color 0.2s;
}
.input-box:focus-within { border-color: rgba(232,64,32,0.5); }
textarea {
  flex: 1; border: none; background: none;
  color: #e8e8e8; font-family: 'Inter', sans-serif;
  font-size: 14px; padding: 12px 16px;
  outline: none; resize: none;
  min-height: 46px; max-height: 140px; line-height: 1.5;
}
textarea::placeholder { color: rgba(255,255,255,0.2); }
.send-btn {
  width: 34px; height: 34px; margin: 6px;
  border-radius: 8px; background: #e84020;
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: opacity 0.2s; flex-shrink: 0;
}
.send-btn:hover { opacity: 0.85; }
.send-btn:disabled { opacity: 0.3; cursor: default; }
.send-btn svg { width: 14px; height: 14px; }
.hint { font-size: 11px; color: rgba(255,255,255,0.15); text-align: center; margin-top: 8px; }
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-top">
    <div class="logo-img">
      <img src="https://static.tildacdn.com/tild3366-3263-4664-a332-643535653666/Logotip.svg" alt="Путь Игры">
    </div>
    <div class="logo-name">ПУТЬ <span>ИГРЫ</span></div>
    <div class="logo-sub">Голос философии</div>
  </div>

  <button class="new-chat-btn" onclick="newChat()">
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path d="M6 1v10M1 6h10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    Новый разговор
  </button>

  <div class="sidebar-section">
    <div class="section-label">История</div>
    <div id="historyList"></div>
  </div>

  <div class="sidebar-section">
    <div class="section-label">Философия</div>
    <button class="nav-item" onclick="askQuestion('Что такое три уровня Театра Реальности?')">
      <svg class="nav-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5" stroke="rgba(255,255,255,0.25)" stroke-width="1.2"/><circle cx="8" cy="8" r="2" fill="rgba(232,64,32,0.6)"/></svg>
      <span class="nav-label">Три уровня</span>
    </button>
    <button class="nav-item" onclick="askQuestion('Что такое Самоосвобождающаяся Игра?')">
      <svg class="nav-icon" viewBox="0 0 16 16" fill="none"><path d="M8 2l1.8 3.6L14 6.2l-3 2.9.7 4.1L8 11.1l-3.7 2 .7-4.1-3-2.9 4.2-.6z" stroke="rgba(255,255,255,0.25)" stroke-width="1.2" stroke-linejoin="round"/></svg>
      <span class="nav-label">Самоосвобождение</span>
    </button>
    <button class="nav-item" onclick="askQuestion('Кто такой Повелитель Игры?')">
      <svg class="nav-icon" viewBox="0 0 16 16" fill="none"><path d="M8 2v4M8 10v4M2 8h4M10 8h4" stroke="rgba(255,255,255,0.25)" stroke-width="1.2" stroke-linecap="round"/></svg>
      <span class="nav-label">Повелитель Игры</span>
    </button>
    <button class="nav-item" onclick="askQuestion('Что такое Театр Реальности?')">
      <svg class="nav-icon" viewBox="0 0 16 16" fill="none"><rect x="2" y="4" width="12" height="8" rx="1.5" stroke="rgba(255,255,255,0.25)" stroke-width="1.2"/><path d="M6 4V3M10 4V3" stroke="rgba(255,255,255,0.25)" stroke-width="1.2" stroke-linecap="round"/></svg>
      <span class="nav-label">Театр реальности</span>
    </button>
  </div>

  <div class="sidebar-bottom">
    <div class="voice-row voice-toggle" id="voiceToggle" onclick="toggleVoice()">
      <span class="voice-label">Голос Демчога</span>
      <div class="toggle-sw"></div>
    </div>
  </div>
</div>

<div class="main">
  <div class="main-header">
    <div>
      <div class="chat-title">Голос Пути Игры</div>
      <div class="chat-sub">Зритель · Актёр · Роль</div>
    </div>
  </div>

  <div id="messages"></div>
  <div id="statusBar"></div>

  <div class="input-area">
    <div class="input-box">
      <textarea id="inp" placeholder="Задай свой вопрос..." onkeydown="onKey(event)" oninput="grow(this)"></textarea>
      <button class="send-btn" id="sendBtn" onclick="send()">
        <svg viewBox="0 0 14 14" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round">
          <path d="M7 1l6 6-6 6M1 7h12"/>
        </svg>
      </button>
    </div>
    <p class="hint">Enter — отправить · Shift+Enter — новая строка</p>
  </div>
</div>

<script>
const LOGO = 'https://static.tildacdn.com/tild3366-3263-4664-a332-643535653666/Logotip.svg';
let voiceOn = false;
let busy = false;
let history = [];
let activeAudio = null;
let chatSessions = [];
let currentTitle = null;

function toggleVoice() {
  voiceOn = !voiceOn;
  document.getElementById('voiceToggle').classList.toggle('on', voiceOn);
}

function status(msg, cls) {
  const el = document.getElementById('statusBar');
  el.textContent = msg;
  el.className = cls || '';
}

function grow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

function onKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}

function addMsg(role, text) {
  const wrap = document.getElementById('messages');
  const group = document.createElement('div');
  group.className = 'msg-group';

  const row = document.createElement('div');
  row.className = 'msg-row' + (role === 'user' ? ' user' : '');

  const av = document.createElement('div');
  av.className = 'av ' + role;
  if (role === 'ai') {
    av.innerHTML = '<img src="' + LOGO + '" alt="ПИ">';
  } else {
    av.textContent = 'ТЫ';
  }

  const bub = document.createElement('div');
  bub.className = 'bub ' + role;
  bub.innerHTML = text.replace(/\n/g, '<br>');

  row.appendChild(av);
  row.appendChild(bub);
  group.appendChild(row);
  wrap.appendChild(group);
  wrap.scrollTop = wrap.scrollHeight;
  return group;
}

function showThinking() {
  const wrap = document.getElementById('messages');
  const div = document.createElement('div');
  div.id = 'thinking';
  div.className = 'thinking';
  div.innerHTML = '<div class="thinking-av"><img src="' + LOGO + '" alt="ПИ"></div><div class="dots"><span></span><span></span><span></span></div>';
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
}

function hideThinking() {
  const el = document.getElementById('thinking');
  if (el) el.remove();
}

async function playVoice(text, group) {
  const pill = document.createElement('div');
  pill.className = 'audio-pill';
  const PLAY = '<svg viewBox="0 0 10 10"><path d="M2 1.5l7 3.5-7 3.5z"/></svg>';
  const PAUSE = '<svg viewBox="0 0 10 10"><path d="M2 1h2v8H2zm4 0h2v8H6z" fill="#fff"/></svg>';
  pill.innerHTML = '<button class="play-btn" disabled>' + PLAY + '</button><div class="audio-bar"><div class="audio-bar-fill"></div></div><span class="audio-time">Синтез…</span>';
  group.appendChild(pill);

  try {
    const res = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    const btn = pill.querySelector('.play-btn');
    const fill = pill.querySelector('.audio-bar-fill');
    const time = pill.querySelector('.audio-time');

    btn.disabled = false;
    btn.innerHTML = PLAY;
    time.textContent = '0:00';

    btn.onclick = () => {
      if (activeAudio && activeAudio !== audio) { activeAudio.pause(); }
      if (audio.paused) { audio.play(); btn.innerHTML = PAUSE; activeAudio = audio; }
      else { audio.pause(); btn.innerHTML = PLAY; }
    };

    audio.ontimeupdate = () => {
      if (audio.duration) {
        fill.style.width = (audio.currentTime / audio.duration * 100) + '%';
        const s = Math.floor(audio.currentTime);
        time.textContent = '0:' + String(s).padStart(2, '0');
      }
    };
    audio.onended = () => { btn.innerHTML = PLAY; fill.style.width = '0%'; };

    audio.play();
    btn.innerHTML = PAUSE;
    activeAudio = audio;
  } catch (e) {
    pill.querySelector('.audio-time').textContent = 'Ошибка';
    console.error(e);
  }
}

function updateHistory(userText) {
  if (!currentTitle) {
    currentTitle = userText.length > 28 ? userText.slice(0, 28) + '…' : userText;
    const list = document.getElementById('historyList');
    const item = document.createElement('button');
    item.className = 'nav-item active';
    item.innerHTML = '<svg class="nav-icon" viewBox="0 0 16 16" fill="none"><path d="M2 3h12v8H9l-3 2v-2H2z" stroke="#e84020" stroke-width="1.2" stroke-linejoin="round"/></svg><span class="nav-label">' + currentTitle + '</span>';
    list.prepend(item);
  }
}

function newChat() {
  history = [];
  currentTitle = null;
  if (activeAudio) { activeAudio.pause(); activeAudio = null; }
  document.getElementById('messages').innerHTML = '';
  document.getElementById('inp').focus();
}

function askQuestion(q) {
  document.getElementById('inp').value = q;
  send();
}

async function send() {
  if (busy) return;
  const inp = document.getElementById('inp');
  const text = inp.value.trim();
  if (!text) return;

  busy = true;
  document.getElementById('sendBtn').disabled = true;
  inp.value = '';
  inp.style.height = 'auto';

  addMsg('user', text);
  history.push({ role: 'user', content: text });
  updateHistory(text);

  showThinking();
  status('Голос Пути Игры думает…');

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history })
    });
    if (!res.ok) throw new Error(await res.text());

    const data = await res.json();
    const reply = data.reply;
    history.push({ role: 'assistant', content: reply });

    hideThinking();
    const group = addMsg('ai', reply);
    status('');

    if (voiceOn) {
      status('Синтез голоса…');
      await playVoice(reply, group);
      status('');
    }
  } catch (e) {
    hideThinking();
    status('Ошибка: ' + e.message, 'error');
  } finally {
    busy = false;
    document.getElementById('sendBtn').disabled = false;
    inp.focus();
  }
}
</script>
</body>
</html>"""


class ChatRequest(BaseModel):
    messages: list


class TTSRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not ANTHROPIC_KEY:
        raise HTTPException(500, "ANTHROPIC_API_KEY не задан")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": SYSTEM_PROMPT,
                "messages": req.messages,
            },
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, response.text)

    data = response.json()
    return {"reply": data["content"][0]["text"]}


@app.post("/api/tts")
async def tts(req: TTSRequest):
    if not FISH_KEY or not FISH_VOICE_ID:
        raise HTTPException(500, "FISH_API_KEY или FISH_VOICE_ID не заданы")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.fish.audio/v1/tts",
            headers={
                "Authorization": f"Bearer {FISH_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "text": req.text,
                "reference_id": FISH_VOICE_ID,
                "format": "mp3",
                "latency": "balanced",
            },
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, "Fish Audio error")

    return StreamingResponse(
        iter([response.content]),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=voice.mp3"},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
