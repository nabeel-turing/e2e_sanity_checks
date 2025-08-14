# APIs/clock/tests/test_timer_api.py

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..TimerApi import (
    create_timer,
    show_matching_timers,
    modify_timer_v2,
    modify_timer,
    change_timer_state
)
from ..SimulationEngine.db import DB
from ..SimulationEngine.custom_errors import *


class TestCreateTimer:
    def setup_method(self):
        """Reset DB before each test"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_create_timer_with_duration(self):
        """Test creating a timer with duration"""
        result = create_timer(duration="25m", label="Pomodoro")
        
        assert "message" in result
        assert "timer" in result
        assert len(result["timer"]) == 1
        
        timer = result["timer"][0]
        assert timer["label"] == "Pomodoro"
        assert timer["state"] == "RUNNING"
        assert timer["original_duration"] == "25m"
        assert "TIMER-1" in timer["timer_id"]

    def test_create_timer_with_time(self):
        """Test creating a timer for specific time"""
        result = create_timer(time="3:30 PM", label="Meeting reminder")
        
        assert "message" in result
        assert "timer" in result
        assert len(result["timer"]) == 1
        
        timer = result["timer"][0]
        assert timer["label"] == "Meeting reminder"
        assert timer["state"] == "RUNNING"

    def test_create_timer_no_duration_no_time(self):
        """Test error when neither duration nor time provided"""
        with pytest.raises(ValueError, match="Either duration or time must be provided"):
            create_timer(label="Invalid timer")

    def test_create_timer_invalid_duration(self):
        """Test error with invalid duration format"""
        with pytest.raises(ValueError, match="Invalid duration format"):
            create_timer(duration="invalid_duration")

    def test_create_timer_invalid_time(self):
        """Test error with invalid time format"""
        with pytest.raises(ValueError, match="Invalid time format"):
            create_timer(time="invalid_time")

    def test_create_timer_type_validation(self):
        """Test type validation for parameters"""
        with pytest.raises(TypeError):
            create_timer(duration=123)  # Should be string
        
        with pytest.raises(TypeError):
            create_timer(time="3:00 PM", label=123)  # Should be string


class TestShowMatchingTimers:
    def setup_method(self):
        """Reset DB and add sample timers"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {
                "TIMER-1": {
                    "timer_id": "TIMER-1",
                    "original_duration": "25m",
                    "remaining_duration": "18m30s",
                    "time_of_day": "2:45 PM",
                    "label": "Pomodoro session",
                    "state": "RUNNING",
                    "created_at": "2024-01-15T14:20:00",
                    "fire_time": "2024-01-15T14:45:00",
                    "start_time": "2024-01-15T14:20:00"
                },
                "TIMER-2": {
                    "timer_id": "TIMER-2",
                    "original_duration": "10m",
                    "remaining_duration": "10m",
                    "time_of_day": "3:10 PM",
                    "label": "Tea brewing",
                    "state": "PAUSED",
                    "created_at": "2024-01-15T15:00:00",
                    "fire_time": "2024-01-15T15:10:00",
                    "start_time": "2024-01-15T15:00:00"
                }
            },
            "stopwatch": {},
            "settings": {}
        })

    def test_show_all_timers(self):
        """Test showing all timers when no filters"""
        result = show_matching_timers()
        
        assert "message" in result
        assert "timer" in result
        assert len(result["timer"]) == 2

    def test_show_timers_by_label(self):
        """Test filtering timers by label"""
        result = show_matching_timers(query="Pomodoro session")
        
        assert len(result["timer"]) == 1
        assert result["timer"][0]["label"] == "Pomodoro session"

    def test_show_timers_by_duration(self):
        """Test filtering timers by duration"""
        result = show_matching_timers(query="25m")
        
        assert len(result["timer"]) == 1
        assert result["timer"][0]["original_duration"] == "25m"

    def test_show_timers_by_state(self):
        """Test filtering timers by state"""
        result = show_matching_timers(timer_type="RUNNING")
        
        assert len(result["timer"]) == 1
        assert result["timer"][0]["state"] == "RUNNING"

    def test_show_timers_by_ids(self):
        """Test filtering timers by IDs"""
        result = show_matching_timers(timer_ids=["TIMER-1"])
        
        assert len(result["timer"]) == 1
        assert result["timer"][0]["timer_id"] == "TIMER-1"

    def test_show_timers_type_validation(self):
        """Test type validation"""
        with pytest.raises(TypeError):
            show_matching_timers(query=123)
        
        with pytest.raises(TypeError):
            show_matching_timers(timer_ids="TIMER-1")  # Should be list


