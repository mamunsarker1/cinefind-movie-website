const DATA_URL = "data/movies.json";
const FALLBACK = [
  {title:"Add your first listing",category:"Other",year:"",source_url:"https://southfreak.club/",description:"This is a starter card. Replace it with a verified movie page link in data/movies.json."},
  {title:"SouthFreak — Latest Movies",category:"Other",year:"",source_url:"https://southfreak.club/",description:"Open the source website to browse its latest listings."}
];
const grid=document.getElementById("movie-grid"), search=document.getElementById("search"), cat=document.getElementById("category-filter"), sort=document.getElementById("sort-filter"), statusEl=document.getElementById("status"), empty=document.getElementById("empty-state"), more=document.getElementById("load-more");
let movies=[], shown=10;
const palette=[["#253b57","#725a9e"],["#174d56","#bd855f"],["#3e2c5e","#bf718b"],["#263c43","#b58b54"],["#243a6b","#9d6ab1"],["#3e3449","#d58c68"],["#183c4a","#657cc1"]];
function safeUrl(value){try{const u=new URL(value);return ["http:","https:"].includes(u.protocol)?u.href:null}catch{return null}}
function categoryOf(m) {
  const title = String(m.title || "").toLowerCase();
  const original = String(m.category || "").toLowerCase();

  if (/bachelor point|natok|drama|episode|bangla drama/.test(title)) {
    return "Drama";
  }

  if (/web series|season \d|series|episode \d/.test(title)) {
    return "Web Series";
  }

  if (/movie|film|dual audio|1080p|720p|480p|web-dl|bluray|hindi|tamil|telugu/.test(title)) {
    return "Movie";
  }

  if (original && original !== "other") {
    return original.charAt(0).toUpperCase() + original.slice(1);
  }

  return "Other";
}
function posterMarkup(m,i){const p=palette[i%palette.length];const letter=(m.title||"?").trim().charAt(0).toUpperCase();return `<div class="movie-poster" style="background:linear-gradient(145deg,${p[0]},${p[1]})"><span class="type-pill">${escapeHtml(categoryOf(m).toUpperCase())}</span><span class="year-pill">${escapeHtml(m.year||"NEW")}</span><span class="poster-letter">${escapeHtml(letter)}</span></div>`}
function escapeHtml(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function render(){
 const q=search.value.trim().toLowerCase();let list=movies.filter(m=>(cat.value==="all"||categoryOf(m).toLowerCase()===cat.value.toLowerCase())&&(`${m.title||""} ${m.category||""} ${m.year||""} ${m.description||""}`).toLowerCase().includes(q));
 if(sort.value==="az")list.sort((a,b)=>(a.title||"").localeCompare(b.title||""));
 else list.sort((a,b)=>String(b.published_at||"").localeCompare(String(a.published_at||"")));
 statusEl.textContent=`Showing ${Math.min(shown,list.length)} of ${list.length} listing${list.length===1?"":"s"}.`;
 empty.hidden=list.length!==0;grid.innerHTML=list.slice(0,shown).map((m,i)=>{const url=safeUrl(m.source_url)||"https://southfreak.club/";return `<article class="movie-card">${posterMarkup(m,i)}<div class="movie-info"><h3 class="movie-title">${escapeHtml(m.title||"Untitled listing")}</h3><div class="movie-meta"><span>${escapeHtml(categoryOf(m))}</span><span>${escapeHtml(m.year||"")}</span></div><a class="watch-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer nofollow">Visit source <span>↗</span></a></div></article>`}).join("");
 more.hidden=list.length<=shown;
}
function setCategories(){const values=[...new Set(movies.map(categoryOf).filter(Boolean))].sort();cat.innerHTML='<option value="all">All categories</option>'+values.map(v=>`<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join("")}
async function init(){document.getElementById("year").textContent=new Date().getFullYear();try{const r=await fetch(DATA_URL,{cache:"no-store"});if(!r.ok)throw Error("not found");const data=await r.json();movies=Array.isArray(data.movies)?data.movies:[];document.getElementById("updated-date").textContent=data.updated_at?new Date(data.updated_at).toLocaleDateString():"—";}catch(e){movies=FALLBACK;document.getElementById("updated-date").textContent="Starter";statusEl.textContent="Starter listings shown. Upload data/movies.json to add verified titles and source links."}document.getElementById("total-count").textContent=movies.length;setCategories();render()}
search.addEventListener("input",()=>{shown=10;render()});cat.addEventListener("change",()=>{shown=10;render()});sort.addEventListener("change",render);more.addEventListener("click",()=>{shown+=10;render()});
document.querySelectorAll(".category-grid button").forEach(b=>b.addEventListener("click",()=>{const wanted=b.dataset.cat;const match=[...cat.options].find(o=>o.value.toLowerCase()===wanted.toLowerCase());cat.value=match?match.value:"all";search.value="";shown=10;document.getElementById("latest").scrollIntoView({behavior:"smooth"});render()}));
init();
