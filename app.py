import os
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8766"))
DATA_FILE = "channels.json"
LOCK = threading.Lock()

DEFAULT_CHANNELS = [
    {
        "name": "NASA TV",
        "country": "États-Unis",
        "category": "Documentaires",
        "url": "https://plus.nasa.gov",
        "type": "website"
    },
    {
        "name": "France 24 Français",
        "country": "France",
        "category": "Actualités",
        "url": "https://www.youtube.com/@FRANCE24",
        "type": "website"
    },
    {
        "name": "Africanews",
        "country": "Afrique",
        "category": "Actualités",
        "url": "https://www.africanews.com/",
        "type": "website"
    }
]

def load_channels():
    if not os.path.exists(DATA_FILE):
        save_channels(DEFAULT_CHANNELS)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CHANNELS.copy()

def save_channels(channels):
    temp = DATA_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)
    os.replace(temp, DATA_FILE)

PAGE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JACKSON NGITUKA TV MONDE LIVE</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#eaf8ff;color:#12324b;font-family:Arial,sans-serif}
header{background:linear-gradient(120deg,#40c4f4,#0876ce);color:white;padding:24px 12px;text-align:center}
header h1{font-size:23px;margin:0}
header p{margin:8px 0 0}
nav{display:flex;gap:8px;overflow-x:auto;padding:12px;background:#d7f0ff}
nav button{white-space:nowrap;border:0;border-radius:20px;padding:12px 16px;background:white;color:#0876ce;font-weight:bold}
main{max-width:1000px;margin:auto;padding:12px}
.box{background:white;border-radius:17px;padding:15px;margin-bottom:15px;box-shadow:0 3px 14px #c4e3f3}
.player{background:#071522;border-radius:13px;overflow:hidden;min-height:230px}
video{width:100%;max-height:500px;display:block;background:#000}
.status{color:white;text-align:center;padding:18px}
input,select{width:100%;padding:13px;margin:7px 0;border:1px solid #b9dbea;border-radius:9px;font-size:15px}
.action{background:#078bd3;color:white;border:0;border-radius:9px;padding:12px 15px;font-weight:bold;margin:4px}
.channel{border:1px solid #d6eaf4;border-radius:12px;padding:13px;margin:10px 0}
.channel strong{display:block;margin-bottom:8px}
.small{font-size:12px;color:#668196}
.badge{background:#e1f5ff;color:#0876ce;border-radius:20px;padding:4px 8px;font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.tile{background:#e7f6ff;border-radius:12px;padding:17px;text-align:center;font-weight:bold;color:#0876ce}
footer{text-align:center;padding:20px;color:#668196}

body {
 background:#080808 !important;
 color:#fff !important;
}
header {
 background:linear-gradient(100deg,#160000,#850000,#160000) !important;
 padding:30px 14px !important;
}
header h1 {
 font-size:26px;
 letter-spacing:1px;
}
nav {
 background:#111 !important;
 justify-content:flex-start;
}
nav button {
 background:#292929 !important;
 color:white !important;
 border-radius:5px !important;
}
nav button:hover {
 background:#e50914 !important;
}
main {max-width:1200px}
.box {
 background:#151515 !important;
 color:white !important;
 box-shadow:none !important;
 border-radius:9px;
}
.player {
 border:1px solid #333;
 min-height:250px;
}
.channel {
 background:#222;
 color:white;
 border:1px solid #383838;
 border-radius:8px;
 display:inline-block;
 vertical-align:top;
 width:100%;
 transition:transform .2s;
}
.channel:hover {
 transform:scale(1.025);
 border-color:#e50914;
}
.channel strong {color:white}
.action {
 background:#e50914 !important;
 color:white;
 border-radius:5px;
}
input,select {
 background:#222;
 color:white;
 border-color:#444;
}
.small {color:#bbb}
footer {color:#aaa}
#channels {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
 gap:12px;
}
#countryList {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
}

</style>
</head>
<body>
<header>
<h1>📺 JACKSON NGITUKA TV MONDE LIVE</h1>
<p>Votre télévision internationale partout avec vous</p>
<span class="badge">● SERVICE EN LIGNE</span>
</header>

<nav>
<button onclick="showPage('home')">🏠 Accueil</button>
<button onclick="showPage('countries')">🌍 Pays</button>
<button onclick="showPage('favorites')">⭐ Favoris</button>
<button onclick="showPage('admin')">⚙ Administration</button>
</nav>

<main>
<section id="home">
<div class="box">
<h2>🔵 Lecteur TV HD</h2>
<div class="player">
<video id="video" controls playsinline></video>
<div class="status" id="status">Bienvenue sur JACKSON NGITUKA TV MONDE LIVE.<br>Choisissez une chaîne.</div>
</div>
<p class="small">La lecture dépend de la disponibilité et des droits du flux.</p>
</div>

<div class="box">
<h2>📡 Catalogue international</h2>
<input id="search" placeholder="Rechercher une chaîne ou un pays..." oninput="render()">
<select id="category" onchange="render()">
<option value="">Toutes les catégories</option>
<option>Actualités</option>
<option>Sport</option>
<option>Films</option>
<option>Séries</option>
<option>Musique</option>
<option>Enfants</option>
<option>Documentaires</option>
<option>Émissions</option>
</select>
<div id="channels"></div>
</div>
</section>

<section id="countries" style="display:none">
<div class="box">
<h2>🌍 Télévision par pays</h2>
<div class="grid" id="countryList"></div>
</div>
</section>

<section id="favorites" style="display:none">
<div class="box">
<h2>⭐ Mes favoris</h2>
<div id="favoriteList"></div>
</div>
</section>

<section id="admin" style="display:none">
<div class="box">
<h2>⚙ Administration des chaînes</h2>
<p class="small">Ajoute uniquement des flux dont tu possèdes les droits ou une autorisation de diffusion.</p>
<input id="adminName" placeholder="Nom de la chaîne">
<input id="adminCountry" placeholder="Pays">
<select id="adminCategory">
<option>Actualités</option><option>Sport</option><option>Films</option>
<option>Séries</option><option>Musique</option><option>Enfants</option>
<option>Documentaires</option><option>Émissions</option>
</select>
<input id="adminUrl" placeholder="URL HTTPS du flux .m3u8 ou .mp4">
<button class="action" onclick="addChannel()">Ajouter au catalogue</button>
<p id="adminMessage"></p>
</div>
</section>
</main>

<footer>JACKSON NGITUKA TV MONDE LIVE © 2026</footer>

<script src="https://cdn.jsdelivr.net/npm/hls.js@1"></script>
<script>
let channels=[];
let favorites=JSON.parse(localStorage.getItem("jack_favorites")||"[]");
let hls=null;
const video=document.getElementById("video");
const statusBox=document.getElementById("status");

async function load(){
 try{
  let r=await fetch("/api/channels");
  channels=await r.json();
  render();
  renderCountries();
  renderFavorites();
 }catch(e){
  document.getElementById("channels").textContent="Impossible de charger le catalogue.";
 }
}

function showPage(id){
 ["home","countries","favorites","admin"].forEach(x=>{
  document.getElementById(x).style.display=x===id?"block":"none";
 });
 if(id==="favorites")renderFavorites();
}

function play(url){
 if(!url.startsWith("https://")){
  statusBox.textContent="Adresse HTTPS obligatoire.";
  return;
 }
 if(hls){hls.destroy();hls=null;}
 video.pause();
 video.removeAttribute("src");
 video.load();
 statusBox.textContent="Chargement du flux...";
 if(url.includes(".m3u8")&&window.Hls&&Hls.isSupported()){
  hls=new Hls();
  hls.loadSource(url);
  hls.attachMedia(video);
  hls.on(Hls.Events.MANIFEST_PARSED,()=>{
   statusBox.textContent="";
   video.play().catch(()=>statusBox.textContent="Appuyez sur Lecture.");
  });
  hls.on(Hls.Events.ERROR,(e,d)=>{
   if(d.fatal)statusBox.textContent="Flux indisponible ou incompatible.";
  });
 }else{
  video.src=url;
  video.play().then(()=>statusBox.textContent="")
  .catch(()=>statusBox.textContent="Lecture impossible avec ce navigateur.");
 }
 window.scrollTo({top:0,behavior:"smooth"});
}

function card(c){
 let d=document.createElement("div");
 d.className="channel";
 let title=document.createElement("strong");
 title.textContent="📺 "+c.name;
 d.appendChild(title);
 let info=document.createElement("div");
 info.className="small";
 info.textContent=c.country+" • "+c.category;
 d.appendChild(info);
 let b=document.createElement("button");
 b.className="action";
 b.textContent="▶ Regarder";
 b.onclick=()=>play(c.url);
 d.appendChild(b);
 let f=document.createElement("button");
 f.className="action";
 f.textContent=favorites.includes(c.id)?"★ Favori":"☆ Ajouter";
 f.onclick=()=>{
  favorites.includes(c.id)?
   favorites=favorites.filter(x=>x!==c.id):favorites.push(c.id);
  localStorage.setItem("jack_favorites",JSON.stringify(favorites));
  render();
  renderFavorites();
 };
 d.appendChild(f);
 return d;
}

function render(){
 let q=document.getElementById("search").value.toLowerCase();
 let cat=document.getElementById("category").value;
 let box=document.getElementById("channels");
 box.innerHTML="";
 let result=channels.filter(c=>
  (c.name+" "+c.country).toLowerCase().includes(q)&&
  (!cat||c.category===cat)
 );
 result.forEach(c=>box.appendChild(card(c)));
 if(!result.length)box.textContent="Aucune chaîne dans cette catégorie.";
}

function renderCountries(){
 let countries=[...new Set(channels.map(c=>c.country))].sort();
 let box=document.getElementById("countryList");
 box.innerHTML="";
 countries.forEach(country=>{
  let b=document.createElement("button");
  b.className="tile";
  b.textContent="🌍 "+country;
  b.onclick=()=>{
   showPage("home");
   document.getElementById("search").value=country;
   render();
  };
  box.appendChild(b);
 });
}

function renderFavorites(){
 let box=document.getElementById("favoriteList");
 box.innerHTML="";
 let result=channels.filter(c=>favorites.includes(c.id));
 result.forEach(c=>box.appendChild(card(c)));
 if(!result.length)box.textContent="Aucun favori pour le moment.";
}

async function addChannel(){
 let data={
  name:document.getElementById("adminName").value.trim(),
  country:document.getElementById("adminCountry").value.trim(),
  category:document.getElementById("adminCategory").value,
  url:document.getElementById("adminUrl").value.trim()
 };
 if(!data.name||!data.country||!data.url){
  alert("Remplissez tous les champs.");
  return;
 }
 if(!data.url.startsWith("https://")){
  alert("Le flux doit utiliser HTTPS.");
  return;
 }
 try{
  let r=await fetch("/api/channels",{method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify(data)});
  let result=await r.json();
  if(!r.ok)throw Error(result.error||"Erreur");
  document.getElementById("adminMessage").textContent="Chaîne ajoutée.";
  ["adminName","adminCountry","adminUrl"].forEach(x=>document.getElementById(x).value="");
  await load();
 }catch(e){alert("Erreur : "+e.message);}
}
load();
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            raw = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif path == "/api/channels":
            with LOCK:
                self.send_json(load_channels())
        else:
            self.send_error(404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/channels":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 10000:
                self.send_json({"error": "Taille invalide"}, 400)
                return
            data = json.loads(self.rfile.read(size))
            name = str(data.get("name", "")).strip()
            country = str(data.get("country", "")).strip()
            category = str(data.get("category", "")).strip()
            url = str(data.get("url", "")).strip()
            if not name or not country or not url.startswith("https://"):
                self.send_json({"error": "Informations invalides"}, 400)
                return
            if not url.lower().endswith((".m3u8", ".mp4")):
                self.send_json({"error": "Utilise une URL directe .m3u8 ou .mp4"}, 400)
                return
            with LOCK:
                channels = load_channels()
                channels.append({
                    "id": str(len(channels) + 1) + "-" + str(abs(hash(url))),
                    "name": name,
                    "country": country,
                    "category": category,
                    "url": url
                })
                save_channels(channels)
            self.send_json({"success": True})
        except Exception:
            self.send_json({"error": "Données incorrectes"}, 400)

    def log_message(self, fmt, *args):
        print("[JACKSON TV]", fmt % args)

if __name__ == "__main__":
    print("======================================")
    print(" JACKSON NGITUKA TV MONDE LIVE")
    print("======================================")
    print("Adresse : http://127.0.0.1:" + str(PORT))
    print("Serveur prêt. CTRL+C pour arrêter.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Serveur arrêté.")
    finally:
        server.server_close()
