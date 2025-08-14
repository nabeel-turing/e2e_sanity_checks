from .AlarmApi import change_alarm_properties, delay_active_alarm, find_and_display_alarms, postpone_ringing_alarm, schedule_new_alarm, set_alarm_activation_status, set_time_based_event, update_alarms_with_filters
from .StopwatchApi import activate_stopwatch, display_stopwatch_status
from .TimerApi import adjust_timer_properties, configure_new_timer, find_and_display_timers, set_timer_run_status, update_timers_with_filters

_function_map = {
    'activate_stopwatch': 'clock.mutations.m01.StopwatchApi.activate_stopwatch',
    'adjust_timer_properties': 'clock.mutations.m01.TimerApi.adjust_timer_properties',
    'change_alarm_properties': 'clock.mutations.m01.AlarmApi.change_alarm_properties',
    'configure_new_timer': 'clock.mutations.m01.TimerApi.configure_new_timer',
    'delay_active_alarm': 'clock.mutations.m01.AlarmApi.delay_active_alarm',
    'display_stopwatch_status': 'clock.mutations.m01.StopwatchApi.display_stopwatch_status',
    'find_and_display_alarms': 'clock.mutations.m01.AlarmApi.find_and_display_alarms',
    'find_and_display_timers': 'clock.mutations.m01.TimerApi.find_and_display_timers',
    'postpone_ringing_alarm': 'clock.mutations.m01.AlarmApi.postpone_ringing_alarm',
    'schedule_new_alarm': 'clock.mutations.m01.AlarmApi.schedule_new_alarm',
    'set_alarm_activation_status': 'clock.mutations.m01.AlarmApi.set_alarm_activation_status',
    'set_time_based_event': 'clock.mutations.m01.AlarmApi.set_time_based_event',
    'set_timer_run_status': 'clock.mutations.m01.TimerApi.set_timer_run_status',
    'update_alarms_with_filters': 'clock.mutations.m01.AlarmApi.update_alarms_with_filters',
    'update_timers_with_filters': 'clock.mutations.m01.TimerApi.update_timers_with_filters',
}