class TestModifyTimerV2:
    def setup_method(self):
        """Reset DB and add sample timer"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {
                "TIMER-1": {
                    "timer_id": "TIMER-1",
                    "original_duration": "25m",
                    "remaining_duration": "18m30s",
                    "time_of_day": "2:45 PM",
                    "label": "Pomodoro session",
                    "state": "RUNNING",
                    "created_at": "2024-01-15T14:20:00",
                    "fire_time": "2024-01-15T14:45:00",
                    "start_time": "2024-01-15T14:20:00"
                }
            },
            "stopwatch": {},
            "settings": {}
        })

    def test_modify_timer_duration(self):
        """Test modifying timer duration"""
        filters = {"label": "Pomodoro session"}
        modifications = {"duration": "30m"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert "message" in result
        assert "Successfully modified" in result["message"]
        assert result["timer"][0]["original_duration"] == "30m"

    def test_modify_timer_label(self):
        """Test modifying timer label"""
        filters = {"label": "Pomodoro session"}
        modifications = {"label": "Work session"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert result["timer"][0]["label"] == "Work session"

    def test_modify_timer_add_duration(self):
        """Test adding duration to timer"""
        filters = {"label": "Pomodoro session"}
        modifications = {"duration_to_add": "5m"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert "Successfully modified" in result["message"]
        # Original 25m + 5m = 30m
        assert result["timer"][0]["original_duration"] == "30m"

    def test_modify_timer_pause(self):
        """Test pausing a timer"""
        filters = {"label": "Pomodoro session"}
        modifications = {"state_operation": "PAUSE"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert result["timer"][0]["state"] == "PAUSED"

    def test_modify_timer_resume(self):
        """Test resuming a timer"""
        # First pause the timer
        DB["timers"]["TIMER-1"]["state"] = "PAUSED"
        
        filters = {"label": "Pomodoro session"}
        modifications = {"state_operation": "RESUME"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert result["timer"][0]["state"] == "RUNNING"

    def test_modify_timer_reset(self):
        """Test resetting a timer"""
        filters = {"label": "Pomodoro session"}
        modifications = {"state_operation": "RESET"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert result["timer"][0]["state"] == "RESET"
        assert result["timer"][0]["remaining_duration"] == result["timer"][0]["original_duration"]

    def test_modify_timer_delete(self):
        """Test deleting a timer"""
        filters = {"label": "Pomodoro session"}
        modifications = {"state_operation": "DELETE"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications)
        
        assert "Successfully deleted" in result["message"]
        assert len(DB["timers"]) == 0

    def test_modify_timer_no_filters(self):
        """Test modify with no filters shows all timers"""
        result = modify_timer_v2()
        
        assert "Please specify which timer" in result["message"]
        assert len(result["timer"]) == 1

    def test_modify_timer_no_match(self):
        """Test modify with no matching timers"""
        filters = {"label": "Non-existent timer"}
        
        result = modify_timer_v2(filters=filters)
        
        assert "No matching timers found" in result["message"]
        assert len(result["timer"]) == 0

    def test_modify_timer_multiple_found(self):
        """Test modify with multiple matches asks for clarification"""
        # Add another timer
        DB["timers"]["TIMER-2"] = {
            "timer_id": "TIMER-2",
            "original_duration": "10m",
            "remaining_duration": "5m",
            "time_of_day": "3:00 PM",
            "label": "Short break",
            "state": "RUNNING",
            "created_at": "2024-01-15T15:00:00",
            "fire_time": "2024-01-15T15:10:00",
            "start_time": "2024-01-15T15:00:00"
        }
        
        filters = {"timer_type": "RUNNING"}
        
        result = modify_timer_v2(filters=filters)
        
        assert "Multiple timers found" in result["message"]
        assert len(result["timer"]) == 2

    def test_modify_timer_bulk_operation(self):
        """Test bulk modification of timers"""
        # Add another timer
        DB["timers"]["TIMER-2"] = {
            "timer_id": "TIMER-2",
            "original_duration": "10m",
            "remaining_duration": "5m",
            "time_of_day": "3:00 PM",
            "label": "Short break",
            "state": "RUNNING",
            "created_at": "2024-01-15T15:00:00",
            "fire_time": "2024-01-15T15:10:00",
            "start_time": "2024-01-15T15:00:00"
        }
        
        filters = {"timer_type": "RUNNING"}
        modifications = {"state_operation": "PAUSE"}
        
        result = modify_timer_v2(filters=filters, modifications=modifications, bulk_operation=True)
        
        assert "Successfully modified 2 timer(s)" in result["message"]
        assert all(timer["state"] == "PAUSED" for timer in result["timer"])

    def test_modify_timer_invalid_duration(self):
        """Test error with invalid duration format"""
        filters = {"label": "Pomodoro session"}
        modifications = {"duration": "invalid_duration"}
        
        with pytest.raises(ValueError, match="Invalid duration format"):
            modify_timer_v2(filters=filters, modifications=modifications)

    def test_modify_timer_invalid_state_operation(self):
        """Test error with invalid state operation"""
        filters = {"label": "Pomodoro session"}
        modifications = {"state_operation": "INVALID_OPERATION"}
        
        with pytest.raises(ValueError, match="Invalid state operation"):
            modify_timer_v2(filters=filters, modifications=modifications)

    def test_modify_timer_type_validation(self):
        """Test type validation"""
        with pytest.raises(TypeError):
            modify_timer_v2(filters="invalid")  # Should be dict
        
        with pytest.raises(TypeError):
            modify_timer_v2(modifications="invalid")  # Should be dict
        
        with pytest.raises(TypeError):
            modify_timer_v2(bulk_operation="invalid")  # Should be bool


class TestModifyTimer:
    def setup_method(self):
        """Reset DB and add sample timer"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {
                "TIMER-1": {
                    "timer_id": "TIMER-1",
                    "original_duration": "25m",
                    "remaining_duration": "18m30s",
                    "time_of_day": "2:45 PM",
                    "label": "Pomodoro session",
                    "state": "RUNNING",
                    "created_at": "2024-01-15T14:20:00",
                    "fire_time": "2024-01-15T14:45:00",
                    "start_time": "2024-01-15T14:20:00"
                }
            },
            "stopwatch": {},
            "settings": {}
        })

    def test_modify_timer_legacy_new_duration(self):
        """Test legacy modify_timer with new duration"""
        result = modify_timer(
            query="Pomodoro session",
            new_duration="30m"
        )
        
        assert "Successfully modified" in result["message"]

    def test_modify_timer_legacy_add_duration(self):
        """Test legacy modify_timer with duration to add"""
        result = modify_timer(
            query="25m",  # Find by duration
            duration_to_add="5m"
        )
        
        assert "Successfully modified" in result["message"]

    def test_modify_timer_legacy_new_label(self):
        """Test legacy modify_timer with new label"""
        result = modify_timer(
            query="Pomodoro session",
            new_label="Work session"
        )
        
        assert "Successfully modified" in result["message"]
        assert result["timer"][0]["label"] == "Work session"

    def test_modify_timer_legacy_by_type(self):
        """Test legacy modify_timer by timer type"""
        result = modify_timer(
            timer_type="RUNNING",
            new_label="Updated timer"
        )
        
        assert result["timer"][0]["label"] == "Updated timer"

    def test_modify_timer_legacy_by_ids(self):
        """Test legacy modify_timer by timer IDs"""
        result = modify_timer(
            timer_ids=["TIMER-1"],
            new_label="Updated timer"
        )
        
        assert result["timer"][0]["label"] == "Updated timer"

    def test_modify_timer_legacy_bulk_operation(self):
        """Test legacy modify_timer with bulk operation"""
        result = modify_timer(
            timer_type="RUNNING",
            new_label="Bulk updated",
            bulk_operation=True
        )
        
        assert "Successfully modified" in result["message"]


