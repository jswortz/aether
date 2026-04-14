from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ExpertConfig(BaseModel):
    expert_name: str = Field(..., description="The name or role of the expert (e.g., 'Distillation Engineer').")
    model: str = Field(..., description="The model assigned to this expert (e.g., 'gemini-3.0-ultra', 'gemma-4-local').")
    prompt_template: str = Field(..., description="System instructions for this expert's role.")

class SkillData(BaseModel):
    skill_paths: List[str] = Field(..., description="Local paths to skills directories to use as knowledge.")
    extraction_strategy: str = Field(default="full_context", description="How to extract data from skills (e.g., 'full_context', 'summarized', 'qa_pairs').")

class MixtureOfExperts(BaseModel):
    orchestration_type: str = Field(default="sequential", description="How to route between experts (e.g., 'sequential', 'debate', 'router').")
    experts: List[ExpertConfig]

class OutcomeSolution(BaseModel):
    output_format: str = Field(..., description="Expected output format (e.g., 'jsonl', 'markdown').")
    storage_destination: str = Field(..., description="Where the outcome is saved.")
    persistance_strategy: str = Field(default="gcs_checkpoint", description="Ties into Gas Town persistence mechanisms.")

class EvaluationMetric(BaseModel):
    metric_name: str = Field(..., description="Name of the metric (e.g., 'ragas_faithfulness', 'code_validity').")
    target_score: float = Field(..., description="Threshold score to pass.")
    evaluator_model: str = Field(default="gemini-3.0-ultra", description="The model executing the LLM-as-a-judge.")

class Evidence(BaseModel):
    source: str = Field(..., description="Source of the evidence (e.g., 'eval_run_v1', 'skill_corpus').")
    data_payload: Dict[str, Any] = Field(..., description="The empirical data, metrics, or logs collected.")
    confidence_score: float = Field(default=1.0, description="Confidence metric for the evidence.")

class Hypothesis(BaseModel):
    statement: str = Field(..., description="The core hypothesis being tested by this Swarm or Recipe.")
    falsifiability_criteria: str = Field(..., description="Conditions determining how to prove this hypothesis wrong.")

class Goal(BaseModel):
    objective: str = Field(..., description="The primary goal or outcome objective.")
    success_criteria: List[str] = Field(..., description="Measurable criteria indicating goal achievement.")

class ContextKnowledge(BaseModel):
    background_info: str = Field(..., description="Context, foundational knowledge, or environmental state.")
    constraints: List[str] = Field(default_factory=list, description="Known system, systemic or API constraints.")

class ExperimentTest(BaseModel):
    test_name: str = Field(..., description="The name of the experiment or test suite.")
    methodology: str = Field(..., description="How the test or experiment is to be executed in the environment.")
    expected_result: str = Field(..., description="The predicted manifestation from the swarm.")
    linked_hypothesis: Optional[str] = Field(None, description="Hypothesis this experiment intends to validate.")

class Recipe(BaseModel):
    """
    Aether Recipe
    A codified document describing a Mixture of Experts (MoE), local skill data ingestion, 
    outcome expectations, and a continuous evaluation loop for training and routing.
    Also serves as an epistemic artifact tracking hypothesis, goals, context and evidence.
    """
    recipe_name: str
    description: str
    goals: List[Goal] = Field(default_factory=list, description="Objectives driving the recipe.")
    context_knowledge: Optional[ContextKnowledge] = Field(None, description="Background info informing the creation.")
    hypothesis: Optional[Hypothesis] = Field(None, description="Emergent properties or behaviors to test.")
    skills_data: SkillData
    moe: MixtureOfExperts
    outcome: OutcomeSolution
    experiments: List[ExperimentTest] = Field(default_factory=list, description="Tests designed to validate the hypothesis.")
    evaluation: List[EvaluationMetric]
    evidence: List[Evidence] = Field(default_factory=list, description="Data points confirming or denying the hypothesis.")
