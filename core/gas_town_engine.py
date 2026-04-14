import time
import logging
import json
import os
import subprocess
from typing import Dict, Any, List, Optional
from evals.judge_scoring import Judge

class GasTownEngine:
    """
    The Gas Town Engine implements a continuous execution protocol inspired by
    Steve Yegge's Gas Town. It uses micro-epochs and state checkpointing to GCS
    to ensure that the agent process is effectively immortal and resumable.
    """

    def __init__(self, state_bucket: str, session_id: str, judge: Optional[Judge] = None):
        self.state_bucket = state_bucket.replace("gs://", "")
        self.session_id = session_id
        self.judge = judge or Judge()
        self.state_file = f"state/{session_id}/engine_state.json"
        
        from google.cloud import storage
        try:
            self.storage_client = storage.Client()
        except:
            # Fallback if no credentials or default project is missing, helpful for local testing
            self.storage_client = None

        self.state = {
            "epoch": 0,
            "session_id": session_id,
            "history": [],
            "status": "initialized",
            "last_checkpoint": None
        }
        self.logger = logging.getLogger("aether.core.gastown")
        logging.basicConfig(level=logging.INFO)

    def _gsutil_cmd(self, cmd: List[str]):
        # DEPRECATED/REMOVED: using google.cloud.storage instead
        pass

    def checkpoint(self):
        """
        Saves the current engine state to GCS.
        """
        self.state["last_checkpoint"] = time.time()
        
        self.logger.info(f"Checkpointing state to gs://{self.state_bucket}/{self.state_file}")
        
        if not self.storage_client:
            self.logger.warning("No GCS client available. Checkpoint skipped.")
            return False
            
        try:
            bucket = self.storage_client.bucket(self.state_bucket)
            blob = bucket.blob(self.state_file)
            blob.upload_from_string(json.dumps(self.state), content_type="application/json")
            self.logger.info("Checkpoint successful.")
            return True
        except Exception as e:
            self.logger.error(f"GCS checkpoint failed: {e}")
            return False

    def resurrect(self) -> bool:
        """
        Loads the engine state from GCS, effectively resurrecting the session.
        """
        self.logger.info(f"Attempting resurrection from gs://{self.state_bucket}/{self.state_file}")
        
        if not self.storage_client:
            self.logger.warning("No GCS client available. Resurrection skipped.")
            return False
            
        try:
            bucket = self.storage_client.bucket(self.state_bucket)
            blob = bucket.blob(self.state_file)
            if blob.exists():
                data = blob.download_as_string()
                self.state = json.loads(data)
                self.logger.info(f"Resurrection complete. Resuming from epoch {self.state['epoch']}")
                return True
        except Exception as e:
            self.logger.error(f"Resurrection failed: {e}")
        
        self.logger.warning("Resurrection failed or no previous state found. Starting fresh.")
        return False

    def run_micro_epoch(self, step_fn, *args, **kwargs):
        """
        Executes a single micro-epoch.
        A micro-epoch is a discrete unit of work followed by a state checkpoint.
        """
        self.state["epoch"] += 1
        epoch_id = self.state["epoch"]
        self.logger.info(f"--- Starting Micro-Epoch {epoch_id} ---")
        
        try:
            result = step_fn(*args, **kwargs)
            self.state["history"].append({
                "epoch": epoch_id,
                "timestamp": time.time(),
                "result": result,
                "status": "success"
            })
            self.state["status"] = "running"
        except Exception as e:
            self.logger.error(f"Error in epoch {epoch_id}: {e}")
            self.state["history"].append({
                "epoch": epoch_id,
                "timestamp": time.time(),
                "error": str(e),
                "status": "failed"
            })
            self.state["status"] = "error"
            raise e
        finally:
            self.checkpoint()
            
        return result

    def continuous_run(self, task_generator):
        """
        Runs the engine continuously, pulling tasks and executing them in micro-epochs.
        """
        self.resurrect()
        
        for task in task_generator:
            self.run_micro_epoch(self.execute_task, task)

    def execute_task(self, task: str):
        # Placeholder for actual task execution logic, 
        # likely integrating with HeadlessGeminiRunner
        self.logger.info(f"Executing task: {task}")
        return f"Completed task: {task}"

if __name__ == "__main__":
    # Example usage:
    # engine = GasTownEngine(state_bucket="aether-persistent-state", session_id="session-123")
    # engine.run_micro_epoch(print, "Hello Gas Town")
    pass
