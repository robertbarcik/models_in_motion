# L3 "Open Models on Your Machines" - demo code

Run order (all on CPU; Ollama must be running locally):

    python3.12 -m venv venv && ./venv/bin/pip install -r requirements.txt
    ./venv/bin/python hub_inspect.py                      # Demo A
    ./venv/bin/python sentiment_pipeline.py               # Demo B
    ./venv/bin/python sentiment_unhidden.py
    ./venv/bin/python chat_template_peek.py
    ./venv/bin/python generate_transformers.py
    ollama create team-assistant -f Modelfile             # Demo C
    ./venv/bin/python ollama_api.py
    LLM_BASE_URL=http://localhost:11434/v1 LLM_MODEL=qwen2.5:0.5b \
        ./venv/bin/python switch_worlds.py                # two worlds
    ./venv/bin/python make_dataset.py                     # Demo D
    ./venv/bin/python train_lora.py
    ./venv/bin/python use_adapter.py
    ./venv/bin/python merge_adapter.py
    ./venv/bin/python safetensors_peek.py                 # serialization
    ./venv/bin/python -u pickle_contrast.py

`adapter/` (2.1 MB) is committed as the chapter's artifact; `merged/`
(957 MB) is not.
