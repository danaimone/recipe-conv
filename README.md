# recipe-conv

Convert a **Mela** export (`*.melarecipes`) into a **Paprika** archive (`*.paprikarecipes`) that Crouton (or Paprika) can import.

---

## Contents

| file | language | purpose |
|------|----------|---------|
| `Program.fs` | F# / .NET | Fast, type‑safe converter (original). |
| `convert.py` | Python 3 | Zero‑build alternative; handy when you don’t want .NET. |

---

## 1 · Prerequisites

| route | requirements |
|-------|--------------|
| **F#** | .NET 6 / 7 / 8 SDK (`dotnet --version` ≥ 6). |
| **Python** | Python 3.8+ (3.11+ recommended). Optional: `pip install tqdm` for progress bar. |

---

## 2 · Using the F# converter

```bash
# clone & build (Release config)
git clone https://github.com/<your‑fork>/recipe-conv.git
cd recipe-conv
dotnet build -c Release

# run
dotnet run -c Release -- ~/Downloads/Recipes.melarecipes out/all.paprikarecipes
```

*The output folder must exist (`mkdir -p out`) or use a path in the current directory.*

Want a single self‑contained DLL?

```bash
dotnet publish -c Release -o publish
# then
dotnet publish/recipe-conv.dll <input.melarecipes> <output.paprikarecipes>
```

---

## 3 · Using the Python converter

```bash
# optional: virtualenv
python -m venv .venv && source .venv/bin/activate

# progress bar
pip install tqdm

# run
python convert.py ~/Downloads/Recipes.melarecipes out/all.paprikarecipes
```

No external deps besides `tqdm`; the script drops it if not present.

---

## 4 · Import into Crouton / Paprika

1. **Settings › Import › Paprika**  
2. Select the `*.paprikarecipes` file you produced.  
3. Crouton iterates through each recipe and adds it to your library.

---

## 5 · Troubleshooting

| symptom | fix |
|---------|-----|
| `DirectoryNotFoundException` | Create the **output folder** first or specify an existing path. |
| `FS0058` indentation errors | Use the bundled `Program.fs` or add `<LangVersion>7.0</LangVersion>` to the fsproj. |
| Python `IndexError` on images | Pull latest `convert.py` (handles empty `images` arrays). |

---

## 6 · Credits

Originally created by **Chris Nola** — see the upstream repo <https://github.com/chrnola/recipe-conv>. This fork cleans up CLI handling, adds Python support, and updates docs, but the core idea and F# implementation are his. 🙌

---

## 7 · License

MIT — see `LICENSE`.


