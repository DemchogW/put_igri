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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Raleway:wght@200;300;400&display=swap" rel="stylesheet">
<style>
  :root{--bg:#0a0a0f;--surface:#111118;--border:rgba(180,150,100,0.15);--gold:#c9a96e;--gold-dim:rgba(201,169,110,0.4);--gold-glow:rgba(201,169,110,0.08);--text:#e8e0d0;--text-dim:rgba(232,224,208,0.45);}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--bg);color:var(--text);font-family:'Raleway',sans-serif;font-weight:300;min-height:100vh;display:flex;flex-direction:column;align-items:center;overflow-x:hidden;}
  body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 60% 40% at 20% 50%,rgba(201,169,110,0.04) 0%,transparent 70%),radial-gradient(ellipse 40% 60% at 80% 30%,rgba(120,80,180,0.03) 0%,transparent 70%);pointer-events:none;z-index:0;}
  header{width:100%;max-width:760px;padding:48px 32px 32px;text-align:center;position:relative;z-index:1;}
  .logo-line{display:flex;align-items:center;justify-content:center;gap:20px;margin-bottom:12px;}
  .logo-line::before{content:'';flex:1;height:1px;background:linear-gradient(to right,transparent,var(--gold-dim));}
  .logo-line::after{content:'';flex:1;height:1px;background:linear-gradient(to left,transparent,var(--gold-dim));}
  h1{font-family:'Cormorant Garamond',serif;font-weight:300;font-size:clamp(28px,5vw,42px);letter-spacing:0.15em;margin-bottom:8px;}
  h1 span{color:var(--gold);font-style:italic;}
  .subtitle{font-size:11px;letter-spacing:0.35em;text-transform:uppercase;color:var(--text-dim);}
  .chat-wrap{width:100%;max-width:760px;padding:0 32px;flex:1;display:flex;flex-direction:column;position:relative;z-index:1;}
  #messages{flex:1;min-height:300px;max-height:58vh;overflow-y:auto;padding:8px 0;scrollbar-width:thin;scrollbar-color:var(--border) transparent;}
  #messages::-webkit-scrollbar{width:3px;}
  #messages::-webkit-scrollbar-thumb{background:var(--border);}
  .msg{display:flex;gap:16px;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.03);animation:fadeIn 0.4s ease;}
  @keyframes fadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
  .msg-avatar{width:28px;height:28px;flex-shrink:0;display:flex;align-items:center;justify-content:center;margin-top:2px;}
  .msg.user .msg-avatar{color:var(--text-dim);border:1px solid var(--border);border-radius:50%;font-size:10px;letter-spacing:0.05em;}
  .msg.ai .msg-avatar{color:var(--gold);font-size:16px;}
  .msg-content{flex:1;line-height:1.85;}
  .msg.user .msg-content{color:var(--text-dim);font-size:14px;}
  .msg.ai .msg-content{color:var(--text);font-family:'Cormorant Garamond',serif;font-size:17px;font-weight:300;}
  .audio-row{display:flex;align-items:center;gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.04);}
  .play-btn{width:32px;height:32px;border-radius:50%;border:1px solid var(--gold-dim);background:var(--gold-glow);color:var(--gold);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.2s;font-size:12px;}
  .play-btn:hover{background:rgba(201,169,110,0.15);}
  .play-btn:disabled{opacity:0.35;cursor:default;}
  .audio-bar{flex:1;height:2px;background:var(--border);border-radius:1px;}
  .audio-bar-fill{height:100%;background:var(--gold);border-radius:1px;width:0%;transition:width 0.1s;}
  .audio-label{font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:var(--text-dim);min-width:55px;}
  .thinking{display:flex;gap:16px;padding:20px 0;align-items:flex-start;}
  .thinking-dots{display:flex;gap:5px;padding-top:8px;}
  .thinking-dots span{width:5px;height:5px;background:var(--gold-dim);border-radius:50%;animation:pulse 1.4s infinite;}
  .thinking-dots span:nth-child(2){animation-delay:0.2s;}
  .thinking-dots span:nth-child(3){animation-delay:0.4s;}
  @keyframes pulse{0%,80%,100%{opacity:0.2;transform:scale(0.8);}40%{opacity:1;transform:scale(1);}}
  .input-area{padding:20px 0 40px;position:relative;}
  .voice-toggle{display:flex;align-items:center;gap:8px;position:absolute;right:0;top:20px;font-size:11px;letter-spacing:0.15em;text-transform:uppercase;color:var(--text-dim);cursor:pointer;user-select:none;transition:color 0.2s;}
  .toggle-sw{width:32px;height:18px;background:var(--border);border-radius:9px;position:relative;transition:background 0.3s;}
  .toggle-sw::after{content:'';position:absolute;width:12px;height:12px;background:var(--text-dim);border-radius:50%;top:3px;left:3px;transition:all 0.3s;}
  .voice-toggle.on{color:var(--gold);}
  .voice-toggle.on .toggle-sw{background:var(--gold-dim);}
  .voice-toggle.on .toggle-sw::after{left:17px;background:var(--gold);}
  .input-wrap{display:flex;border:1px solid var(--border);background:var(--surface);transition:border-color 0.3s;}
  .input-wrap:focus-within{border-color:var(--gold-dim);}
  textarea{flex:1;background:none;border:none;color:var(--text);font-family:'Raleway',sans-serif;font-size:14px;font-weight:300;padding:16px 20px;outline:none;resize:none;min-height:54px;max-height:140px;line-height:1.6;}
  textarea::placeholder{color:var(--text-dim);}
  .send-btn{width:54px;background:none;border:none;border-left:1px solid var(--border);color:var(--gold-dim);cursor:pointer;font-size:18px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;}
  .send-btn:hover{color:var(--gold);background:var(--gold-glow);}
  .send-btn:disabled{opacity:0.3;cursor:default;}
  .hint{font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:var(--text-dim);text-align:center;margin-top:12px;opacity:0.6;}
  #statusBar{font-size:11px;letter-spacing:0.15em;text-transform:uppercase;color:var(--text-dim);text-align:center;padding:6px;min-height:26px;}
  #statusBar.error{color:#c06060;}
  #statusBar.ok{color:var(--gold);}
