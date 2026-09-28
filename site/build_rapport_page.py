import os
import json

md_path = "/home/elrems/kaggle/docs/RAPPORT_GLOBAL.md"
with open(md_path, "r", encoding="utf-8") as f:
    raw_md = f.read()

# JSON encode raw_md to safely embed it in Javascript
json_md = json.dumps(raw_md)

html_content = f"""<!doctype html>
<html lang="fr" class="dark scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rapport Global All-in-One — Gemma 4 × PrestaShop</title>
  
  <!-- Directives strictes noindex / no-robot -->
  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
  <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet">
  <meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet">

  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            background: '#090d16',
            card: '#0f172a',
            surface: '#1e293b',
            accent: '#06b6d4',
            primary: '#6366f1',
            border: '#334155'
          }},
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }}
        }}
      }}
    }}
  </script>

  <style>
    body {{
      background-color: #090d16;
      color: #cbd5e1;
      font-family: 'Inter', sans-serif;
    }}
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: #090d16;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #1e293b;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #334155;
    }}
    /* Markdown Prose Custom Styles */
    .prose-custom h1 {{
      color: #ffffff;
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      margin-top: 3rem;
      margin-bottom: 1.25rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid #1e293b;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      scroll-margin-top: 100px;
    }}
    .prose-custom h2 {{
      color: #38bdf8;
      font-size: 1.35rem;
      font-weight: 700;
      margin-top: 2rem;
      margin-bottom: 1rem;
      scroll-margin-top: 100px;
    }}
    .prose-custom h3 {{
      color: #818cf8;
      font-size: 1.1rem;
      font-weight: 600;
      margin-top: 1.5rem;
      margin-bottom: 0.75rem;
      scroll-margin-top: 100px;
    }}
    .prose-custom p {{
      margin-top: 0.75rem;
      margin-bottom: 0.75rem;
      line-height: 1.75;
      color: #cbd5e1;
    }}
    .prose-custom ul, .prose-custom ol {{
      margin-top: 0.75rem;
      margin-bottom: 0.75rem;
      padding-left: 1.5rem;
    }}
    .prose-custom ul {{
      list-style-type: disc;
    }}
    .prose-custom ol {{
      list-style-type: decimal;
    }}
    .prose-custom li {{
      margin-top: 0.35rem;
      margin-bottom: 0.35rem;
      line-height: 1.6;
    }}
    .prose-custom blockquote {{
      border-left: 4px solid #06b6d4;
      background: rgba(15, 23, 42, 0.7);
      padding: 1rem 1.25rem;
      margin: 1.25rem 0;
      border-radius: 0 0.5rem 0.5rem 0;
      color: #94a3b8;
      font-style: italic;
    }}
    .prose-custom table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      margin: 1.5rem 0;
      border-radius: 0.75rem;
      overflow: hidden;
      border: 1px solid #1e293b;
      background: #0f172a;
      font-size: 0.85rem;
    }}
    .prose-custom th {{
      background: #1e293b;
      color: #f8fafc;
      font-weight: 700;
      padding: 0.75rem 1rem;
      text-align: left;
      border-bottom: 1px solid #334155;
    }}
    .prose-custom td {{
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #1e293b;
      color: #cbd5e1;
    }}
    .prose-custom tr:last-child td {{
      border-bottom: none;
    }}
    .prose-custom tr:hover td {{
      background: rgba(30, 41, 59, 0.4);
    }}
    .prose-custom code:not(pre code) {{
      background: #1e293b;
      color: #38bdf8;
      padding: 0.2rem 0.4rem;
      border-radius: 0.375rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85em;
      border: 1px solid rgba(51, 65, 85, 0.6);
    }}
    .prose-custom pre {{
      background: #0b1120;
      border: 1px solid #1e293b;
      border-radius: 0.75rem;
      padding: 1.25rem 1rem 1rem 1rem;
      overflow-x: auto;
      margin: 1.25rem 0;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      line-height: 1.5;
      color: #e2e8f0;
      position: relative;
    }}
    .prose-custom pre code {{
      background: transparent;
      padding: 0;
      border: none;
      color: inherit;
    }}
    .prose-custom a {{
      color: #38bdf8;
      text-decoration: none;
      border-bottom: 1px dashed rgba(56, 189, 248, 0.4);
      transition: color 0.2s, border-color 0.2s;
    }}
    .prose-custom a:hover {{
      color: #7dd3fc;
      border-bottom-color: #7dd3fc;
    }}
    .prose-custom hr {{
      border: 0;
      border-top: 1px solid #1e293b;
      margin: 2.5rem 0;
    }}
    /* Toast styles */
    #copy-toast {{
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
  </style>
</head>
<body class="min-h-screen bg-background text-slate-300 selection:bg-cyan-500/20 selection:text-cyan-200">

  <!-- ========================================== -->
  <!-- TOP STICKY MASTER ACTION BAR -->
  <!-- ========================================== -->
  <header class="sticky top-0 z-50 backdrop-blur-xl bg-background/90 border-b border-slate-800 shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
      
      <!-- Logo & Back to Showcase -->
      <div class="flex items-center gap-3">
        <a href="/" class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all flex items-center gap-1.5 text-xs font-semibold" title="Retourner à la vitrine interactive">
          <i data-lucide="arrow-left" class="w-4 h-4 text-cyan-400"></i>
          <span class="hidden sm:inline">Vitrine</span>
        </a>
        <div class="h-6 w-px bg-slate-800 hidden sm:block"></div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-sm font-extrabold text-white tracking-tight">RAPPORT GLOBAL (ALL-IN-ONE)</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">1 CLIC COPIER</span>
          </div>
          <span class="block text-[11px] text-slate-400 font-mono">Gemma 4 (4B) LoRA &times; PrestaShop Legacy Benchmark</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2.5">
        
        <!-- Toggle Views Button -->
        <div class="bg-slate-900 border border-slate-800 rounded-lg p-0.5 flex items-center text-xs">
          <button id="tab-btn-rendered" onclick="switchView('rendered')" class="px-3 py-1.5 rounded-md bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30 flex items-center gap-1.5 transition-all">
            <i data-lucide="book-open" class="w-3.5 h-3.5"></i>
            <span>Rendu Formaté</span>
          </button>
          <button id="tab-btn-raw" onclick="switchView('raw')" class="px-3 py-1.5 rounded-md text-slate-400 hover:text-white font-medium flex items-center gap-1.5 transition-all">
            <i data-lucide="file-code" class="w-3.5 h-3.5"></i>
            <span>Markdown Brut</span>
          </button>
        </div>

        <!-- Download Button -->
        <a href="/RAPPORT_GLOBAL.md" download="RAPPORT_GLOBAL_GEMMA4_PRESTASHOP.md" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-1.5 transition-all shadow-sm" title="Télécharger le fichier Markdown brut">
          <i data-lucide="download" class="w-3.5 h-3.5 text-indigo-400"></i>
          <span class="hidden md:inline">Télécharger .md</span>
        </a>

        <!-- MASTER COPY BUTTON -->
        <button id="btn-master-copy" onclick="copyMasterReport()" class="px-4 py-2 rounded-xl text-xs sm:text-sm font-extrabold bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all transform active:scale-95 cursor-pointer">
          <i data-lucide="copy" class="w-4 h-4"></i>
          <span>Copier Tout le Rapport (1 Clic)</span>
        </button>

      </div>
    </div>

    <!-- Quick-Jump Section Navigation Bar -->
    <div class="border-t border-slate-800/80 bg-slate-950/60 overflow-x-auto py-2 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto flex items-center gap-2 text-xs whitespace-nowrap custom-scrollbar">
        <span class="text-slate-500 font-mono text-[11px] uppercase tracking-wider mr-1">Aller à :</span>
        <a href="#sec-1" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">1. Fiche & Chiffres</a>
        <a href="#sec-2" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">2. Enjeux Legacy</a>
        <a href="#sec-3" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">3. 6 Niveaux Débogage</a>
        <a href="#sec-4" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">4. Architecture & QLoRA</a>
        <a href="#sec-5" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">5. Résultats A/B/E</a>
        <a href="#sec-6" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">6. Les 4 Victoires</a>
        <a href="#sec-7" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">7. Sobriété Énergétique</a>
        <a href="#sec-8" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">8. Pyramide des Tests</a>
        <a href="#sec-9" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">9. Modules Tiers</a>
        <a href="#sec-10" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">10. Writeup Kaggle (EN)</a>
        <a href="#sec-11" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors">11. Guide Clé en Main</a>
      </div>
    </div>
  </header>

  <!-- ========================================== -->
  <!-- MAIN CONTAINER -->
  <!-- ========================================== -->
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Hero / Intro Banner -->
    <div class="mb-8 p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/40 border border-slate-800 shadow-xl relative overflow-hidden">
      <div class="absolute -right-12 -top-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-950/80 border border-cyan-800 text-cyan-300">
            <i data-lucide="layers" class="w-3.5 h-3.5"></i>
            Document de Synthèse Intégrale (All-in-One)
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Toute la Recherche &amp; les Données du Projet en 1 Seul Document
          </h1>
          <p class="text-sm text-slate-300 max-w-2xl leading-relaxed">
            Ce document compile l'intégralité du travail accompli : la vision métier, les résultats scientifiques (Conditions A/R/B/O/D/E), l'analyse chirurgicale des 4 victoires de Gemma 4 LoRA, l'étude de frugalité énergétique (1.9 Wh/bug), la pyramide des tests, l'évaluation des 10 modules tiers et le Writeup officiel Kaggle en anglais.
          </p>
        </div>

        <!-- Big Action Card -->
        <div class="bg-slate-950/80 border border-slate-800 p-4 rounded-xl flex flex-col items-center justify-center text-center gap-3 shrink-0 sm:w-64">
          <span class="text-xs font-mono text-slate-400">Taille : 26 Ko &bull; 11 Sections</span>
          <button onclick="copyMasterReport()" class="w-full py-3 px-4 rounded-xl font-extrabold text-xs sm:text-sm bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2 transition-all transform active:scale-95 cursor-pointer">
            <i data-lucide="copy" class="w-4 h-4"></i>
            <span>Copier Tout le Markdown</span>
          </button>
          <span class="text-[11px] text-slate-500">Prêt à coller dans Kaggle, Word ou Obsidian</span>
        </div>
      </div>
    </div>

    <!-- VIEW 1: RENDERED HTML VIEW -->
    <div id="view-rendered" class="space-y-4">
      <div id="markdown-container" class="prose-custom bg-slate-900/40 border border-slate-800/80 p-6 sm:p-10 rounded-2xl shadow-sm">
        <!-- Will be dynamically populated with marked.js -->
        <div class="py-12 text-center text-slate-400 font-mono text-sm">
          <i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-400"></i>
          Chargement et rendu du rapport intégral...
        </div>
      </div>
    </div>

    <!-- VIEW 2: RAW TEXTAREA VIEW (HIDDEN BY DEFAULT) -->
    <div id="view-raw" class="hidden space-y-4">
      <div class="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
        <span class="text-xs font-mono text-slate-400 flex items-center gap-2">
          <i data-lucide="file-text" class="w-4 h-4 text-cyan-400"></i>
          Fichier brut : <strong class="text-white">docs/RAPPORT_GLOBAL.md</strong> (Markdown GFM)
        </span>
        <div class="flex items-center gap-2">
          <button onclick="selectAllRaw()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors">
            Tout Sélectionner (Ctrl+A)
          </button>
          <button onclick="copyMasterReport()" class="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-bold text-white transition-colors flex items-center gap-1.5">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
            Copier
          </button>
        </div>
      </div>
      <textarea id="raw-markdown-area" readonly class="w-full h-[75vh] bg-slate-950 text-slate-200 font-mono text-xs p-6 rounded-xl border border-slate-800 focus:outline-none focus:border-cyan-500 custom-scrollbar leading-relaxed selection:bg-cyan-500/30 selection:text-white" spellcheck="false"></textarea>
    </div>

  </main>

  <!-- ========================================== -->
  <!-- FLOATING ACTION BUTTON (BOTTOM RIGHT) -->
  <!-- ========================================== -->
  <div class="fixed bottom-6 right-6 z-40">
    <button onclick="copyMasterReport()" class="px-5 py-3 rounded-full bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-cyan-500/30 flex items-center gap-2 transition-all transform hover:scale-105 active:scale-95 border border-cyan-400/30 cursor-pointer">
      <i data-lucide="copy" class="w-4 h-4"></i>
      <span>Copier Tout (1 Clic)</span>
    </button>
  </div>

  <!-- ========================================== -->
  <!-- TOAST NOTIFICATION -->
  <!-- ========================================== -->
  <div id="copy-toast" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 transform translate-y-24 opacity-0 pointer-events-none transition-all duration-300">
    <div class="bg-emerald-950 border border-emerald-500/60 shadow-2xl shadow-emerald-500/20 text-emerald-200 px-6 py-3.5 rounded-2xl flex items-center gap-3 text-sm font-semibold">
      <div class="w-7 h-7 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
        <i data-lucide="check" class="w-4 h-4"></i>
      </div>
      <div>
        <span class="font-bold text-white block">Rapport Copié avec Succès !</span>
        <span class="text-xs text-emerald-300 font-normal">L'intégralité du Markdown (26 000 caractères) est dans votre presse-papier.</span>
      </div>
    </div>
  </div>

  <!-- Raw Markdown Data Embedded -->
  <script>
    const RAW_MARKDOWN = {json_md};

    // Render markdown on page load
    document.addEventListener('DOMContentLoaded', () => {{
      const container = document.getElementById('markdown-container');
      const textarea = document.getElementById('raw-markdown-area');
      
      // Setup textarea
      textarea.value = RAW_MARKDOWN;

      // Configure marked
      marked.setOptions({{
        gfm: true,
        breaks: false
      }});

      // Render HTML
      container.innerHTML = marked.parse(RAW_MARKDOWN);

      // Map headers to IDs (#sec-1 to #sec-11) and add Section Copy buttons
      let secIndex = 1;
      container.querySelectorAll('h1').forEach((h1) => {{
        const text = h1.textContent.trim();
        // Check if starts with a number like "1.", "2.", "10."
        const match = text.match(/^(\\d+)\\./);
        if (match) {{
          const num = match[1];
          h1.id = 'sec-' + num;
        }} else if (text.includes("FICHE D'IDENTITÉ")) {{
          h1.id = 'sec-1';
        }} else {{
          h1.id = 'sec-' + secIndex;
          secIndex++;
        }}

        // Add a "Copier cette section" button to each H1
        const secBtn = document.createElement('button');
        secBtn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 border border-slate-700 flex items-center gap-1.5 transition-all cursor-pointer font-sans';
        secBtn.innerHTML = '<i data-lucide="copy" class="w-3 h-3"></i><span>Copier section</span>';
        secBtn.onclick = (e) => {{
          e.stopPropagation();
          copySection(h1);
        }};
        h1.appendChild(secBtn);
      }});

      // Colorize Diffs (+ green, - red, @@ cyan)
      container.querySelectorAll('pre code').forEach(codeEl => {{
        const rawCode = codeEl.innerText;
        if (rawCode.includes('--- a/') || rawCode.includes('<<<<<<< SEARCH') || rawCode.includes('@@ -')) {{
          const lines = codeEl.innerHTML.split('\\n');
          const colored = lines.map(line => {{
            if (line.startsWith('+') && !line.startsWith('+++')) {{
              return `<span class="text-emerald-400 bg-emerald-950/40 inline-block w-full">${{line}}</span>`;
            }} else if (line.startsWith('-') && !line.startsWith('---')) {{
              return `<span class="text-rose-400 bg-rose-950/40 inline-block w-full">${{line}}</span>`;
            }} else if (line.startsWith('@@')) {{
              return `<span class="text-cyan-400 font-bold inline-block w-full">${{line}}</span>`;
            }} else if (line.startsWith('&lt;&lt;&lt;&lt;&lt;&lt;&lt;') || line.startsWith('=======') || line.startsWith('&gt;&gt;&gt;&gt;&gt;&gt;&gt;')) {{
              return `<span class="text-amber-400 font-bold inline-block w-full">${{line}}</span>`;
            }}
            return line;
          }}).join('\\n');
          codeEl.innerHTML = colored;
        }}
      }});

      // Enhance pre/code blocks with individual copy buttons
      container.querySelectorAll('pre').forEach((pre) => {{
        const btn = document.createElement('button');
        btn.className = 'absolute top-3 right-3 px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] font-mono border border-slate-700 flex items-center gap-1 transition-all opacity-80 hover:opacity-100 cursor-pointer';
        btn.innerHTML = '<i data-lucide="copy" class="w-3 h-3"></i><span>Copier</span>';
        btn.onclick = (e) => {{
          e.stopPropagation();
          const code = pre.querySelector('code') ? pre.querySelector('code').innerText : pre.innerText;
          copyText(code, btn);
        }};
        pre.appendChild(btn);
      }});

      // Re-initialize lucide icons
      lucide.createIcons();
    }});

    // Universal copy with fallback
    function copyText(text, btnElement) {{
      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(text).then(() => {{
          if (btnElement) {{
            const orig = btnElement.innerHTML;
            btnElement.innerHTML = '<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i><span class="text-emerald-400">Copié</span>';
            lucide.createIcons();
            setTimeout(() => {{
              btnElement.innerHTML = orig;
              lucide.createIcons();
            }}, 2000);
          }}
        }});
      }} else {{
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-999999px';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        if (btnElement) {{
          const orig = btnElement.innerHTML;
          btnElement.innerHTML = '<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i><span class="text-emerald-400">Copié</span>';
          lucide.createIcons();
          setTimeout(() => {{
            btnElement.innerHTML = orig;
            lucide.createIcons();
          }}, 2000);
        }}
      }}
    }}

    // Master Copy Function
    function copyMasterReport() {{
      const btn = document.getElementById('btn-master-copy');
      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(RAW_MARKDOWN).then(() => {{
          showToast();
          if (btn) {{
            const orig = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="check" class="w-4 h-4 text-emerald-300"></i><span>✓ Copié dans le Presse-Papier !</span>';
            btn.classList.add('from-emerald-600', 'to-teal-600');
            setTimeout(() => {{
              btn.innerHTML = orig;
              btn.classList.remove('from-emerald-600', 'to-teal-600');
              lucide.createIcons();
            }}, 3000);
          }}
        }}).catch(err => {{
          copyFallback();
        }});
      }} else {{
        copyFallback();
      }}
    }}

    function copyFallback() {{
      const ta = document.createElement('textarea');
      ta.value = RAW_MARKDOWN;
      ta.style.position = 'fixed';
      ta.style.left = '-999999px';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast();
    }}

    // Copy specific section from H1 to next H1
    function copySection(h1Element) {{
      const title = h1Element.innerText.replace('Copier section', '').trim();
      // Find content between this H1 and next H1
      let content = title + '\\n\\n';
      let curr = h1Element.nextElementSibling;
      while (curr && curr.tagName !== 'H1') {{
        content += curr.innerText + '\\n\\n';
        curr = curr.nextElementSibling;
      }}
      copyText(content);
      showToast();
    }}

    function showToast() {{
      const toast = document.getElementById('copy-toast');
      toast.classList.remove('translate-y-24', 'opacity-0', 'pointer-events-none');
      toast.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {{
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-24', 'opacity-0', 'pointer-events-none');
      }}, 3500);
      lucide.createIcons();
    }}

    function switchView(view) {{
      const renderedView = document.getElementById('view-rendered');
      const rawView = document.getElementById('view-raw');
      const btnRendered = document.getElementById('tab-btn-rendered');
      const btnRaw = document.getElementById('tab-btn-raw');

      if (view === 'rendered') {{
        renderedView.classList.remove('hidden');
        rawView.classList.add('hidden');
        btnRendered.className = 'px-3 py-1.5 rounded-md bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30 flex items-center gap-1.5 transition-all';
        btnRaw.className = 'px-3 py-1.5 rounded-md text-slate-400 hover:text-white font-medium flex items-center gap-1.5 transition-all';
      }} else {{
        renderedView.classList.add('hidden');
        rawView.classList.remove('hidden');
        btnRaw.className = 'px-3 py-1.5 rounded-md bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30 flex items-center gap-1.5 transition-all';
        btnRendered.className = 'px-3 py-1.5 rounded-md text-slate-400 hover:text-white font-medium flex items-center gap-1.5 transition-all';
      }}
      lucide.createIcons();
    }}

    function selectAllRaw() {{
      const area = document.getElementById('raw-markdown-area');
      area.focus();
      area.select();
    }}
  </script>
</body>
</html>
"""

target_path = "/home/elrems/kaggle.d1dev.fr/public/rapport.html"
with open(target_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {target_path} successfully. Size: {len(html_content)} bytes.")
