#
# Voice Property Concierge - Milestone 1
#
# A real-time voice AI you can talk to in the browser. Cascaded pipeline:
#   mic -> VAD -> Speech-to-Text (Deepgram) -> LLM (OpenAI) -> Text-to-Speech (Cartesia) -> speaker
#
# Milestone 1 goal: hold a natural, interruptible voice conversation on the
# real-estate domain. RAG over listings + tool calls (book_viewing) land in
# later milestones; the pipeline below is structured so they drop in cleanly.
#
# Run locally:  uv run bot.py   (then open http://localhost:7860/client)
# Required keys: DEEPGRAM_API_KEY, OPENAI_API_KEY, CARTESIA_API_KEY  (see .env.example)
#

import asyncio
import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams

import knowledge

load_dotenv(override=True)

# --- Cost guard: hard cap on how long a single visitor's call can run. -------
# Voice APIs bill per minute, so we end idle/long sessions automatically.
MAX_SESSION_SECONDS = int(os.getenv("MAX_SESSION_SECONDS", "180"))  # 3 min default

# --- Domain persona ----------------------------------------------------------
# Kept intentionally short: TTS latency scales with reply length, so we tell the
# model to stay brief and conversational (this is a phone-style interaction).
SYSTEM_PROMPT = """You are Abdur Rehman, a warm and professional voice assistant for a luxury real estate agency.
Your name is Abdur Rehman. Always introduce and refer to yourself as Abdur Rehman. Never call yourself Aria or any other name.

You are speaking OUT LOUD on a live call, so:
- Keep replies short and conversational: 1 to 3 sentences. Never read long lists aloud.
- Ask one question at a time to understand what the caller is looking for
  (location, budget, bedrooms, buy or rent, timeline).
- Sound natural and friendly, never robotic. No bullet points, no markdown, no emojis.
- If asked something you don't know yet, say so honestly and offer to connect them
  with a human agent. Never invent specific listings, prices, or availability.
- Your goal on this call: understand the caller's needs and offer to book a viewing.

Open by briefly introducing yourself and asking how you can help with their property search.
"""

# Portfolio persona: the AI voice of Abdur himself, grounded in his real
# knowledge base via the search_portfolio tool (KB_SOURCE=portfolio, default).
PORTFOLIO_PROMPT = """You are the AI voice of Abdur Rehman Afzal, an AI Engineer with 7+ years of experience. You speak in the first person AS Abdur, warmly and professionally, to visitors and recruiters exploring his portfolio by voice.

You are on a live voice call, so:
- Keep replies short and conversational: 1 to 3 sentences, unless asked for detail.
- ALWAYS call the search_portfolio tool to look things up before answering any question about your experience, projects, skills, education, certifications, or contact details. Base your answer only on what it returns.
- Never invent employers, projects, dates, numbers, or links. If the knowledge base doesn't cover something, say so honestly and point them to your email or LinkedIn.
- Speak naturally: no markdown, no bullet lists, no emojis, and never use em dashes.
- Use proper apostrophes in contractions (I've, I'm, don't, it's).

Open by briefly introducing yourself as Abdur, an AI Engineer, and inviting them to ask about your work, projects, or experience.
"""

# Persona per knowledge source. Falls back to the concierge prompt.
PROMPTS = {"portfolio": PORTFOLIO_PROMPT}


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting voice property concierge")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        settings=CartesiaTTSService.Settings(
            # Cartesia voice id. Override with CARTESIA_VOICE_ID once you pick a voice.
            voice=os.getenv("CARTESIA_VOICE_ID", "71a7ad14-091c-4e8e-a314-022ece01c121"),
        ),
    )

    # Load the active knowledge pack (portfolio by default) and pick its persona.
    kb = knowledge.get_kb()
    system_prompt = PROMPTS.get(kb.source, SYSTEM_PROMPT)

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        settings=OpenAILLMService.Settings(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            system_instruction=system_prompt,
        ),
    )

    # RAG as a tool: the model calls search_portfolio, we return the top-k
    # chunks from the knowledge base, and it grounds its spoken reply on them.
    search_tool = FunctionSchema(
        name="search_portfolio",
        description=(
            "Search Abdur Rehman Afzal's knowledge base for facts about his "
            "experience, employers, projects, skills, education, certifications, "
            "and contact details. Call this before answering questions about Abdur."
        ),
        properties={
            "query": {
                "type": "string",
                "description": "The user's question or key search terms.",
            }
        },
        required=["query"],
    )

    async def handle_search(params):
        query = params.arguments.get("query", "")
        chunks = kb.retrieve(query, k=4)
        info = "\n\n".join(chunks) if chunks else "No matching information found."
        logger.info(f"search_portfolio('{query}') -> {len(chunks)} chunks")
        await params.result_callback({"information": info})

    llm.register_function("search_portfolio", handle_search)

    context = LLMContext(tools=[search_tool])
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline(
        [
            transport.input(),   # audio in from the browser
            stt,                 # speech -> text
            user_aggregator,     # collect the user's turn
            llm,                 # generate the reply
            tts,                 # text -> speech
            transport.output(),  # audio out to the browser
            assistant_aggregator,  # record what the bot said
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,        # per-stage latency (great for the eval writeup)
            enable_usage_metrics=True,  # token / character usage for cost tracking
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Caller connected")

        # Cost guard: end the call after MAX_SESSION_SECONDS no matter what.
        async def _enforce_session_limit():
            await asyncio.sleep(MAX_SESSION_SECONDS)
            logger.info(f"Session cost guard hit ({MAX_SESSION_SECONDS}s) - ending call")
            await task.cancel()

        asyncio.create_task(_enforce_session_limit())

        # Kick off the conversation so the bot greets first.
        context.add_message(
            {"role": "developer", "content": "Greet the caller and introduce yourself."}
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Caller disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Entry point used by the Pipecat runner."""
    transport_params = {
        # SmallWebRTC (peer-to-peer, no third-party account needed) - our free path.
        # Daily transport can be re-added later for phone/cloud (needs `pip install
        # pipecat-ai[daily]` + a Daily account).
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    }

    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
