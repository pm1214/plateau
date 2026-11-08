"""テスト共通の設定: tools/ を import できるようにし、フィクスチャの場所を返す。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
