"""
Main Entrypoint for Family Evolution System
Starts the FastAPI web server, background scheduler, and Telegram bot.
"""
import sys
import uvicorn
import logging
from core.config import config
from data.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("family_evolution")

def main():
    logger.info("Initializing Family Evolution Database...")
    init_db(seed_defaults=True)
    
    logger.info(f"Starting Family Evolution Web Dashboard on http://{config.web_host}:{config.web_port}")
    uvicorn.run(
        "api.app:app",
        host=config.web_host,
        port=config.web_port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
