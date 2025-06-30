Multi-Summary API

FastAPI 서비스로 PDF 요약과 채팅 기록 요약을 제공합니다.

LangChain 0.2+ 최신 provider 패키지(langchain-openai, langchain-chroma) 사용
Chroma VectorStore + SQLite 캐시 + OpenAI GPT
Quick Start

git clone https://github.com/<USER>/<REPO>.git
cd <REPO>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
uvicorn app.main:app --reload
