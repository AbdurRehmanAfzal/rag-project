"""Branded web server for the Voice Property Concierge.

Serves a custom, Abdur Rehman Afzal-branded UI at `/` and the SmallWebRTC
signaling endpoint at `/api/offer`, reusing the exact pipeline defined in
bot.py. This replaces the generic Pipecat prebuilt client for a friendly,
portfolio-ready experience (and is the same setup we deploy in Milestone 5).

Run:  python server.py      then open  http://localhost:7860
(bot.py still works on its own with the plain prebuilt client if you want it.)
"""

import os

import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from pipecat.runner.types import SmallWebRTCRunnerArguments
from pipecat.transports.smallwebrtc.request_handler import (
    SmallWebRTCPatchRequest,
    SmallWebRTCRequest,
    SmallWebRTCRequestHandler,
)

import bot as bot_module

app = FastAPI(title="Voice Property Concierge")

# Handles WebRTC peer connections (SDP offer/answer + ICE), same component the
# Pipecat dev runner uses internally.
_webrtc = SmallWebRTCRequestHandler()


@app.post("/api/offer")
async def offer(request: SmallWebRTCRequest, background_tasks: BackgroundTasks):
    """Browser posts its SDP offer here; we spin up the bot on connect."""

    async def _on_connection(connection):
        # SmallWebRTCRunnerArguments.__post_init__ sets handle_sigint=False,
        # so this is safe to run from a background task (no main-thread signals).
        runner_args = SmallWebRTCRunnerArguments(webrtc_connection=connection)
        background_tasks.add_task(bot_module.bot, runner_args)

    return await _webrtc.handle_web_request(
        request=request, webrtc_connection_callback=_on_connection
    )


@app.patch("/api/offer")
async def ice_candidate(request: SmallWebRTCPatchRequest):
    """Trickle ICE candidates from the browser."""
    await _webrtc.handle_patch_request(request)
    return {"status": "success"}


# Serve the branded client. Mounted last so the /api routes above win.
_client_dir = os.path.join(os.path.dirname(__file__), "client")
app.mount("/", StaticFiles(directory=_client_dir, html=True), name="client")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"🎙️  Voice concierge UI ready → http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
