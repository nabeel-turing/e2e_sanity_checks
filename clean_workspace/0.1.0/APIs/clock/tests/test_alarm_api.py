# APIs/clock/tests/test_alarm_api.py

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..AlarmApi import (
    create_alarm,
    show_matching_alarms,
    modify_alarm_v2,
    snooze,
    create_clock,
    modify_alarm,
    change_alarm_state,
    snooze_alarm
)
from ..SimulationEngine.db import DB
from ..SimulationEngine.custom_errors import *


class TestCreateAlarm:
    def setup_method(self):
        """Reset DB before each test"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_create_alarm_with_duration(self):
        """Test creating an alarm with duration"""
        result = create_alarm(duration="30m", label="Test alarm")
        
        assert "message" in result
        assert "alarm" in result
        assert len(result["alarm"]) == 1
        
        alarm = result["alarm"][0]
        assert alarm["label"] == "Test alarm"
        assert alarm["state"] == "ACTIVE"
        assert "ALARM-1" in alarm["alarm_id"]

    def test_create_alarm_with_time(self):
        """Test creating an alarm with specific time"""
        result = create_alarm(time="9:30 AM", label="Morning meeting")
        
        assert "message" in result
        assert "alarm" in result
        assert len(result["alarm"]) == 1
        
        alarm = result["alarm"][0]
        assert alarm["label"] == "Morning meeting"
        assert "9:30 AM" in alarm["time_of_day"]

    def test_create_alarm_with_recurrence(self):
        """Test creating a recurring alarm"""
        result = create_alarm(
            time="7:00 AM",
            label="Daily standup",
            recurrence=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        )
        
        assert "message" in result
        alarm = result["alarm"][0]
        assert "MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY" in alarm["recurrence"]

    def test_create_alarm_missing_time_and_duration(self):
        """Test error when neither time nor duration provided"""
        with pytest.raises(ValueError, match="Either duration or time must be provided"):
            create_alarm(label="Invalid alarm")

    def test_create_alarm_invalid_duration_format(self):
        """Test error with invalid duration format"""
        with pytest.raises(ValueError, match="Invalid duration format"):
            create_alarm(duration="invalid_duration")

    def test_create_alarm_invalid_time_format(self):
        """Test error with invalid time format"""
        with pytest.raises(ValueError, match="Invalid time format"):
            create_alarm(time="invalid_time")

    def test_create_alarm_invalid_date_format(self):
        """Test error with invalid date format"""
        with pytest.raises(ValueError, match="Invalid date format"):
            create_alarm(time="9:00 AM", date="invalid_date")

    def test_create_alarm_invalid_recurrence(self):
        """Test error with invalid recurrence days"""
        with pytest.raises(ValueError, match="Invalid recurrence days"):
            create_alarm(time="9:00 AM", recurrence=["INVALID_DAY"])

    def test_create_alarm_type_validation(self):
        """Test type validation for parameters"""
        with pytest.raises(TypeError):
            create_alarm(duration=123)  # Should be string
        
        with pytest.raises(TypeError):
            create_alarm(time="9:00 AM", label=123)  # Should be string
        
        with pytest.raises(TypeError):
            create_alarm(time="9:00 AM", recurrence="MONDAY")  # Should be list


class TestShowMatchingAlarms:
    def setup_method(self):
        """Reset DB and add sample alarms"""
        DB.clear()
        DB.update({
            "alarms": {
                "ALARM-1": {
                    "alarm_id": "ALARM-1",
                    "time_of_day": "7:00 AM",
                    "date": "2024-01-15",
                    "label": "Morning alarm",
                    "state": "ACTIVE",
                    "recurrence": "",
                    "created_at": "2024-01-14T22:30:00",
                    "fire_time": "2024-01-15T07:00:00"
                },
                "ALARM-2": {
                    "alarm_id": "ALARM-2",
                    "time_of_day": "8:30 AM",
                    "date": "2024-01-15",
                    "label": "Meeting reminder",
                    "state": "DISABLED",
                    "recurrence": "",
                    "created_at": "2024-01-14T20:15:00",
                    "fire_time": "2024-01-15T08:30:00"
                }
            },
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_show_all_alarms(self):
        """Test showing all alarms when no filters"""
        result = show_matching_alarms()
        
        assert "message" in result
        assert "alarm" in result
        assert len(result["alarm"]) == 2

    def test_show_alarms_by_label(self):
        """Test filtering alarms by label"""
        result = show_matching_alarms(query="Morning alarm")
        
        assert len(result["alarm"]) == 1
        assert result["alarm"][0]["label"] == "Morning alarm"

    def test_show_alarms_by_time(self):
        """Test filtering alarms by time"""
        result = show_matching_alarms(query="7:00 AM")
        
        assert len(result["alarm"]) == 1
        assert result["alarm"][0]["time_of_day"] == "7:00 AM"

    def test_show_alarms_by_type(self):
        """Test filtering alarms by type"""
        DB["alarms"]["ALARM-1"]["fire_time"] = (datetime.now() + timedelta(minutes=10)).isoformat()
        result = show_matching_alarms(alarm_type="ACTIVE")
        
        assert len(result["alarm"]) == 1
        assert result["alarm"][0]["state"] == "ACTIVE"

    def test_show_alarms_by_date(self):
        """Test filtering alarms by date"""
        result = show_matching_alarms(date="2024-01-15")
        
        assert len(result["alarm"]) == 2

    def test_show_alarms_by_start_date(self):
        """Test filtering alarms by start_date"""
        result = show_matching_alarms(start_date="2024-01-15")
        
        assert len(result["alarm"]) == 2
    
    def test_show_alarms_by_end_date(self):
        """Test filtering alarms by end_date"""
        DB["alarms"]["ALARM-1"]["date"] = "2024-01-14"
        result = show_matching_alarms(end_date="2024-01-14")
        assert len(result["alarm"]) == 1

    def test_show_alarms_by_date_range(self):
        """Test filtering alarms by date range"""
        DB["alarms"]["ALARM-1"]["date"] = "2024-01-14"
        result = show_matching_alarms(start_date="2024-01-14", end_date="2024-01-15")
        assert len(result["alarm"]) == 2

    def test_show_alarms_by_label_and_type(self):
        """Test filtering alarms by label and type"""
        DB["alarms"]["ALARM-1"]["fire_time"] = (datetime.now() + timedelta(minutes=10)).isoformat()
        result = show_matching_alarms(query="Morning alarm", alarm_type="ACTIVE")
        
        assert len(result["alarm"]) == 1
        assert result["alarm"][0]["label"] == "Morning alarm"
        assert result["alarm"][0]["state"] == "ACTIVE"

    def test_show_alarms_invalid_date_format(self):
        """Test error with invalid date format"""
        with pytest.raises(ValueError, match="Invalid date format"):
            show_matching_alarms(date="invalid_date")

    def test_show_alarms_type_validation(self):
        """Test type validation"""
        with pytest.raises(TypeError):
            show_matching_alarms(query=123)


class TestModifyAlarmV2:
    def setup_method(self):
        """Reset DB and add sample alarm"""
        DB.clear()
        DB.update({
            "alarms": {
                "ALARM-1": {
                    "alarm_id": "ALARM-1",
                    "time_of_day": "7:00 AM",
                    "date": "2024-01-15",
                    "label": "Morning alarm",
                    "state": "ACTIVE",
                    "recurrence": "",
                    "created_at": "2024-01-14T22:30:00",
                    "fire_time": "2024-01-15T07:00:00"
                }
            },
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_modify_alarm_time(self):
        """Test modifying alarm time"""
        filters = {"time": "7:00 AM"}
        modifications = {"time": "8:00 AM"}
        
        result = modify_alarm_v2(filters=filters, modifications=modifications)
        
        assert "message" in result
        assert "Successfully modified" in result["message"]
        assert result["alarm"][0]["time_of_day"] == "8:00 AM"

    def test_modify_alarm_label(self):
        """Test modifying alarm label"""
        filters = {"label": "Morning alarm"}
        modifications = {"label": "Updated alarm"}
        
        result = modify_alarm_v2(filters=filters, modifications=modifications)
        
        assert result["alarm"][0]["label"] == "Updated alarm"

    def test_modify_alarm_state_delete(self):
        """Test deleting an alarm"""
        filters = {"label": "Morning alarm"}
        modifications = {"state_operation": "DELETE"}
        
        result = modify_alarm_v2(filters=filters, modifications=modifications)
        
        assert "Successfully deleted" in result["message"]
        assert len(DB["alarms"]) == 0

    def test_modify_alarm_no_filters(self):
        """Test modify with no filters shows all alarms"""
        result = modify_alarm_v2()
        
        assert "Please specify which alarm" in result["message"]
        assert len(result["alarm"]) == 1

    def test_modify_alarm_no_match(self):
        """Test modify with no matching alarms"""
        filters = {"label": "Non-existent alarm"}
        
        result = modify_alarm_v2(filters=filters)
        
        assert "No matching alarms found" in result["message"]
        assert len(result["alarm"]) == 0

    def test_modify_alarm_invalid_time_format(self):
        """Test error with invalid time format in modifications"""
        filters = {"label": "Morning alarm"}
        modifications = {"time": "invalid_time"}
        
        with pytest.raises(ValueError, match="Invalid time format"):
            modify_alarm_v2(filters=filters, modifications=modifications)


class TestSnooze:
    def setup_method(self):
        """Reset DB and add firing alarm"""
        DB.clear()
        DB.update({
            "alarms": {
                "ALARM-1": {
                    "alarm_id": "ALARM-1",
                    "time_of_day": "7:00 AM",
                    "date": "2024-01-15",
                    "label": "Morning alarm",
                    "state": "ACTIVE",
                    "recurrence": "",
                    "created_at": "2024-01-14T22:30:00",
                    "fire_time": (datetime.now() - timedelta(minutes=1)).isoformat()
                }
            },
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_snooze_default_duration(self):
        """Test snoozing with default 10 minute duration"""
        result = snooze()
        
        assert "message" in result
        assert "Successfully snoozed" in result["message"]
        assert result["alarm"][0]["state"] == "SNOOZED"

    def test_snooze_custom_duration(self):
        """Test snoozing with custom duration"""
        result = snooze(duration=300)  # 5 minutes
        
        assert "Successfully snoozed" in result["message"]
        assert result["alarm"][0]["state"] == "SNOOZED"

    def test_snooze_until_time(self):
        """Test snoozing until specific time"""
        result = snooze(time="8:00 AM")
        
        assert "Successfully snoozed" in result["message"]
        assert result["alarm"][0]["state"] == "SNOOZED"

    def test_snooze_no_firing_alarms(self):
        """Test snooze when no alarms are firing"""
        DB["alarms"]["ALARM-1"]["fire_time"] = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        result = snooze()
        
        assert "No firing alarms" in result["message"]
        assert len(result["alarm"]) == 0

    def test_snooze_invalid_time_format(self):
        """Test error with invalid time format"""
        with pytest.raises(ValueError, match="Invalid time format"):
            snooze(time="invalid_time")


class TestCreateClock:
    def setup_method(self):
        """Reset DB before each test"""
        DB.clear()
        DB.update({
            "alarms": {},
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_create_clock_alarm(self):
        """Test creating an alarm via create_clock"""
        result = create_clock(
            type="ALARM",
            duration="30m",
            label="Test alarm"
        )
        
        assert "message" in result
        assert "alarm" in result
        assert len(result["alarm"]) == 1

    def test_create_clock_timer(self):
        """Test creating a timer via create_clock"""
        with patch('clock.TimerApi.create_timer') as mock_create_timer:
            mock_create_timer.return_value = {"message": "Timer created", "timer": []}
            
            result = create_clock(
                type="TIMER",
                duration="25m",
                label="Pomodoro"
            )
            
            mock_create_timer.assert_called_once()

    def test_create_clock_invalid_type(self):
        """Test error with invalid type"""
        with pytest.raises(ValueError, match="type must be TIMER or ALARM"):
            create_clock(type="INVALID", duration="30m")

    def test_create_clock_type_validation(self):
        """Test type validation"""
        with pytest.raises(TypeError):
            create_clock(type=123, duration="30m")


class TestModifyAlarm:
    def setup_method(self):
        """Reset DB and add sample alarm"""
        DB.clear()
        DB.update({
            "alarms": {
                "ALARM-1": {
                    "alarm_id": "ALARM-1",
                    "time_of_day": "7:00 AM",
                    "date": "2024-01-15",
                    "label": "Morning alarm",
                    "state": "ACTIVE",
                    "recurrence": "",
                    "created_at": "2024-01-14T22:30:00",
                    "fire_time": "2024-01-15T07:00:00"
                }
            },
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_modify_alarm_legacy_time(self):
        """Test legacy modify_alarm with new time"""
        result = modify_alarm(
            query="Morning alarm",
            new_time_of_day="08:00:00",
            new_am_pm_or_unknown="AM"
        )
        
        assert "Successfully modified" in result["message"]


class TestChangeAlarmState:
    def setup_method(self):
        """Reset DB and add sample alarm"""
        DB.clear()
        DB.update({
            "alarms": {
                "ALARM-1": {
                    "alarm_id": "ALARM-1",
                    "time_of_day": "7:00 AM",
                    "date": "2024-01-15",
                    "label": "Morning alarm",
                    "state": "ACTIVE",
                    "recurrence": "",
                    "created_at": "2024-01-14T22:30:00",
                    "fire_time": "2024-01-15T07:00:00"
                }
            },
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_change_alarm_state_disable(self):
        """Test disabling an alarm"""
        result = change_alarm_state(
            label="Morning alarm",
            state_operation="DISABLE"
        )
        
        assert "Successfully modified" in result["message"]


class TestSnoozeAlarm:
    def setup_method(self):
        """Reset DB and add firing alarm"""
        DB.clear()
        DB.update({
            "alarms": {
                "ALARM-1": {
                    "alarm_id": "ALARM-1",
                    "time_of_day": "7:00 AM",
                    "date": "2024-01-15",
                    "label": "Morning alarm",
                    "state": "ACTIVE",
                    "recurrence": "",
                    "created_at": "2024-01-14T22:30:00",
                    "fire_time": (datetime.now() - timedelta(minutes=1)).isoformat()
                }
            },
            "timers": {},
            "stopwatch": {},
            "settings": {}
        })

    def test_snooze_alarm_duration(self):
        """Test snoozing alarm with duration"""
        result = snooze_alarm(snooze_duration="600")  # 10 minutes
        
        assert "Successfully snoozed" in result["message"]

    def test_snooze_alarm_until_time(self):
        """Test snoozing alarm until specific time"""
        result = snooze_alarm(
            snooze_till_time_of_day="08:00:00",
            am_pm_or_unknown="AM"
        )
        
        assert "Successfully snoozed" in result["message"]




if __name__ == "__main__":
    pytest.main([__file__]) 