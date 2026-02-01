"""Message queue for ship updates using asyncio.Queue."""
import asyncio
import logging
from typing import Dict, Any, Optional
from collections import deque

logger = logging.getLogger(__name__)


class MessageQueue:
    """In-memory message queue for ship updates (can be extended to Redis/RabbitMQ)."""
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize message queue.
        
        Args:
            max_size: Maximum queue size (backpressure)
        """
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._subscribers: set = set()
        self._running = False
        self._broadcast_task: Optional[asyncio.Task] = None
    
    async def publish(self, message: Dict[str, Any]) -> bool:
        """
        Publish message to queue.
        
        Args:
            message: Message dictionary
            
        Returns:
            True if published, False if queue full
        """
        try:
            await self._queue.put(message)
            return True
        except asyncio.QueueFull:
            logger.warning("Message queue full, dropping message")
            return False
    
    def subscribe(self, callback):
        """
        Subscribe to messages.
        
        Args:
            callback: Async function to call with messages
        """
        self._subscribers.add(callback)
        logger.info(f"New subscriber added. Total: {len(self._subscribers)}")
    
    def unsubscribe(self, callback):
        """Remove subscriber."""
        self._subscribers.discard(callback)
        logger.info(f"Subscriber removed. Total: {len(self._subscribers)}")
    
    async def _broadcast_loop(self):
        """Broadcast messages to all subscribers."""
        while self._running:
            try:
                # Wait for message with timeout
                try:
                    message = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Broadcast to all subscribers
                if self._subscribers:
                    tasks = [
                        callback(message)
                        for callback in list(self._subscribers)
                    ]
                    # Run all callbacks in parallel
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                self._queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("Message queue broadcast loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in message queue broadcast: {e}", exc_info=True)
    
    def start(self):
        """Start the broadcast loop."""
        if not self._running:
            self._running = True
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())
            logger.info("Message queue started")
    
    async def stop(self):
        """Stop the broadcast loop."""
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        logger.info("Message queue stopped")


# Global message queue instance
message_queue = MessageQueue(max_size=10000)
