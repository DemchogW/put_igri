"""
Путь Игры — Backend сервер (всё в одном файле)
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
  *{margin:0;padding:0;box-sizing:border-box;}
  :root{--accent:#e84020;--dark:#111111;--border:#e5e5e5;--bg:#f7f7f7;--surface:#ffffff;}
  body{background:var(--bg);color:var(--dark);font-family:'Inter',sans-serif;font-weight:400;min-height:100vh;display:flex;flex-direction:column;align-items:center;}

  .app{width:100%;max-width:740px;min-height:100vh;background:var(--surface);display:flex;flex-direction:column;border-left:0.5px solid var(--border);border-right:0.5px solid var(--border);}

  /* TOP BAR */
  .top-bar{background:var(--dark);padding:28px 24px 22px;display:flex;flex-direction:column;align-items:center;gap:10px;}
  .logo-img{width:60px;height:60px;display:flex;align-items:center;justify-content:center;}
  .logo-img img{width:100%;height:100%;object-fit:contain;}
  .logo-text{font-size:16px;font-weight:500;color:#fff;letter-spacing:0.12em;text-transform:uppercase;}
  .logo-text span{color:var(--accent);}
  .tagline{font-size:11px;color:rgba(255,255,255,0.35);letter-spacing:0.08em;text-transform:uppercase;}

  /* MESSAGES */
  #messages{flex:1;min-height:300px;max-height:58vh;overflow-y:auto;padding:20px 24px 8px;scrollbar-width:thin;scrollbar-color:var(--border) transparent;}
  #messages::-webkit-scrollbar{width:3px;}
  #messages::-webkit-scrollbar-thumb{background:var(--border);}

  .msg-group{margin-bottom:18px;}
  .msg-row{display:flex;gap:10px;align-items:flex-start;}
  .msg-row.user{flex-direction:row-reverse;}

  .avatar{width:28px;height:28px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:500;margin-top:2px;overflow:hidden;}
  .avatar.ai{background:var(--dark);padding:5px;}
  .avatar.ai img{width:100%;height:100%;object-fit:contain;}
  .avatar.user{background:#f0f0f0;color:#888;letter-spacing:0.03em;}

  .bubble{max-width:80%;padding:10px 14px;font-size:14px;line-height:1.7;}
  .bubble.ai{background:#f5f5f5;color:var(--dark);border-radius:4px 14px 14px 14px;}
  .bubble.user{background:var(--dark);color:#fff;border-radius:14px 4px 14px 14px;}

  .quote-block{margin:6px 0 0 38px;padding:10px 14px;border-left:3px solid var(--accent);background:#fdf2f0;border-radius:0 8px 8px 0;font-size:13px;color:#666;font-style:italic;max-width:72%;}

  .audio-pill{display:flex;align-items:center;gap:8px;margin:6px 0 0 38px;background:#f5f5f5;border:0.5px solid var(--border);border-radius:999px;padding:6px 12px;max-width:220px;}
  .play-btn{width:22px;height:22px;background:var(--accent);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;border:none;cursor:pointer;transition:opacity 0.2s;}
  .play-btn:hover{opacity:0.85;}
  .play-btn:disabled{opacity:0.3;cursor:default;}
  .play-btn svg{width:8px;height:8px;fill:#fff;margin-left:1px;}
  .audio-bar{flex:1;height:2px;background:var(--border);border-radius:1px;cursor:pointer;}
  .audio-bar-fill{height:100%;background:var(--accent);border-radius:1px;width:0%;transition:width 0.1s;}
  .audio-label{font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#999;min-width:55px;}

  .divider{display:flex;align-items:center;gap:10px;margin:4px 0 16px;padding:0 24px;}
  .divider span{font-size:11px;color:#bbb;white-space:nowrap;}
  .divider::before,.divider::after{content:'';flex:1;height:0.5px;background:var(--border);}

  /* THINKING */
  .thinking{display:flex;gap:10px;padding:10px 0;align-items:flex-start;}
  .thinking-avatar{width:28px;height:28px;border-radius:50%;background:var(--dark);padding:5px;display:flex;align-items:center;justify-content:center;flex-shrink:0;overflow:hidden;}
  .thinking-avatar img{width:100%;height:100%;object-fit:contain;}
  .thinking-dots{display:flex;gap:5px;padding-top:8px;}
  .thinking-dots span{width:6px;height:6px;background:var(--accent);border-radius:50%;animation:pulse 1.4s infinite;opacity:0.3;}
  .thinking-dots span:nth-child(2){animation-delay:0.2s;}
  .thinking-dots span:nth-child(3){animation-delay:0.4s;}
  @keyframes pulse{0%,80%,100%{opacity:0.2;transform:scale(0.8);}40%{opacity:1;transform:scale(1);}}
  @keyframes fadeIn{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}
  .msg-group{animation:fadeIn 0.35s ease;}

  /* INPUT */
  .input-area{padding:12px 16px 20px;border-top:0.5px solid var(--border);background:var(--surface);}
  .voice-row{display:flex;align-items:center;justify-content:flex-end;gap:6px;margin-bottom:8px;}
  .voice-label{font-size:12px;color:#888;}
  .toggle-sw{width:32px;height:18px;background:#ddd;border-radius:9px;position:relative;transition:background 0.3s;cursor:pointer;}
  .toggle-sw::after{content:'';position:absolute;width:12px;height:12px;background:#fff;border-radius:50%;top:3px;left:3px;transition:all 0.3s;box-shadow:0 1px 2px rgba(0,0,0,0.2);}
  .voice-toggle.on .toggle-sw{background:var(--accent);}
  .voice-toggle.on .toggle-sw::after{left:17px;}
  .voice-toggle.on .voice-label{color:var(--accent);}
  .voice-toggle{display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none;}

  .input-box{display:flex;border:0.5px solid #ddd;border-radius:14px;background:#f5f5f5;overflow:hidden;align-items:flex-end;transition:border-color 0.2s;}
  .input-box:focus-within{border-color:var(--accent);}
  textarea{flex:1;border:none;background:none;padding:12px 16px;font-size:14px;font-family:'Inter',sans-serif;color:var(--dark);resize:none;outline:none;min-height:46px;max-height:140px;line-height:1.5;}
  textarea::placeholder{color:#bbb;}
  .send-btn{width:34px;height:34px;margin:6px;border-radius:10px;background:var(--dark);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background 0.2s;flex-shrink:0;}
  .send-btn:hover{background:var(--accent);}
  .send-btn:disabled{opacity:0.3;cursor:default;}
  .send-btn svg{width:14px;height:14px;}
  .hint{font-size:11px;color:#bbb;text-align:center;margin-top:8px;}

  #statusBar{font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#bbb;text-align:center;padding:6px 24px;min-height:26px;}
  #statusBar.error{color:var(--accent);}
  #statusBar.ok{color:#2e9e5b;}
</style>
</head>
<body>
<div class="app">
  <div class="top-bar">
    <div class="logo-img">
      <img src="https://static.tildacdn.com/tild3366-3263-4664-a332-643535653666/Logotip.svg" alt="Путь Игры">
    </div>
    <div class="logo-text">ПУТЬ <span>ИГРЫ</span></div>
    <div class="tagline">Голос философии · Зритель · Актёр · Роль</div>
  </div>

  <div id="messages"></div>
  <div id="statusBar"></div>

  <div class="input-area">
    <div class="voice-row">
      <label class="voice-toggle" id="voiceToggle" onclick="toggleVoice()">
        <div class="toggle-sw"></div>
        <span class="voice-label">Голос Демчога</span>
      </label>
    </div>
    <div class="input-box">
      <textarea id="inp" placeholder="Задай свой вопрос..." onkeydown="onKey(event)" oninput="grow(this)"></textarea>
      <button class="send-btn" id="sendBtn" onclick="send()">
        <svg viewBox="0 0 14 14" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"><path d="M7 1l6 6-6 6M1 7h12"/></svg>
      </button>
    </div>
    <p class="hint">Enter — отправить · Shift+Enter — новая строка</p>
  </div>
</div>
<script>
  let voiceOn=false,busy=false,history=[],activeAudio=null;
  const LOGO='https://static.tildacdn.com/tild3366-3263-4664-a332-643535653666/Logotip.svg';

  function toggleVoice(){voiceOn=!voiceOn;document.getElementById('voiceToggle').classList.toggle('on',voiceOn);}
  function status(msg,cls=''){const el=document.getElementById('statusBar');el.textContent=msg;el.className=cls;}
  function grow(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,140)+'px';}
  function onKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}

  function addMsg(role,text){
    const wrap=document.getElementById('messages');
    const group=document.createElement('div');group.className='msg-group';
    const avatarHtml=role==='user'?'<div class="avatar user">ТЫ</div>':'<div class="avatar ai"><img src="'+LOGO+'" alt="ПИ"></div>';
    const row=document.createElement('div');row.className='msg-row'+(role==='user'?' user':'');
    row.innerHTML=avatarHtml+'<div class="bubble '+role+'">'+text.replace(/\n/g,'<br>')+'</div>';
    group.appendChild(row);wrap.appendChild(group);wrap.scrollTop=wrap.scrollHeight;return group;
  }

  function thinking(){
    const wrap=document.getElementById('messages');
    const div=document.createElement('div');div.id='thinking';div.className='thinking';
    div.innerHTML='<div class="thinking-avatar"><img src="'+LOGO+'" alt="ПИ"></div><div class="thinking-dots"><span></span><span></span><span></span></div>';
    wrap.appendChild(div);wrap.scrollTop=wrap.scrollHeight;
  }
  function stopThinking(){const el=document.getElementById('thinking');if(el)el.remove();}

  async function playVoice(text,group){
    const pill=document.createElement('div');pill.className='audio-pill';
    const playIcon='<svg viewBox="0 0 10 10" fill="#fff"><path d="M2 1.5l7 3.5-7 3.5z"/></svg>';
    const pauseIcon='<svg viewBox="0 0 10 10" fill="#fff"><path d="M2 1h2v8H2zm4 0h2v8H6z"/></svg>';
    pill.innerHTML='<button class="play-btn" disabled>'+playIcon+'</button><div class="audio-bar"><div class="audio-bar-fill"></div></div><span class="audio-label">Синтез…</span>';
    group.appendChild(pill);
    try{
      const res=await fetch('/api/tts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
      if(!res.ok)throw new Error(await res.text());
      const blob=await res.blob();const url=URL.createObjectURL(blob);const audio=new Audio(url);
      const btn=pill.querySelector('.play-btn');const fill=pill.querySelector('.audio-bar-fill');const lbl=pill.querySelector('.audio-label');
      btn.disabled=false;lbl.textContent='Готово';
      btn.onclick=()=>{
        if(activeAudio&&activeAudio!==audio)activeAudio.pause();
        if(audio.paused){audio.play();btn.innerHTML=pauseIcon;activeAudio=audio;}
        else{audio.pause();btn.innerHTML=playIcon;}
      };
      audio.ontimeupdate=()=>{fill.style.width=(audio.currentTime/audio.duration*100)+'%';};
      audio.onended=()=>{btn.innerHTML=playIcon;fill.style.width='0%';};
      audio.play();btn.innerHTML=pauseIcon;activeAudio=audio;
    }catch(e){pill.querySelector('.audio-label').textContent='Ошибка';console.error(e);}
  }

  async function send(){
    if(busy)return;
    const inp=document.getElementById('inp');
    const text=inp.value.trim();if(!text)return;
    busy=true;document.getElementById('sendBtn').disabled=true;
    inp.value='';inp.style.height='auto';
    addMsg('user',text);history.push({role:'user',content:text});
    thinking();status('Голос Пути Игры думает…');
    try{
      const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:history})});
      if(!res.ok)throw new Error(await res.text());
      const data=await res.json();const reply=data.reply;
      history.push({role:'assistant',content:reply});
      stopThinking();const group=addMsg('ai',reply);status('');
      if(voiceOn){status('Синтез голоса…');await playVoice(reply,group);status('');}
    }catch(e){stopThinking();status('Ошибка: '+e.message,'error');}
    finally{busy=false;document.getElementById('sendBtn').disabled=false;inp.focus();}
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
