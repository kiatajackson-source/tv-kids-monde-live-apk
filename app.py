import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8766"))

PAGE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TV KIDS MONDE LIVE</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#eefaff;color:#18344b;
 font-family:Arial,sans-serif
}
header{
 background:linear-gradient(120deg,#42b9ed,#0879d1);
 color:white;padding:22px 15px;text-align:center
}
header h1{margin:0;font-size:25px}
header p{margin:8px 0 0}
nav{
 display:flex;gap:8px;justify-content:center;
 flex-wrap:wrap;padding:14px
}
nav button{
 border:0;border-radius:20px;padding:11px 17px;
 background:white;color:#0879d1;font-weight:bold
}
main{max-width:900px;margin:auto;padding:12px}
.box{
 background:white;border-radius:17px;padding:16px;
 margin-bottom:16px;box-shadow:0 3px 14px #b9dced
}
.player{
 background:#071522;border-radius:13px;
 overflow:hidden;min-height:220px
}
video{width:100%;max-height:460px;display:block}
.status{text-align:center;color:#dceefa;padding:12px}
input,select{
 width:100%;padding:13px;margin:7px 0;
 border:1px solid #b8d8e8;border-radius:9px;
 font-size:15px
}
button.action{
 background:#078bd3;color:white;border:0;
 border-radius:9px;padding:12px 16px;
 font-weight:bold;margin:5px 3px
}
.channel{
 border:1px solid #d6eaf4;border-radius:11px;
 padding:12px;margin:9px 0
}
.channel strong{display:block;margin-bottom:8px}
.small{font-size:12px;color:#668196}
footer{text-align:center;padding:20px;color:#668196}
</style>
</head>
<body>
<header>
 <h1>📺 TV KIDS MONDE LIVE</h1>
 <p>Le monde des enfants, partout avec vous !</p>
</header>

<nav>
 <button onclick="filterChannels('Toutes')">Accueil</button>
 <button onclick="filterChannels('Dessins animés')">Dessins animés</button>
 <button onclick="filterChannels('Éducation')">Éducation</button>
 <button onclick="filterChannels('Musique')">Musique</button>
 <button onclick="filterChannels('Favoris')">Favoris ⭐</button>
</nav>

<main>
 <section class="box">
  <h2>🔵 Lecteur vidéo HD</h2>
  <div class="player">
   <video id="video" controls playsinline></video>
   <div class="status" id="status">
    Bienvenue sur TV KIDS MONDE LIVE.
    <br>Choisis une chaîne pour commencer.
   </div>
  </div>
  <p class="small">La qualité dépend du flux vidéo et de la connexion Internet.</p>
 </section>

 <section class="box">
  <h2>🌍 Ajouter une chaîne autorisée</h2>
  <input id="channelName" placeholder="Nom de la chaîne">
  <select id="category">
   <option>Dessins animés</option>
   <option>Éducation</option>
   <option>Musique</option>
  </select>
  <input id="streamUrl" placeholder="Adresse du flux HTTPS (.m3u8 ou .mp4)">
  <button class="action" onclick="addChannel()">Ajouter la chaîne</button>
  <p class="small">Ajoute uniquement des flux dont tu possèdes les droits de diffusion ou une autorisation.</p>
 </section>

 <section class="box">
  <h2>📡 Mes chaînes</h2>
  <div id="channels"></div>
 </section>
</main>

<footer>TV KIDS MONDE LIVE • Projet en développement</footer>

<script src="https://cdn.jsdelivr.net/npm/hls.js@1"></script>
<script>
const video=document.getElementById("video");
const statusBox=document.getElementById("status");
const list=document.getElementById("channels");
let hls=null;
let channels=JSON.parse(localStorage.getItem("kids_channels")||"[]");
let currentFilter="Toutes";

function save(){
 localStorage.setItem("kids_channels",JSON.stringify(channels));
}

function playStream(url){
 if(!url.startsWith("https://")){
  statusBox.textContent="Le flux doit commencer par https://";
  return;
 }
 if(hls){hls.destroy();hls=null;}
 video.pause();
 video.removeAttribute("src");
 video.load();

 let isHLS=false;
 try{
  isHLS=new URL(url).pathname.toLowerCase().endsWith(".m3u8");
 }catch(e){}

 statusBox.textContent="Chargement de la chaîne...";
 if(isHLS && window.Hls && Hls.isSupported()){
  hls=new Hls();
  hls.loadSource(url);
  hls.attachMedia(video);
  hls.on(Hls.Events.MANIFEST_PARSED,()=>{
   statusBox.textContent="";
   video.play().catch(()=>{statusBox.textContent="Appuie sur Lecture."});
  });
  hls.on(Hls.Events.ERROR,(event,data)=>{
   if(data.fatal)statusBox.textContent="Flux indisponible ou incompatible.";
  });
 }else{
  video.src=url;
  video.play().then(()=>{
   statusBox.textContent="";
  }).catch(()=>{
   statusBox.textContent="Lecture impossible. Vérifie le flux.";
  });
 }
}

function addChannel(){
 const name=document.getElementById("channelName").value.trim();
 const category=document.getElementById("category").value;
 const url=document.getElementById("streamUrl").value.trim();

 if(!name || !url){
  alert("Entre le nom et l'adresse du flux.");
  return;
 }
 if(!url.startsWith("https://")){
  alert("L'adresse doit commencer par https://");
  return;
 }
 channels.push({
  id:Date.now().toString(),
  name:name,
  category:category,
  url:url,
  favorite:false
 });
 save();
 render();
 document.getElementById("channelName").value="";
 document.getElementById("streamUrl").value="";
 alert("Chaîne ajoutée !");
}

function filterChannels(filter){
 currentFilter=filter;
 render();
}

function render(){
 list.innerHTML="";
 let visible=channels.filter(c=>{
  if(currentFilter==="Favoris")return c.favorite;
  if(currentFilter==="Toutes")return true;
  return c.category===currentFilter;
 });

 if(visible.length===0){
  list.textContent="Aucune chaîne ajoutée pour le moment.";
  return;
 }

 visible.forEach(c=>{
  const card=document.createElement("div");
  card.className="channel";

  const title=document.createElement("strong");
  title.textContent="📺 "+c.name+" — "+c.category;
  card.appendChild(title);

  const play=document.createElement("button");
  play.className="action";
  play.textContent="▶ Lire";
  play.onclick=()=>playStream(c.url);
  card.appendChild(play);

  const fav=document.createElement("button");
  fav.className="action";
  fav.textContent=c.favorite?"Retirer des favoris":"⭐ Favori";
  fav.onclick=()=>{
   c.favorite=!c.favorite;
   save();render();
  };
  card.appendChild(fav);

  const remove=document.createElement("button");
  remove.className="action";
  remove.textContent="Supprimer";
  remove.onclick=()=>{
   channels=channels.filter(x=>x.id!==c.id);
   save();render();
  };
  card.appendChild(remove);

  list.appendChild(card);
 });
}

render();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        data = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        print("[TV KIDS]", format % args)

print("====================================")
print("       TV KIDS MONDE LIVE")
print("====================================")
print("Serveur : http://127.0.0.1:8766")
print("Pour arrêter : CTRL + C")

server = ThreadingHTTPServer((HOST, PORT), Handler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nTV KIDS MONDE LIVE arrêté.")
finally:
    server.server_close()
