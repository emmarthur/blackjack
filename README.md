# Blackjack (catalog #439)

Classic 21 from Al Sweigart’s *Big Book of Small Python Projects* (Project #4). Rules live in `blackjack_core.py`.

## Run the web demo (port 3027)

```powershell
Set-Location "c:\Users\emmak\Desktop\Content\CodingProjects\PortProjects\demos\blackjack\web"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 3027
```

Open http://localhost:3027

## CLI

```powershell
Set-Location "c:\Users\emmak\Desktop\Content\CodingProjects\PortProjects\demos\blackjack"
python reference/run_cli.py
```

Book provenance: [BOOK_DIRECTIONS.md](./BOOK_DIRECTIONS.md).