</style>
</head>
<body>
<header>
  <div class="logo-line"><span style="color:var(--gold);font-size:20px">◉</span></div>
  <p class="subtitle">Философия присутствия</p>
  <h1>Путь <span>Игры</span></h1>
</header>
<div class="chat-wrap">
  <div id="messages"></div>
  <div id="statusBar"></div>
  <div class="input-area">
    <label class="voice-toggle" id="voiceToggle" onclick="toggleVoice()">
      <div class="toggle-sw"></div>Голос
    </label>
    <div class="input-wrap">
      <textarea id="inp" placeholder="Задай свой вопрос..." onkeydown="onKey(event)" oninput="grow(this)"></textarea>
      <button class="send-btn" id="sendBtn" onclick="send()">↑</button>
    </div>
    <p class="hint">Enter — отправить · Shift+Enter — новая строка</p>
  </div>
</div>
<script>
  let voiceOn=false,busy=false,history=[],activeAudio=null;
  function toggleVoice(){voiceOn=!voiceOn;document.getElementById('voiceToggle').classList.toggle('on',voiceOn);}
  function status(msg,cls=''){const el=document.getElementById('statusBar');el.textContent=msg;el.className=cls;}
  function grow(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,140)+'px';}
  function onKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}
  function addMsg(role,text){
    const wrap=document.getElementById('messages');
    const div=document.createElement('div');
    div.className='msg '+role;
    div.innerHTML='<div class="msg-avatar">'+(role==='user'?'Я':'◉')+'</div><div class="msg-content">'+text.replace(/\\n/g,'<br>')+'</div>';
    wrap.appendChild(div);wrap.scrollTop=wrap.scrollHeight;return div;
  }
  function thinking(){
    const wrap=document.getElementById('messages');
    const div=document.createElement('div');
    div.id='thinking';div.className='thinking';
    div.innerHTML='<div class="msg-avatar" style="color:var(--gold);font-size:16px">◉</div><div class="thinking-dots"><span></span><span></span><span></span></div>';
    wrap.appendChild(div);wrap.scrollTop=wrap.scrollHeight;
  }
  function stopThinking(){const el=document.getElementById('thinking');if(el)el.remove();}
  async function playVoice(text,msgDiv){
    const content=msgDiv.querySelector('.msg-content');
    const row=document.createElement('div');
    row.className='audio-row';
    row.innerHTML='<button class="play-btn" disabled>⟳</button><div class="audio-bar"><div class="audio-bar-fill"></div></div><span class="audio-label">Синтез…</span>';
    content.appendChild(row);
    try{
      const res=await fetch('/api/tts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
      if(!res.ok)throw new Error(await res.text());
      const blob=await res.blob();const url=URL.createObjectURL(blob);const audio=new Audio(url);
      const btn=row.querySelector('.play-btn');const fill=row.querySelector('.audio-bar-fill');const lbl=row.querySelector('.audio-label');
      btn.disabled=false;btn.textContent='▶';lbl.textContent='Готово';
      btn.onclick=()=>{
        if(activeAudio&&activeAudio!==audio)activeAudio.pause();
        if(audio.paused){audio.play();btn.textContent='⏸';activeAudio=audio;}
        else{audio.pause();btn.textContent='▶';}
      };
      audio.ontimeupdate=()=>{fill.style.width=(audio.currentTime/audio.duration*100)+'%';};
      audio.onended=()=>{btn.textContent='▶';fill.style.width='0%';};
      audio.play();btn.textContent='⏸';activeAudio=audio;
    }catch(e){row.querySelector('.audio-label').textContent='Ошибка';console.error(e);}
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
      stopThinking();const msgDiv=addMsg('ai',reply);status('');
      if(voiceOn){status('Синтез голоса…');await playVoice(reply,msgDiv);status('');}
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
