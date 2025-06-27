#!/usr/bin/env python3
"""
Standalone Queue Worker for Blood Test Analysis
Run this as a separate process to handle queued analysis jobs
"""

import asyncio
import logging
import signal
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkerManager:
    """Manages queue worker lifecycle"""
    
    def __init__(self):
        self.workers = []
        self.running = False
        self.num_workers = int(os.getenv('WORKER_COUNT', '2'))
    
    async def start_workers(self):
        """Start multiple worker processes"""
        logger.info(f"Starting {self.num_workers} worker processes...")
        
        try:
            from queue_worker import BloodTestWorker, QueueManager
            
            # Create queue manager
            queue_manager = QueueManager()
            
            # Start workers
            for i in range(self.num_workers):
                worker = BloodTestWorker(queue_manager)
                worker_task = asyncio.create_task(worker.run())
                self.workers.append((worker, worker_task))
                logger.info(f"Worker {i+1} started")
            
            self.running = True
            logger.info(f"All {self.num_workers} workers started successfully")
            
            # Wait for all workers
            await asyncio.gather(*[task for _, task in self.workers])
            
        except ImportError as e:
            logger.error(f"Failed to import queue system: {e}")
            logger.error("Make sure Redis is available and requirements are installed")
            return False
        except Exception as e:
            logger.error(f"Failed to start workers: {e}")
            return False
    
    def stop_workers(self):
        """Stop all worker processes"""
        logger.info("Stopping workers...")
        
        for worker, task in self.workers:
            worker.stop()
            task.cancel()
        
        self.running = False
        logger.info("All workers stopped")

def signal_handler(worker_manager):
    """Handle shutdown signals"""
    def handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        worker_manager.stop_workers()
        sys.exit(0)
    return handler

async def main():
    """Main worker process"""
    logger.info("🔄 Blood Test Analysis Worker Starting...")
    
    # Create worker manager
    worker_manager = WorkerManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler(worker_manager))
    signal.signal(signal.SIGTERM, signal_handler(worker_manager))
    
    try:
        # Start workers
        await worker_manager.start_workers()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Worker process error: {e}")
    finally:
        worker_manager.stop_workers()
        logger.info("Worker process shutdown complete")

if __name__ == "__main__":
    print("🔄 Blood Test Analysis Queue Worker")
    print("📊 Processing queued analysis jobs...")
    print("🛑 Press Ctrl+C to stop")
    print("")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Worker stopped by user")
    except Exception as e:
        print(f"\n❌ Worker failed: {e}")
        sys.exit(1) 