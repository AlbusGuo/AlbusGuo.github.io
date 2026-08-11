(()=>{
let activeNotebook='';let explorer=null;let transitionId=0;
const duration=150;const easing='ease-in-out';
const reduceMotion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
const roots=()=>Array.from(explorer?.querySelectorAll(':scope > .mathcraft-export-notebook-tree')??[]);
const indexView=()=>explorer?.querySelector('.mathcraft-export-notebook-index');
const detailView=()=>explorer?.querySelector('.mathcraft-export-notebook-detail');
function stopAnimations(){if(!explorer)return;for(const element of explorer.querySelectorAll('.mathcraft-export-notebook-view,.mathcraft-export-notebook-tree'))for(const animation of element.getAnimations())animation.cancel();}
function resetAnimationLayout(){explorer?.classList.remove('mathcraft-export-navigation-animating');}
async function slide(outgoing,incoming,forward){
	if(!explorer)return;const id=++transitionId;stopAnimations();for(const element of incoming)element.removeAttribute('hidden');
	if(reduceMotion()){for(const element of outgoing)element.setAttribute('hidden','');return;}
	explorer.classList.add('mathcraft-export-navigation-animating');
	const outFrames=forward?[{transform:'translateX(0)'},{transform:'translateX(-100%)'}]:[{transform:'translateX(0)'},{transform:'translateX(100%)'}];
	const inFrames=forward?[{transform:'translateX(100%)'},{transform:'translateX(0)'}]:[{transform:'translateX(-100%)'},{transform:'translateX(0)'}];
	const animations=[...outgoing.map(element=>element.animate(outFrames,{duration,easing,fill:'both'})),...incoming.map(element=>element.animate(inFrames,{duration,easing,fill:'both'}))];
	await Promise.allSettled(animations.map(animation=>animation.finished));if(id!==transitionId)return;
	for(const element of outgoing)element.setAttribute('hidden','');for(const animation of animations)animation.cancel();explorer.classList.remove('mathcraft-export-navigation-animating');
}
function setTitle(title){const element=detailView()?.querySelector('.mathcraft-export-notebook-title');if(element)element.textContent=title;}
function cleanPath(path){return path.replaceAll(String.fromCharCode(92),'/').split('/').filter(Boolean).join('/');}
function normalizePath(path){try{return cleanPath(decodeURIComponent(new URL(path,document.baseURI).pathname));}catch{return cleanPath(String(path??''));}}
function notebookForPath(path){const target=normalizePath(path);for(const root of roots()){for(const link of root.querySelectorAll('a.nav-file-title[href]'))if(normalizePath(link.href)===target)return root.dataset.notebookKey??'';}return '';}
function syncNotebook(path){const key=notebookForPath(path);if(key)showNotebook(key,activeNotebook!==key);}
function scrollMainTarget(target){const scroller=document.querySelector('#center-content>.obsidian-document');if(!(target instanceof Element)||!(scroller instanceof HTMLElement)){target?.scrollIntoView();return;}const targetRect=target.getBoundingClientRect();const scrollerRect=scroller.getBoundingClientRect();const top=scroller.scrollTop+targetRect.top-scrollerRect.top-24;scroller.scrollTo({top:Math.max(0,top),behavior:'auto'});}
function bindSiteNavigation(){const site=window.ObsidianSite;if(!site||typeof site.onDocumentLoad!=='function'||site.__mathcraftNotebookNavigationBound)return false;site.__mathcraftNotebookNavigationBound=true;const nativeScroll=typeof site.scrollTo==='function'?site.scrollTo.bind(site):null;site.scrollTo=target=>{if(target instanceof Element&&target.closest('#center-content'))scrollMainTarget(target);else nativeScroll?.(target);};let currentPath=document.querySelector('meta[name="pathname"]')?.getAttribute('content')??'';site.onDocumentLoad(documentView=>{const nextPath=documentView?.pathname??'';if(!nextPath||normalizePath(nextPath)===normalizePath(currentPath))return;currentPath=nextPath;syncNotebook(nextPath);});return true;}
function showIndex(animate=true){if(!explorer)return;const index=indexView();const detail=detailView();if(!index||!detail)return;const visibleRoots=roots().filter(root=>!root.hasAttribute('hidden'));activeNotebook='';if(animate&&!index.hasAttribute('hidden'))return;if(animate){void slide([detail,...visibleRoots],[index],false);}else{stopAnimations();resetAnimationLayout();index.removeAttribute('hidden');detail.setAttribute('hidden','');for(const root of roots())root.setAttribute('hidden','');}}
function showNotebook(key,animate=true){if(!explorer)return;const index=indexView();const detail=detailView();const root=roots().find(item=>item.dataset.notebookKey===key);if(!index||!detail||!root)return;activeNotebook=key;setTitle(root.dataset.notebookTitle??'');for(const item of roots())if(item!==root)item.setAttribute('hidden','');if(animate&&index.hasAttribute('hidden')){detail.removeAttribute('hidden');root.removeAttribute('hidden');return;}if(animate){void slide([index],[detail,root],true);}else{stopAnimations();resetAnimationLayout();index.setAttribute('hidden','');detail.removeAttribute('hidden');root.removeAttribute('hidden');}}
function showSearch(){if(!explorer)return;transitionId+=1;stopAnimations();resetAnimationLayout();indexView()?.setAttribute('hidden','');detailView()?.removeAttribute('hidden');for(const root of roots())root.removeAttribute('hidden');setTitle('搜索结果');}
function init(){const next=document.querySelector('#file-explorer');if(next&&next!==explorer){explorer=next;showIndex(false);}bindSiteNavigation();}
document.addEventListener('click',event=>{const target=event.target instanceof Element?event.target:null;const entry=target?.closest('.mathcraft-export-notebook-entry');if(entry){event.preventDefault();showNotebook(entry.dataset.notebookKey??'');return;}if(target?.closest('.mathcraft-export-notebook-back')){event.preventDefault();showIndex();}},true);
document.addEventListener('input',event=>{const input=event.target;if(!(input instanceof HTMLInputElement)||input.type!=='search')return;if(input.value.trim())showSearch();else if(activeNotebook)showNotebook(activeNotebook,false);else showIndex(false);});
new MutationObserver(init).observe(document.documentElement,{childList:true,subtree:true});init();
const siteTimer=setInterval(()=>{if(bindSiteNavigation())clearInterval(siteTimer);},50);setTimeout(()=>clearInterval(siteTimer),10000);
})();