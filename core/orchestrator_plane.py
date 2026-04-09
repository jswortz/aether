import subprocess
import logging
import os
import json
from typing import Dict, Any, Optional
from evals.judge_scoring import Judge

class OrchestratorPlane:
    """
    The Orchestrator Plane manages the lifecycle of ephemeral Cloud Run workers.
    It handles provisioning, scaling, and teardown of specialized agent instances.
    """

    def __init__(self, project_id: Optional[str] = None, region: str = "us-central1", judge: Optional[Judge] = None):
        self.project_id = project_id or os.getenv("PROJECT_ID")
        self.region = region or os.getenv("REGION", "us-central1")
        self.judge = judge or Judge()
        self.logger = logging.getLogger("aether.core.orchestrator")
        
        if not self.project_id:
            try:
                self.project_id = subprocess.check_output(
                    ["gcloud", "config", "get-value", "project"],
                    text=True
                ).strip()
            except Exception:
                self.logger.warning("Could not determine PROJECT_ID from gcloud. Please set it manually.")

    def provision_worker(self, worker_name: str, image_tag: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Spins up an ephemeral Cloud Run instance for a specific worker.
        """
        self.logger.info(f"Provisioning ephemeral worker: {worker_name}")
        
        cmd = [
            "gcloud", "run", "deploy", worker_name,
            "--image", image_tag,
            "--platform", "managed",
            "--region", self.region,
            "--no-allow-unauthenticated",
            "--memory", "2Gi",
            "--cpu", "1",
            "--format", "json"
        ]

        if env_vars:
            env_str = ",".join([f"{k}={v}" for k, v in env_vars.items()])
            cmd.extend(["--set-env-vars", env_str])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            deployment_info = json.loads(result.stdout)
            url = deployment_info.get("status", {}).get("url")
            self.logger.info(f"Worker {worker_name} provisioned at {url}")
            return {
                "status": "success",
                "worker_name": worker_name,
                "url": url,
                "deployment_info": deployment_info
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to provision worker {worker_name}: {e.stderr}")
            return {
                "status": "error",
                "error": e.stderr
            }

    def teardown_worker(self, worker_name: str) -> bool:
        """
        Deletes the ephemeral Cloud Run worker.
        """
        self.logger.info(f"Tearing down worker: {worker_name}")
        cmd = [
            "gcloud", "run", "services", "delete", worker_name,
            "--platform", "managed",
            "--region", self.region,
            "--quiet"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            self.logger.info(f"Worker {worker_name} deleted.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to delete worker {worker_name}: {e.stderr}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example:
    # plane = OrchestratorPlane()
    # plane.provision_worker("ephemeral-worker-v1", "gcr.io/my-project/aether-base:latest")
