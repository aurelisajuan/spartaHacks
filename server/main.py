import json
import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from concurrent.futures import TimeoutError as ConnectionTimeoutError
from retell import Retell
# from custom_types import (
#     ConfigResponse,
#     ResponseRequiredRequest,
# )
# from typing import Optional
# from socket_manager import manager

