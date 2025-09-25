"""
Execution Monitor for real-time tracking and metrics collection.

Monitors parallel execution progress, collects performance metrics,
and provides real-time visibility into execution status and health.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

from ..models.execution_graph import ExecutionGraph
from ..models.result_models import TaskResult


@dataclass
class ExecutionMetrics:
    """Real-time execution metrics"""
    session_id: str
    start_time: datetime
    current_time: datetime = field(default_factory=datetime.now)
    elapsed_time_seconds: float = 0.0

    # Task metrics
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    running_tasks: int = 0
    pending_tasks: int = 0

    # Performance metrics
    tasks_per_minute: float = 0.0
    average_task_duration: float = 0.0
    completion_rate: float = 0.0

    # Resource metrics
    active_agents: int = 0
    agent_utilization: float = 0.0

    # Quality metrics
    quality_score: float = 0.0
    quality_gates_passed: int = 0
    quality_gates_failed: int = 0


@dataclass
class SessionMonitoringData:
    """Monitoring data for an execution session"""
    session_id: str
    execution_graph: ExecutionGraph
    start_time: datetime
    metrics_history: deque = field(default_factory=lambda: deque(maxlen=100))
    task_timelines: Dict[str, Dict[str, datetime]] = field(default_factory=dict)
    agent_assignments: Dict[str, str] = field(default_factory=dict)  # task_id -> agent_id
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True


class ExecutionMonitorError(Exception):
    """Exception raised during execution monitoring"""
    pass


class ExecutionMonitor:
    """
    Real-time execution monitor for parallel task execution.

    Provides comprehensive monitoring, metrics collection, alerting,
    and real-time visibility into execution progress and performance.
    """

    def __init__(
        self,
        metrics_collection_interval: float = 5.0,
        alert_thresholds: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution monitor.

        Args:
            metrics_collection_interval: Interval for metrics collection (seconds)
            alert_thresholds: Thresholds for generating alerts
        """
        self.metrics_interval = metrics_collection_interval
        self.alert_thresholds = alert_thresholds or self._get_default_alert_thresholds()
        self.logger = logging.getLogger("execution.monitor")

        # Monitoring state
        self.active_sessions: Dict[str, SessionMonitoringData] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.alert_callbacks: List[Callable] = []

        # Performance tracking
        self.global_metrics = {
            "total_sessions": 0,
            "successful_sessions": 0,
            "failed_sessions": 0,
            "total_tasks_executed": 0,
            "average_session_duration": 0.0
        }

    async def start_session_monitoring(self, session) -> None:
        """
        Start monitoring an execution session.

        Args:
            session: ExecutionSession to monitor
        """
        try:
            self.logger.info(f"Starting monitoring for session {session.session_id}")

            # Create monitoring data
            monitoring_data = SessionMonitoringData(
                session_id=session.session_id,
                execution_graph=session.execution_graph,
                start_time=session.start_time
            )

            self.active_sessions[session.session_id] = monitoring_data

            # Start monitoring task
            monitoring_task = asyncio.create_task(
                self._monitor_session_loop(monitoring_data)
            )
            self.monitoring_tasks[session.session_id] = monitoring_task

            # Update global metrics
            self.global_metrics["total_sessions"] += 1

            self.logger.info(f"Monitoring started for session {session.session_id}")

        except Exception as e:
            self.logger.error(f"Failed to start monitoring for session {session.session_id}: {e}")
            raise ExecutionMonitorError(f"Failed to start session monitoring: {str(e)}")

    async def stop_session_monitoring(self, session_id: str) -> None:
        """
        Stop monitoring an execution session.

        Args:
            session_id: Session to stop monitoring
        """
        try:
            if session_id in self.monitoring_tasks:
                # Cancel monitoring task
                monitoring_task = self.monitoring_tasks[session_id]
                monitoring_task.cancel()

                try:
                    await monitoring_task
                except asyncio.CancelledError:
                    pass

                del self.monitoring_tasks[session_id]

            if session_id in self.active_sessions:
                # Mark session as inactive
                self.active_sessions[session_id].is_active = False

                # Archive monitoring data (simplified - in practice might store to database)
                archived_data = self.active_sessions[session_id]

                # Calculate final session metrics
                await self._finalize_session_metrics(archived_data)

                del self.active_sessions[session_id]

            self.logger.info(f"Monitoring stopped for session {session_id}")

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring for session {session_id}: {e}")

    async def record_task_event(
        self,
        session_id: str,
        task_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a task event for monitoring.

        Args:
            session_id: Session ID
            task_id: Task ID
            event_type: Type of event (started, completed, failed, etc.)
            event_data: Additional event data
        """
        if session_id not in self.active_sessions:
            return

        monitoring_data = self.active_sessions[session_id]
        current_time = datetime.now()

        # Update task timeline
        if task_id not in monitoring_data.task_timelines:
            monitoring_data.task_timelines[task_id] = {}

        monitoring_data.task_timelines[task_id][event_type] = current_time

        # Record agent assignment if provided
        if event_data and "agent_id" in event_data:
            monitoring_data.agent_assignments[task_id] = event_data["agent_id"]

        # Check for alerts based on event
        await self._check_task_event_alerts(session_id, task_id, event_type, event_data)

        self.logger.debug(f"Recorded {event_type} event for task {task_id} in session {session_id}")

    async def get_session_metrics(self, session_id: str) -> Optional[ExecutionMetrics]:
        """
        Get current metrics for a session.

        Args:
            session_id: Session to get metrics for

        Returns:
            ExecutionMetrics: Current session metrics or None
        """
        if session_id not in self.active_sessions:
            return None

        monitoring_data = self.active_sessions[session_id]
        return await self._calculate_current_metrics(monitoring_data)

    async def get_global_metrics(self) -> Dict[str, Any]:
        """Get global monitoring metrics."""
        return self.global_metrics.copy()

    async def get_session_alerts(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get alerts for a session.

        Args:
            session_id: Session to get alerts for

        Returns:
            List[Dict[str, Any]]: List of active alerts
        """
        if session_id not in self.active_sessions:
            return []

        return self.active_sessions[session_id].alerts.copy()

    async def register_alert_callback(self, callback: Callable) -> None:
        """Register callback for alerts."""
        self.alert_callbacks.append(callback)

    async def get_execution_timeline(self, session_id: str) -> Dict[str, Any]:
        """
        Get execution timeline for a session.

        Args:
            session_id: Session to get timeline for

        Returns:
            Dict[str, Any]: Execution timeline data
        """
        if session_id not in self.active_sessions:
            return {}

        monitoring_data = self.active_sessions[session_id]

        timeline = {
            "session_id": session_id,
            "start_time": monitoring_data.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "tasks": {}
        }

        for task_id, events in monitoring_data.task_timelines.items():
            timeline["tasks"][task_id] = {
                "agent_id": monitoring_data.agent_assignments.get(task_id),
                "events": {event_type: timestamp.isoformat() for event_type, timestamp in events.items()}
            }

        return timeline

    async def _monitor_session_loop(self, monitoring_data: SessionMonitoringData) -> None:
        """Main monitoring loop for a session."""
        try:
            while monitoring_data.is_active:
                # Calculate current metrics
                metrics = await self._calculate_current_metrics(monitoring_data)

                # Store metrics in history
                monitoring_data.metrics_history.append(metrics)

                # Check for alerts
                await self._check_metrics_alerts(monitoring_data, metrics)

                # Wait for next collection interval
                await asyncio.sleep(self.metrics_interval)

        except asyncio.CancelledError:
            self.logger.info(f"Monitoring cancelled for session {monitoring_data.session_id}")
        except Exception as e:
            self.logger.error(f"Monitoring loop error for session {monitoring_data.session_id}: {e}")

    async def _calculate_current_metrics(self, monitoring_data: SessionMonitoringData) -> ExecutionMetrics:
        """Calculate current execution metrics for a session."""
        current_time = datetime.now()
        elapsed_time = (current_time - monitoring_data.start_time).total_seconds()

        # Count task states
        completed_count = 0
        failed_count = 0
        running_count = 0

        for task_id, events in monitoring_data.task_timelines.items():
            if "completed" in events:
                completed_count += 1
            elif "failed" in events:
                failed_count += 1
            elif "started" in events and "completed" not in events and "failed" not in events:
                running_count += 1

        total_tasks = monitoring_data.execution_graph.total_tasks
        pending_count = total_tasks - completed_count - failed_count - running_count

        # Calculate rates
        tasks_per_minute = (completed_count / elapsed_time * 60) if elapsed_time > 0 else 0
        completion_rate = (completed_count / total_tasks) if total_tasks > 0 else 0

        # Calculate average task duration
        task_durations = []
        for task_id, events in monitoring_data.task_timelines.items():
            if "started" in events and "completed" in events:
                duration = (events["completed"] - events["started"]).total_seconds()
                task_durations.append(duration)

        average_task_duration = sum(task_durations) / len(task_durations) if task_durations else 0

        # Calculate agent utilization (simplified)
        active_agents = len(set(monitoring_data.agent_assignments.values()))
        agent_utilization = (running_count / active_agents) if active_agents > 0 else 0

        # Calculate quality metrics (simplified)
        quality_score = 0.85  # Would calculate from actual quality results
        quality_gates_passed = completed_count  # Simplified
        quality_gates_failed = failed_count

        return ExecutionMetrics(
            session_id=monitoring_data.session_id,
            start_time=monitoring_data.start_time,
            current_time=current_time,
            elapsed_time_seconds=elapsed_time,
            total_tasks=total_tasks,
            completed_tasks=completed_count,
            failed_tasks=failed_count,
            running_tasks=running_count,
            pending_tasks=pending_count,
            tasks_per_minute=tasks_per_minute,
            average_task_duration=average_task_duration,
            completion_rate=completion_rate,
            active_agents=active_agents,
            agent_utilization=agent_utilization,
            quality_score=quality_score,
            quality_gates_passed=quality_gates_passed,
            quality_gates_failed=quality_gates_failed
        )

    async def _check_task_event_alerts(
        self,
        session_id: str,
        task_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]]
    ) -> None:
        """Check for alerts based on task events."""
        monitoring_data = self.active_sessions[session_id]

        # Check for task failure alerts
        if event_type == "failed":
            alert = {
                "type": "task_failure",
                "severity": "high",
                "message": f"Task {task_id} failed",
                "timestamp": datetime.now().isoformat(),
                "data": event_data
            }
            monitoring_data.alerts.append(alert)
            await self._fire_alert(alert)

        # Check for long-running task alerts
        if event_type == "started":
            # Schedule check for long-running task
            asyncio.create_task(
                self._check_long_running_task(session_id, task_id, event_data)
            )

    async def _check_metrics_alerts(
        self,
        monitoring_data: SessionMonitoringData,
        metrics: ExecutionMetrics
    ) -> None:
        """Check for alerts based on metrics."""
        alerts_to_fire = []

        # Check completion rate alert
        if metrics.completion_rate < self.alert_thresholds["min_completion_rate"]:
            if metrics.elapsed_time_seconds > 300:  # 5 minutes minimum
                alert = {
                    "type": "low_completion_rate",
                    "severity": "medium",
                    "message": f"Completion rate {metrics.completion_rate:.1%} below threshold",
                    "timestamp": datetime.now().isoformat(),
                    "data": {"completion_rate": metrics.completion_rate}
                }
                monitoring_data.alerts.append(alert)
                alerts_to_fire.append(alert)

        # Check failure rate alert
        if metrics.total_tasks > 0:
            failure_rate = metrics.failed_tasks / metrics.total_tasks
            if failure_rate > self.alert_thresholds["max_failure_rate"]:
                alert = {
                    "type": "high_failure_rate",
                    "severity": "high",
                    "message": f"Failure rate {failure_rate:.1%} exceeds threshold",
                    "timestamp": datetime.now().isoformat(),
                    "data": {"failure_rate": failure_rate}
                }
                monitoring_data.alerts.append(alert)
                alerts_to_fire.append(alert)

        # Check agent utilization alert
        if metrics.agent_utilization < self.alert_thresholds["min_agent_utilization"]:
            if metrics.active_agents > 0:
                alert = {
                    "type": "low_agent_utilization",
                    "severity": "medium",
                    "message": f"Agent utilization {metrics.agent_utilization:.1%} below threshold",
                    "timestamp": datetime.now().isoformat(),
                    "data": {"utilization": metrics.agent_utilization}
                }
                monitoring_data.alerts.append(alert)
                alerts_to_fire.append(alert)

        # Fire alerts
        for alert in alerts_to_fire:
            await self._fire_alert(alert)

    async def _check_long_running_task(
        self,
        session_id: str,
        task_id: str,
        event_data: Optional[Dict[str, Any]]
    ) -> None:
        """Check for long-running task after threshold time."""
        # Wait for threshold time
        await asyncio.sleep(self.alert_thresholds["max_task_duration_seconds"])

        # Check if task is still running
        if session_id in self.active_sessions:
            monitoring_data = self.active_sessions[session_id]
            task_events = monitoring_data.task_timelines.get(task_id, {})

            if "started" in task_events and "completed" not in task_events and "failed" not in task_events:
                duration = (datetime.now() - task_events["started"]).total_seconds()
                alert = {
                    "type": "long_running_task",
                    "severity": "medium",
                    "message": f"Task {task_id} running for {duration:.1f} seconds",
                    "timestamp": datetime.now().isoformat(),
                    "data": {"duration": duration, "task_id": task_id}
                }
                monitoring_data.alerts.append(alert)
                await self._fire_alert(alert)

    async def _fire_alert(self, alert: Dict[str, Any]) -> None:
        """Fire alert to registered callbacks."""
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")

        self.logger.warning(f"ALERT [{alert['severity']}]: {alert['message']}")

    async def _finalize_session_metrics(self, monitoring_data: SessionMonitoringData) -> None:
        """Finalize metrics when session ends."""
        final_metrics = await self._calculate_current_metrics(monitoring_data)

        # Update global metrics
        if final_metrics.completion_rate >= 0.8:  # 80% completion considered successful
            self.global_metrics["successful_sessions"] += 1
        else:
            self.global_metrics["failed_sessions"] += 1

        self.global_metrics["total_tasks_executed"] += final_metrics.completed_tasks

        # Update average session duration
        total_sessions = self.global_metrics["total_sessions"]
        current_avg = self.global_metrics["average_session_duration"]
        new_duration = final_metrics.elapsed_time_seconds

        self.global_metrics["average_session_duration"] = (
            (current_avg * (total_sessions - 1) + new_duration) / total_sessions
        )

    def _get_default_alert_thresholds(self) -> Dict[str, Any]:
        """Get default alert thresholds."""
        return {
            "max_task_duration_seconds": 1800,  # 30 minutes
            "max_failure_rate": 0.2,            # 20% failure rate
            "min_completion_rate": 0.3,         # 30% completion rate
            "min_agent_utilization": 0.5,       # 50% agent utilization
            "max_session_duration_hours": 8     # 8 hours
        }