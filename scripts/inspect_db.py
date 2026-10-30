"""Реальный SELECT SQLite, стандартная библиотека. Не требует backend."""
import argparse
import html
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERY = """SELECT p.id, p.name, p.article, p.price, c.name AS category, p.created_at
FROM parts p JOIN categories c ON c.id = p.category_id ORDER BY p.id"""

def inspect(db_path, html_path=None):
    with sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True) as db:
        rows = db.execute(QUERY).fetchall()
        schema = [row[0] for row in db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name IN ('parts', 'categories') ORDER BY name")]
    columns = ["id", "name", "article", "price, ₽", "category", "created_at (UTC)"]
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))
    if html_path:
        table = "<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in columns) + "</tr>"
        table += "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>" for row in rows)
        markup = f'''<!doctype html><html lang="ru"><meta charset="utf-8"><title>SQLite — АвтоДеталь</title>
<style>body{{font:16px Arial;color:#172f3c;padding:36px;background:#f5f7f8}}h1{{font-size:30px}}table{{border-collapse:collapse;background:white;width:100%}}th,td{{padding:14px;border:1px solid #dae2e6;text-align:left}}th{{background:#172f3c;color:white}}pre{{white-space:pre-wrap;line-height:1.5;background:white;padding:20px;border:1px solid #dae2e6}}p{{color:#526570}}</style>
<h1>Таблица parts · SQLite</h1><p>Источник: {html.escape(str(db_path))}</p>
<pre>{html.escape(QUERY)}</pre><table>{table}</table><p>Получено строк: {len(rows)}</p>
<h2>Ограничения и структура таблиц</h2><pre>{html.escape(';'+chr(10)+chr(10)).join(html.escape(s) for s in schema)}</pre></html>'''
        html_path.write_text(markup, encoding="utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=ROOT / "data/autodetal.db")
    parser.add_argument("--html", type=Path)
    args = parser.parse_args()
    inspect(args.db, args.html)
