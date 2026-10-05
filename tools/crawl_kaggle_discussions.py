#!/usr/bin/env python3
"""Crawler automatique de toutes les discussions du concours Kaggle Gemma 4 Developer Agent.

Utilise l'API CLI officielle Kaggle (pas de blocage Cloudflare/CAPTCHA).
Archive les discussions en JSON brut et génère une synthèse Markdown dans docs/kaggle_discussions/.
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

COMP = "gemma-4-developer-agent"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "kaggle_discussions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_html(raw_html: str) -> str:
    """Nettoie sommairement les balises HTML en texte lisible."""
    text = re.sub(r'<pre><code>(.*?)</code></pre>', r'\n```\n\1\n```\n', raw_html, flags=re.DOTALL)
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text)
    text = re.sub(r'<h2>(.*?)</h2>', r'\n## \1\n', text)
    text = re.sub(r'<h3>(.*?)</h3>', r'\n### \1\n', text)
    text = re.sub(r'<li>(.*?)</li>', r'- \1\n', text)
    text = re.sub(r'<p>(.*?)</p>', r'\1\n\n', text)
    text = re.sub(r'<br\s*/?>', r'\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
    return text.strip()


def run_cmd(cmd_list):
    res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=60)
    if res.returncode != 0:
        return None
    return res.stdout


def fetch_all_topics():
    topics = []
    page_token = None
    page_num = 1

    print(f"📡 Récupération de la liste des topics pour {COMP}...")
    while True:
        cmd = ["kaggle", "competitions", "topics", "list", COMP, "--format", "json"]
        if page_token:
            cmd.extend(["--page-token", str(page_token)])
        
        out = run_cmd(cmd)
        if not out:
            break
        
        # Le CLI Kaggle peut afficher 'Next Page Token = X' en stderr/stdout ou en fin de sortie
        token_match = re.search(r'Next Page Token\s*=\s*([^\s\n\r]+)', out)
        next_token = token_match.group(1) if token_match else None
        
        # Nettoyer JSON
        json_str = re.sub(r'Warning:.*?\n', '', out)
        json_str = re.sub(r'Next Page Token.*?\n', '', json_str).strip()
        
        try:
            batch = json.loads(json_str)
            if not batch:
                break
            topics.extend(batch)
            print(f"  • Page {page_num} : {len(batch)} topics trouvés (Total : {len(topics)})")
        except Exception as e:
            print(f"  ⚠️ Erreur parsing JSON page {page_num}: {e}")
            break

        if not next_token or next_token == page_token:
            break
        page_token = next_token
        page_num += 1
        time.sleep(1)

    return topics


def fetch_topic_messages(topic_id):
    cmd = ["kaggle", "competitions", "topic-messages", COMP, str(topic_id), "--format", "json"]
    out = run_cmd(cmd)
    if not out:
        return []
    try:
        return json.loads(out)
    except:
        return []


def main():
    topics = fetch_all_topics()
    print(f"\n📋 Total topics collectés : {len(topics)}")

    index_lines = [
        f"# 📚 Archives Intégrales des Discussions Kaggle — {COMP}\n",
        f"> *Dernière mise à jour : {time.strftime('%Y-%m-%d %H:%M:%S UTC')}*\n",
        "| ID | Date | Titre | Votes | Commentaires | Fichier |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for i, t in enumerate(topics, 1):
        tid = t["id"]
        title = t.get("title", f"Topic {tid}").strip()
        date = t.get("postDate", "")[:10]
        votes = t.get("votes", 0)
        comments = t.get("commentCount", 0)

        # Fichier markdown individuel
        clean_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '_', title.lower())[:50].strip('_')
        md_filename = f"{tid}_{clean_slug}.md"
        md_path = OUT_DIR / md_filename

        print(f"[{i:2d}/{len(topics)}] Crawl topic {tid} : {title[:50]}...")
        messages = fetch_topic_messages(tid)

        md_content = [
            f"# Topic {tid}: {title}\n",
            f"- **Lien Kaggle** : https://www.kaggle.com/competitions/{COMP}/discussion/{tid}",
            f"- **Date** : {t.get('postDate')}",
            f"- **Votes** : {votes} | **Commentaires** : {len(messages)}\n",
            "---\n"
        ]

        for m_idx, m in enumerate(messages, 1):
            m_author = m.get("authorName") or "Participant"
            m_date = m.get("postDate", "")
            m_votes = m.get("votes", 0)
            raw_c = m.get("content", "")
            clean_c = clean_html(raw_c)

            md_content.append(f"### Message #{m_idx} — {m_author} ({m_date}) [Votes: {m_votes}]\n")
            md_content.append(clean_c + "\n")
            md_content.append("---\n")

        md_path.write_text("\n".join(md_content), encoding="utf-8")
        index_lines.append(f"| [{tid}](https://www.kaggle.com/competitions/{COMP}/discussion/{tid}) | {date} | {title} | {votes} | {len(messages)} | [{md_filename}](./{md_filename}) |")
        time.sleep(0.5)

    (OUT_DIR / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"\n🎉 Crawl terminé ! Toutes les discussions sont archivées dans {OUT_DIR}/")


if __name__ == "__main__":
    main()
