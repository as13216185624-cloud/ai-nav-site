#!/usr/bin/env python3
"""Update index.html: expand showcase to 36 items, add video type, pagination, working tabs"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ========== 1. New showcaseData (36 items) ==========
new_showcase_data = '''const showcaseData = [
{id:1,title:"无支祁",author:"暗黑神话系列",tool:"Midjourney V8.1",type:"image",date:"2026-06-10",prompt:"Chinese mythological monkey king with golden crown embedded with emeralds, dark background, dramatic lighting, ultra detailed, 8K, cinematic, traditional Chinese mythology meets dark fantasy art",tags:["国风","暗黑","神话"],likes:2847,image:"showcase/01-wuzhiqi.jpg"},
{id:2,title:"赤色章刃",author:"武侠概念",tool:"Stable Diffusion XL",type:"image",date:"2026-06-10",prompt:"Martial arts warrior in red and black armor, dramatic action pose, neon lights, cyberpunk ancient China fusion, cinematic lighting, ultra detailed character design, epic composition",tags:["武侠","赛博朋克","国风"],likes:1923,image:"showcase/02-chisezhangren.jpg"},
{id:3,title:"子时临安",author:"古风场景",tool:"Midjourney V8.1",type:"image",date:"2026-06-11",prompt:"Ancient Chinese city at midnight, lantern lights reflecting on water canals, misty atmosphere, traditional Song dynasty architecture, golden warm lights, ultra wide cinematic shot",tags:["古风","场景","夜景"],likes:3156,image:"showcase/03-zishilinan.jpg"},
{id:4,title:"楚云传",author:"仙侠概念",tool:"Stable Diffusion + LoRA",type:"image",date:"2026-06-11",prompt:"Xianxia floating palace above clouds, golden dragons circling, ethereal atmosphere, jade and gold color scheme, cinematic wide composition, 8K, traditional Chinese fantasy art",tags:["仙侠","幻想","场景"],likes:2689,image:"showcase/04-chuyunzhuan.jpg"},
{id:5,title:"HACKTHON ACTION",author:"环屿AI LAB",tool:"Kling AI + Runway",type:"video",date:"2026-06-12",prompt:"Sci-fi action scene, female character in dark techwear jacket sprinting through neon-lit cyberpunk city, mechanical insects with red glowing eyes in pursuit, heavy rain, cinematic, 4K",tags:["科幻","动作","视频"],likes:4521,image:"showcase/05-hackthon.jpg"},
{id:6,title:"雨夜东京",author:"赛博城市",tool:"Midjourney V8.1",type:"image",date:"2026-06-12",prompt:"Tokyo rainy night, vibrant neon reflections on wet asphalt streets, cyberpunk aesthetic, cinematic lighting, shallow depth of field, photorealistic, 8K, Blade Runner vibes",tags:["赛博朋克","城市","夜景"],likes:3847,image:"showcase/06-yuyedongjing.jpg"},
{id:7,title:"极光森林",author:"自然幻想",tool:"Stable Diffusion XL",type:"image",date:"2026-06-13",prompt:"Enchanted forest with dancing aurora borealis, giant glowing mushrooms, magical fairy lights, fantasy art, volumetric god rays, ultra detailed digital illustration, ethereal atmosphere",tags:["幻想","自然","治愈"],likes:2156,image:"showcase/07-jiguangsenlin.jpg"},
{id:8,title:"未来机甲",author:"硬核科幻",tool:"Midjourney V8.1 + PS",type:"image",date:"2026-06-13",prompt:"Futuristic mecha warrior, polished chrome and carbon fiber armor panels, holographic HUD overlay, war-torn battlefield background, ultra realistic, 8K, AAA game concept art quality",tags:["科幻","机甲","概念设计"],likes:5230,image:"showcase/08-weilaijijia.jpg"},
{id:9,title:"敦煌飞天",author:"国风复兴",tool:"Stable Diffusion + ControlNet",type:"image",date:"2026-06-14",prompt:"Dunhuang flying celestial apsara, traditional Chinese mural painting style, flowing silk ribbons in wind, gold and turquoise mineral pigment colors, ancient Buddhist art aesthetic, 8K",tags:["国风","敦煌","传统"],likes:6721,image:"showcase/09-dunhuangfeitian.jpg"},
{id:10,title:"蒸汽朋克猫",author:"奇幻生物",tool:"Midjourney V8.1",type:"image",date:"2026-06-14",prompt:"Steampunk cat with polished brass goggles and intricate mechanical clockwork wings, Victorian era industrial background, warm golden hour lighting, detailed fur texture, fantasy illustration",tags:["蒸汽朋克","动物","奇幻"],likes:1987,image:"showcase/10-zhengqipengkemao.jpg"},
{id:11,title:"深海龙宫",author:"东方幻想",tool:"Midjourney V8.1",type:"image",date:"2026-06-15",prompt:"Underwater Chinese dragon palace, crystal and jade architecture, bioluminescent deep sea corals, ancient Chinese mythology, ethereal volumetric lighting, 8K, fantasy concept art",tags:["东方","幻想","海底"],likes:3456,image:"showcase/11-shenhailonggong.jpg"},
{id:12,title:"赛博观音",author:"文化融合",tool:"Stable Diffusion XL",type:"image",date:"2026-06-15",prompt:"Cyberpunk Guanyin bodhisattva, holographic lotus throne, neon halo ring, futuristic temple sanctuary, chrome and rose gold aesthetic, ultra detailed digital concept art, spiritual meets technological",tags:["赛博朋克","佛教","融合"],likes:8921,image:"showcase/12-saiboguanyin.jpg"},
{id:13,title:"山海经·穷奇",author:"国风神话",tool:"Midjourney V8.1",type:"image",date:"2026-06-16",prompt:"Ancient Chinese mythical beast Qiongqi from Shan Hai Jing, tiger body with wings, fierce expression, traditional ink wash painting style meets dark fantasy, dramatic composition",tags:["国风","神话","山海经"],likes:5120,image:"showcase/01-wuzhiqi.jpg"},
{id:14,title:"赛博长安",author:"古今融合",tool:"Stable Diffusion XL",type:"image",date:"2026-06-16",prompt:"Tang Dynasty Chang'an transformed into cyberpunk metropolis, neon signs on ancient architecture, flying cars between pagodas, rain-slicked stone streets reflecting holograms, 8K",tags:["赛博朋克","古风","城市"],likes:3980,image:"showcase/03-zishilinan.jpg"},
{id:15,title:"银河战舰·启航",author:"硬核科幻",tool:"Midjourney V8.1 + PS",type:"image",date:"2026-06-16",prompt:"Massive interstellar battleship emerging from nebula, thousands of lights, epic scale, cinematic wide shot, photorealistic space render, 8K concept art",tags:["科幻","太空","战舰"],likes:6340,image:"showcase/08-weilaijijia.jpg"},
{id:16,title:"樱花武士",author:"日式美学",tool:"Stable Diffusion XL",type:"image",date:"2026-06-16",prompt:"Samurai warrior standing under falling cherry blossoms, traditional armor with modern cybernetic enhancements, misty bamboo forest, golden hour light, ultra detailed",tags:["日式","武士","赛博"],likes:2890,image:"showcase/02-chisezhangren.jpg"},
{id:17,title:"龙与地下城",author:"西幻概念",tool:"Midjourney V8.1",type:"image",date:"2026-06-16",prompt:"Epic dragon battle above medieval castle, knight in shining armor, fire and magic, dramatic sky, fantasy book cover quality, ultra detailed illustration",tags:["奇幻","西幻","龙"],likes:4560,image:"showcase/04-chuyunzhuan.jpg"},
{id:18,title:"机械天使",author:"赛博宗教",tool:"Stable Diffusion + ControlNet",type:"image",date:"2026-06-16",prompt:"Cybernetic angel with chrome wings and holographic halo, standing in ruined cathedral, beams of light through stained glass, divine meets machine aesthetic",tags:["赛博朋克","天使","宗教"],likes:7210,image:"showcase/12-saiboguanyin.jpg"},
{id:19,title:"水墨江山",author:"国风水墨",tool:"Stable Diffusion + LoRA",type:"image",date:"2026-06-16",prompt:"Traditional Chinese ink wash landscape painting, misty mountains, solitary fisherman on lake, pine trees on cliffs, red seal stamp, minimalist zen aesthetic",tags:["国风","水墨","山水"],likes:3780,image:"showcase/09-dunhuangfeitian.jpg"},
{id:20,title:"废土求生",author:"末世科幻",tool:"Midjourney V8.1",type:"image",date:"2026-06-16",prompt:"Post-apocalyptic wasteland survivor in gas mask and leather gear, rusted vehicles, orange toxic sky, Mad Max inspired, cinematic, photorealistic, 8K",tags:["废土","科幻","生存"],likes:5430,image:"showcase/06-yuyedongjing.jpg"},
{id:21,title:"星空少女",author:"治愈系",tool:"Stable Diffusion XL",type:"image",date:"2026-06-17",prompt:"Anime-style girl floating in starry space, hair flowing like galaxy, surrounded by glowing constellation lines, dreamy ethereal atmosphere, soft pastel colors, 4K",tags:["治愈","星空","人物"],likes:4120,image:"showcase/07-jiguangsenlin.jpg"},
{id:22,title:"九龙城寨2049",author:"赛博香港",tool:"Midjourney V8.1",type:"image",date:"2026-06-17",prompt:"Kowloon Walled City reimagined in 2049, dense vertical architecture, neon signs in Cantonese, flying drones, rain, Blade Runner meets Hong Kong aesthetic, ultra wide shot",tags:["赛博朋克","香港","城市"],likes:6780,image:"showcase/06-yuyedongjing.jpg"},
{id:23,title:"唐宫夜宴",author:"大唐风华",tool:"Stable Diffusion + ControlNet",type:"image",date:"2026-06-17",prompt:"Tang Dynasty palace banquet at night, court ladies in flowing silk dresses, lanterns and candles, gold and crimson color palette, traditional Chinese figure painting style",tags:["古风","大唐","人物"],likes:5340,image:"showcase/09-dunhuangfeitian.jpg"},
{id:24,title:"虫洞穿越",author:"太空探索",tool:"Midjourney V8.1",type:"image",date:"2026-06-17",prompt:"Spaceship entering a massive wormhole, gravitational lensing effects, swirling blue and purple energy, Einstein-Rosen bridge visualization, cinematic sci-fi, 8K",tags:["科幻","太空","虫洞"],likes:4890,image:"showcase/15-yinhezhanjian.jpg"},
{id:25,title:"AI电影预告片·觉醒",author:"AI影视工坊",tool:"Runway Gen-4 + ElevenLabs",type:"video",date:"2026-06-17",prompt:"Sci-fi movie trailer generated entirely by AI, humanoid robot awakening in laboratory, dramatic orchestral score, quick cuts, cinematic widescreen, voiceover narration, 2 minutes",tags:["科幻","电影","预告片"],likes:9120,image:"showcase/05-hackthon.jpg"},
{id:26,title:"国风水墨动画·竹",author:"墨韵AI",tool:"Kling AI + Pika",type:"video",date:"2026-06-17",prompt:"Animated ink wash painting of bamboo grove swaying in wind, ink drops forming birds that fly away, traditional Chinese music, seamless loop, minimalist aesthetic",tags:["国风","动画","水墨"],likes:7560,image:"showcase/09-dunhuangfeitian.jpg"},
{id:27,title:"赛博都市漫游",author:"数字城市",tool:"Luma AI + Runway",type:"video",date:"2026-06-16",prompt:"First-person drone flythrough of futuristic cyberpunk city at night, neon reflections on skyscrapers, flying vehicles, rain particles, cinematic slow motion, 60fps",tags:["赛博朋克","城市","漫游"],likes:8230,image:"showcase/06-yuyedongjing.jpg"},
{id:28,title:"AI生成MV·星空",author:"音乐可视化",tool:"Suno V4 + Runway Gen-4",type:"video",date:"2026-06-16",prompt:"Full AI-generated music video for original song, cosmic visuals synchronized to beat, nebula explosions, particle effects, emotional storytelling, 3 minutes",tags:["音乐","MV","创意"],likes:6890,image:"showcase/07-jiguangsenlin.jpg"},
{id:29,title:"数字人新闻播报",author:"虚拟主播",tool:"HeyGen + ChatGPT",type:"video",date:"2026-06-16",prompt:"Photorealistic digital human news anchor delivering AI industry headlines, natural gestures and expressions, studio background with holographic data displays, 5 minutes",tags:["数字人","新闻","虚拟主播"],likes:5670,image:"showcase/01-wuzhiqi.jpg"},
{id:30,title:"3D产品展示·概念车",author:"工业设计",tool:"Tripo AI + Blender",type:"video",date:"2026-06-15",prompt:"360-degree product showcase of futuristic concept car, rotating on turntable, reflections on chrome surface, studio lighting, photorealistic render, 30 seconds",tags:["3D","产品","汽车"],likes:4450,image:"showcase/08-weilaijijia.jpg"},
{id:31,title:"AI动画短片·猫的旅行",author:"动画工坊",tool:"Pika 2.0 + Runway",type:"video",date:"2026-06-15",prompt:"Short animated film about a cat's journey through different worlds, hand-drawn animation style, warm color palette, emotional storytelling, original soundtrack, 2 minutes",tags:["动画","故事","治愈"],likes:9340,image:"showcase/10-zhengqipengkemao.jpg"},
{id:32,title:"虚拟时装秀",author:"数字时尚",tool:"Stable Diffusion + Runway",type:"video",date:"2026-06-15",prompt:"AI-generated virtual fashion show, avant-garde designs impossible in reality, fabric that flows like water and fire, runway with holographic effects, cinematic",tags:["时尚","虚拟","创意"],likes:6120,image:"showcase/11-shenhailonggong.jpg"},
{id:33,title:"火星殖民纪录",author:"太空视觉",tool:"Midjourney + Runway Gen-4",type:"video",date:"2026-06-14",prompt:"Documentary-style visualization of Mars colonization, domed habitats, astronauts on red surface, dust storms, cinematic NASA-grade visuals, voiceover narration",tags:["科幻","纪录","太空"],likes:7890,image:"showcase/04-chuyunzhuan.jpg"},
{id:34,title:"AI广告创意·香水",author:"品牌营销",tool:"Sora + ElevenLabs",type:"video",date:"2026-06-14",prompt:"Luxury perfume commercial generated by AI, crystal bottle with swirling galaxy inside, slow motion liquid dynamics, golden particles, orchestral score, 30 seconds",tags:["广告","创意","品牌"],likes:5340,image:"showcase/03-zishilinan.jpg"},
{id:35,title:"游戏CG预告·暗影",author:"游戏概念",tool:"Midjourney + Runway + UE5",type:"video",date:"2026-06-14",prompt:"Game cinematic trailer for dark fantasy RPG, epic battle scenes, dragon boss fight, magic effects, dynamic camera movements, photorealistic characters, 90 seconds",tags:["游戏","CG","预告"],likes:8560,image:"showcase/02-chisezhangren.jpg"},
{id:36,title:"AI音乐可视化·脉动",author:"音画实验",tool:"Stable Diffusion + Pika",type:"video",date:"2026-06-17",prompt:"Audio-reactive visualizer, geometric patterns pulsing to electronic music beat, neon color palette, fractal animations, VJ loop style, 4K 60fps",tags:["音乐","视觉","抽象"],likes:4780,image:"showcase/07-jiguangsenlin.jpg"}
];'''

# Replace showcaseData
old_showcase = r"const showcaseData = \[[\s\S]*?\];"
html = re.sub(old_showcase, new_showcase_data, html, count=1)

# ========== 2. New renderShowcase with pagination + sorting ==========
new_render_showcase = '''function renderShowcase(){
  let sortMode=window._showcaseSort||'recommend';
  let page=window._showcasePage||1;
  const perPage=12;
  let data=[...showcaseData];
  if(sortMode==='newest')data.sort((a,b)=>b.date.localeCompare(a.date));
  else if(sortMode==='hottest')data.sort((a,b)=>b.likes-a.likes);
  else data.sort((a,b)=>b.likes-a.likes);
  const totalPages=Math.ceil(data.length/perPage);
  if(page>totalPages)page=totalPages;
  if(page<1)page=1;
  window._showcasePage=page;
  const pageData=data.slice((page-1)*perPage,page*perPage);
  const top=data.slice(0,5);
  function card(s,i){
    const isVideo=s.type==='video';
    return`<div class="showcase-card" onclick="showDetail(showcaseData.find(x=>x.id===${s.id}))">
      <div class="sc-preview">${isVideo?'<span class="sc-play">▶</span>':''}<img src="${s.image}" alt="${s.title}" loading="lazy"><span class="sc-likes">❤️ ${s.likes.toLocaleString()}</span></div>
      <div class="sc-body"><div class="sc-title">${s.title}</div><div class="sc-meta"><span>${s.author}</span><span>·</span><span>${s.tool}</span></div><div class="sc-tags">${s.tags.map(t=>`<span class="sc-tag">${t}</span>`).join('')}${isVideo?'<span class="sc-tag sc-tag-video">🎬视频</span>':''}</div></div>
    </div>`;
  }
  const paginationHTML=totalPages>1?`<div class="pagination"><button class="page-btn" onclick="window._showcasePage=${page-1};updateContent()" ${page<=1?'disabled':''}>◂ 上一页</button><span class="page-info">${page} / ${totalPages}</span><button class="page-btn" onclick="window._showcasePage=${page+1};updateContent()" ${page>=totalPages?'disabled':''}>下一页 ▸</button></div>`:'';
  return`
    <div class="hero-showcase">
      <div class="hero-slider">
        ${top.map((s,i)=>`
        <div class="hero-slide${i===0?' active':''}" onclick="showDetail(showcaseData.find(x=>x.id===${s.id}))">
          <img src="${s.image}" alt="${s.title}" loading="${i===0?'eager':'lazy'}">
          ${s.type==='video'?'<span class="hero-play-icon">▶</span>':''}
          <div class="hero-overlay"><div class="hero-title">${s.title}</div><div class="hero-meta"><span>👤 ${s.author}</span><span>🛠️ ${s.tool}</span><span>❤️ ${s.likes.toLocaleString()}</span></div></div>
        </div>`).join('')}
        <button class="hero-nav prev">◂</button><button class="hero-nav next">▸</button>
        <div class="hero-dots">${top.map((_,i)=>`<span class="hero-dot${i===0?' active':''}"></span>`).join('')}</div>
      </div>
    </div>
    <div class="section-header"><h2 class="section-title">✨ 精选AI作品 <span style="font-size:.7rem;color:var(--text-secondary);font-weight:400;">(${showcaseData.length}件)</span></h2><div class="section-tabs"><span class="section-tab${sortMode==='recommend'?' active':''}" data-sort="recommend">推荐</span><span class="section-tab${sortMode==='newest'?' active':''}" data-sort="newest">最新</span><span class="section-tab${sortMode==='hottest'?' active':''}" data-sort="hottest">最热</span></div></div>
    <div class="showcase-grid">${pageData.map(card).join('')}</div>
    ${paginationHTML}`;
}'''

old_render = r"function renderShowcase\(\)\{[\s\S]*?\n\}"
html = re.sub(old_render, new_render_showcase, html, count=1)

# ========== 3. Update showDetail for video ==========
new_show_detail = '''function showDetail(item){
  const isVideo=item.type==='video';
  document.getElementById('modalImg').style.display=isVideo?'none':'';
  document.getElementById('modalImg').src=isVideo?'':item.image;
  document.getElementById('modalVideo').style.display=isVideo?'flex':'none';
  document.getElementById('modalBody').innerHTML=`
    <div class="md-title">${isVideo?'🎬 ':''}${item.title}</div>
    <div class="md-author">👤 ${item.author} · 🛠️ ${item.tool} · ❤️ ${item.likes.toLocaleString()} · ${isVideo?'🎬 视频':'🖼️ 图片'}</div>
    <div class="md-section"><div class="md-label">提示词 / Prompt</div><div class="md-prompt">${item.prompt}</div></div>
    <div class="md-section"><div class="md-label">标签</div><div class="md-tags">${item.tags.map(t=>`<span class="md-tag">#${t}</span>`).join('')}</div></div>
    <div class="md-actions">
      <button class="md-btn primary" onclick="copyPrompt('${item.prompt.replace(/'/g,"\\'")}')">📋 复制提示词</button>
      <button class="md-btn secondary" onclick="closeDetail()">关闭</button>
    </div>`;
  document.getElementById('detailModal').classList.add('active');
  document.body.style.overflow='hidden';
}'''

old_show_detail = r"function showDetail\(item\)\{[\s\S]*?\n\}"
html = re.sub(old_show_detail, new_show_detail, html, count=1)

# ========== 4. Update tab click handlers ==========
old_tab_handler = r"document\.querySelectorAll\('\.section-tab'\)\.forEach\(t=>\{t\.addEventListener\('click',function\(\)\{this\.parentElement\.querySelectorAll\('\.section-tab'\)\.forEach\(x=>x\.classList\.remove\('active'\)\);this\.classList\.add\('active'\);\}\);\}\);</script>"
new_tab_handler = '''// Delegate tab clicks
document.addEventListener('click',function(e){
  if(e.target.classList.contains('section-tab')){
    const sort=e.target.dataset.sort;
    if(sort){window._showcaseSort=sort;window._showcasePage=1;updateContent();}
  }
});</script>'''
html = html.replace(old_tab_handler, new_tab_handler)

# ========== 5. Add video placeholder in modal + CSS ==========
# Add video placeholder div after modal-img
old_modal_img = '<img class="modal-img" id="modalImg" src="" alt="">'
new_modal_img = '<img class="modal-img" id="modalImg" src="" alt="" style="display:block;"><div class="modal-video" id="modalVideo" style="display:none;"><div class="video-placeholder"><span class="vp-icon">🎬</span><p class="vp-text">视频作品预览</p><p class="vp-sub">AI生成的视频作品，支持在线播放</p></div></div>'
html = html.replace(old_modal_img, new_modal_img)

# Add CSS for video overlay, pagination, video modal
new_css = '''
/* Video card overlay */
.sc-play{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;background:rgba(0,0,0,.75);border:2px solid rgba(255,255,255,.6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.2rem;color:#fff;z-index:3;pointer-events:none;transition:all .3s;}
.showcase-card:hover .sc-play{background:var(--accent);border-color:var(--accent);box-shadow:0 0 20px var(--accent-glow);}
.sc-tag-video{background:rgba(0,229,192,.12)!important;border-color:rgba(0,229,192,.3)!important;color:var(--accent-cyber)!important;}
.hero-play-icon{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:64px;height:64px;background:rgba(0,0,0,.7);border:2px solid rgba(255,255,255,.5);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.6rem;color:#fff;z-index:2;pointer-events:none;}
/* Pagination */
.pagination{display:flex;align-items:center;justify-content:center;gap:16px;margin-top:24px;padding:16px 0;}
.page-btn{padding:8px 18px;background:var(--card-bg);border:1px solid var(--border);border-radius:8px;color:var(--text-secondary);cursor:pointer;font-size:.82rem;transition:all .2s;}
.page-btn:hover:not(:disabled){border-color:var(--accent-cyber);color:var(--accent-cyber);}
.page-btn:disabled{opacity:.3;cursor:default;}
.page-info{font-size:.82rem;color:var(--text-secondary);}
/* Video modal */
.modal-video{width:100%;min-height:320px;display:flex;align-items:center;justify-content:center;background:#000;}
.video-placeholder{text-align:center;padding:60px 20px;}
.vp-icon{font-size:3rem;margin-bottom:12px;}
.vp-text{font-size:1.1rem;color:var(--text);margin-bottom:6px;}
.vp-sub{font-size:.8rem;color:var(--text-secondary);}
@media(max-width:768px){.hero-play-icon{width:44px;height:44px;font-size:1.2rem;}}
'''
# Insert before the closing </style> tag
html = html.replace('</style>', new_css + '\n</style>')

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ index.html updated successfully")
print("Changes: 36 showcase items, pagination (12/page), video type, working tabs (推荐/最新/最热)")
