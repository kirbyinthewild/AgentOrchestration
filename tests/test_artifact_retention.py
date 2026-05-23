import pytest
from src.orchestrator.workflow import WorkflowManager, WorkflowStep, StepStatus
from src.orchestrator.validator import ArtifactRetentionValidator, CleanupSchedule

class TestArtifactRetention:
    def setup_method(self):
        self.manager = WorkflowManager()

    def test_valid_retention_policy(self):
        workflow = self.manager.create_workflow("test")
        policy = {"retention_days": 7, "schedule": "daily"}
        step = WorkflowStep("step1", lambda: "ok", retention_policy=policy)
        workflow.add_step(step)
        
        assert self.manager.execute_workflow(workflow.id) is True
        assert workflow.status == StepStatus.COMPLETED

    def test_invalid_retention_days(self):
        workflow = self.manager.create_workflow("test")
        policy = {"retention_days": -1, "schedule": "daily"}
        step = WorkflowStep("step1", lambda: "ok", retention_policy=policy)
        workflow.add_step(step)
        
        # This should fail during pre-dispatch validation
        assert self.manager.execute_workflow(workflow.id) is False
        assert workflow.status == StepStatus.FAILED

    def test_invalid_schedule(self):
        workflow = self.manager.create_workflow("test")
        policy = {"retention_days": 7, "schedule": "invalid"}
        step = WorkflowStep("step1", lambda: "ok", retention_policy=policy)
        workflow.add_step(step)
        
        assert self.manager.execute_workflow(workflow.id) is False
        assert workflow.status == StepStatus.FAILED

    def test_stale_policy(self):
        from datetime import datetime, timedelta
        workflow = self.manager.create_workflow("test")
        # 2 years ago
        stale_date = datetime.now() - timedelta(days=730)
        policy = {"retention_days": 7, "schedule": "daily", "created_at": stale_date}
        step = WorkflowStep("step1", lambda: "ok", retention_policy=policy)
        workflow.add_step(step)
        
        assert self.manager.execute_workflow(workflow.id) is False
        assert workflow.status == StepStatus.FAILED

    def test_missing_policy_is_valid(self):
        workflow = self.manager.create_workflow("test")
        step = WorkflowStep("step1", lambda: "ok")
        workflow.add_step(step)
        
        assert self.manager.execute_workflow(workflow.id) is True
        assert workflow.status == StepStatus.COMPLETED