class TestChangeTimerState:
    def setup_method(self):
        """Reset DB and add sample timer"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {
                "TIMER-1": {
                    "timer_id": "TIMER-1",
                    "original_duration": "25m",
                    "remaining_duration": "18m30s",
                    "time_of_day": "2:45 PM",
                    "label": "Pomodoro session",
                    "state": "RUNNING",
                    "created_at": "2024-01-15T14:20:00",
                    "fire_time": "2024-01-15T14:45:00",
                    "start_time": "2024-01-15T14:20:00"
                }
            },
            "stopwatch": {},
            "settings": {}
        })

    def test_change_timer_state_pause(self):
        """Test pausing a timer via change_timer_state"""
        result = change_timer_state(
            timer_ids=["TIMER-1"],
            state_operation="PAUSE"
        )
        
        assert "Successfully modified" in result["message"]
        assert result["timer"][0]["state"] == "PAUSED"

    def test_change_timer_state_by_type(self):
        """Test changing timer state by type"""
        result = change_timer_state(
            timer_type="RUNNING",
            state_operation="PAUSE"
        )
        
        assert result["timer"][0]["state"] == "PAUSED"

    def test_change_timer_state_by_duration(self):
        """Test changing timer state by duration"""
        result = change_timer_state(
            duration="25m",
            state_operation="RESET"
        )
        
        assert result["timer"][0]["state"] == "RESET"

    def test_change_timer_state_by_label(self):
        """Test changing timer state by label"""
        result = change_timer_state(
            label="Pomodoro session",
            state_operation="STOP"
        )
        
        assert result["timer"][0]["state"] == "STOPPED"

    def test_change_timer_state_cancel(self):
        """Test cancelling a timer"""
        result = change_timer_state(
            timer_ids=["TIMER-1"],
            state_operation="CANCEL"
        )
        
        assert result["timer"][0]["state"] == "CANCELLED"

    def test_change_timer_state_dismiss(self):
        """Test dismissing a timer"""
        result = change_timer_state(
            timer_ids=["TIMER-1"],
            state_operation="DISMISS"
        )
        
        assert result["timer"][0]["state"] == "CANCELLED"

    def test_change_timer_state_delete(self):
        """Test deleting a timer"""
        result = change_timer_state(
            timer_ids=["TIMER-1"],
            state_operation="DELETE"
        )
        
        assert "Successfully deleted" in result["message"]
        assert len(DB["timers"]) == 0

    def test_change_timer_state_bulk_operation(self):
        """Test bulk state change operation"""
        # Add another timer
        DB["timers"]["TIMER-2"] = {
            "timer_id": "TIMER-2",
            "original_duration": "10m",
            "remaining_duration": "5m",
            "time_of_day": "3:00 PM",
            "label": "Short break",
            "state": "RUNNING",
            "created_at": "2024-01-15T15:00:00",
            "fire_time": "2024-01-15T15:10:00",
            "start_time": "2024-01-15T15:00:00"
        }
        
        result = change_timer_state(
            timer_type="RUNNING",
            state_operation="PAUSE",
            bulk_operation=True
        )
        
        assert "Successfully modified 2 timer(s)" in result["message"]
        assert all(timer["state"] == "PAUSED" for timer in result["timer"])


if __name__ == "__main__":
    pytest.main([__file__]) 