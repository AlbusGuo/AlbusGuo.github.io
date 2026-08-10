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
function showIndex(animate=true){if(!explorer)return;const index=indexView();const detail=detailView();if(!index||!detail)return;const visibleRoots=roots().filter(root=>!root.hasAttribute('hidden'));activeNotebook='';if(animate&&!index.hasAttribute('hidden'))return;if(animate){void slide([detail,...visibleRoots],[index],false);}else{stopAnimations();resetAnimationLayout();index.removeAttribute('hidden');detail.setAttribute('hidden','');for(const root of roots())root.setAttribute('hidden','');}}
function showNotebook(key,animate=true){if(!explorer)return;const index=indexView();const detail=detailView();const root=roots().find(item=>item.dataset.notebookKey===key);if(!index||!detail||!root)return;activeNotebook=key;setTitle(root.dataset.notebookTitle??'');for(const item of roots())if(item!==root)item.setAttribute('hidden','');if(animate&&index.hasAttribute('hidden')){detail.removeAttribute('hidden');root.removeAttribute('hidden');return;}if(animate){void slide([index],[detail,root],true);}else{stopAnimations();resetAnimationLayout();index.setAttribute('hidden','');detail.removeAttribute('hidden');root.removeAttribute('hidden');}}
function showSearch(){if(!explorer)return;transitionId+=1;stopAnimations();resetAnimationLayout();indexView()?.setAttribute('hidden','');detailView()?.removeAttribute('hidden');for(const root of roots())root.removeAttribute('hidden');setTitle('搜索结果');}
function init(){const next=document.querySelector('#file-explorer');if(!next||next===explorer)return;explorer=next;showIndex(false);}
document.addEventListener('click',event=>{const target=event.target instanceof Element?event.target:null;const entry=target?.closest('.mathcraft-export-notebook-entry');if(entry){event.preventDefault();showNotebook(entry.dataset.notebookKey??'');return;}if(target?.closest('.mathcraft-export-notebook-back')){event.preventDefault();showIndex();}},true);
document.addEventListener('input',event=>{const input=event.target;if(!(input instanceof HTMLInputElement)||input.type!=='search')return;if(input.value.trim())showSearch();else if(activeNotebook)showNotebook(activeNotebook,false);else showIndex(false);});
new MutationObserver(init).observe(document.documentElement,{childList:true,subtree:true});init();
})();