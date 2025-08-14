import os
import logging
from typing import Dict, Any, List, Optional

# Get logger for this module
logger = logging.getLogger(__name__)

# List of allowed system environment variables
ALLOWED_SYSTEM_VARS: List[str] = [
    'PATH', 'LANG', 'HOME', 'USER', 'SHELL', 'TERM',
    'DISPLAY', 'EDITOR', 'VISUAL', 'PAGER', 'TZ'
]

def prepare_command_environment(db: Dict[str, Any], temp_dir: str) -> Dict[str, str]:
    """
    Prepare an isolated environment dictionary for command execution.
    
    Args:
        db: The database dictionary containing environment configuration
        temp_dir: The temporary directory path for command execution
    
    Returns:
        Dict[str, str]: The prepared environment dictionary
    """
    # Get shell config environment variables
    shell_config = db.get('shell_config', {})
    config_env = shell_config.get('environment_variables', {})
    
    # Initialize with base environment variables from shell config
    env: Dict[str, str] = {
        'PWD': temp_dir,
        'SHELL': '/bin/bash',
        'USER': config_env.get('USER', 'user'),
        'HOME': config_env.get('HOME', '/home/user'),
        'PATH': config_env.get('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'),
        'TERM': 'xterm-256color',
        'LANG': 'en_US.UTF-8',
        'LC_ALL': 'en_US.UTF-8',
        'HOSTNAME': 'isolated-env',
        'TZ': 'UTC'
    }
    
    # Add any additional environment variables from shell config
    for key, value in config_env.items():
        if key not in ['USER', 'HOME', 'PATH']:  # Already set above
            env[key] = value
    
    # Add workspace environment variables (overriding base vars)
    workspace_env = db.get('environment', {}).get('workspace', {})
    env.update(workspace_env)
    
    # Add session environment variables (overriding workspace and base vars)
    session_env = db.get('environment', {}).get('session', {})
    env.update(session_env)
    
    return env

def expand_variables(command: str, env: Dict[str, str]) -> str:
    """
    Expand environment variables in the command string.
    
    Args:
        command: The command string potentially containing environment variables
        env: The environment dictionary to use for expansion
    
    Returns:
        str: The command with environment variables expanded
    """
    result = []
    i = 0
    in_single_quotes = False
    in_double_quotes = False
    
    while i < len(command):
        char = command[i]
        
        # Handle quotes
        if char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
            result.append(char)
            i += 1
            continue
        elif char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
            result.append(char)
            i += 1
            continue
        
        # Handle variable expansion
        if char == '$' and not in_single_quotes:
            if i + 1 < len(command):
                next_char = command[i + 1]
                if next_char == '{':
                    # ${VAR} format
                    end_brace = command.find('}', i)
                    if end_brace != -1:
                        var_name = command[i+2:end_brace]
                        if var_name in env:
                            result.append(env[var_name])
                        else:
                            result.append('')  # Unset variables expand to empty string
                        i = end_brace + 1
                        continue
                elif next_char.isalpha() or next_char == '_':
                    # $VAR format
                    j = i + 1
                    while j < len(command) and (command[j].isalnum() or command[j] == '_'):
                        j += 1
                    var_name = command[i+1:j]
                    if var_name in env:
                        result.append(env[var_name])
                    else:
                        result.append('')  # Unset variables expand to empty string
                    i = j
                    continue
                else:
                    # Preserve $ if not followed by a valid variable name
                    result.append(char)
                    i += 1
                    continue
            else:
                # Preserve $ at end of string
                result.append(char)
                i += 1
                continue
        
        result.append(char)
        i += 1
    
    return ''.join(result)

def handle_env_command(command: str, db: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle environment variable commands (export, unset, env).
    
    Args:
        command: The command string to handle
        db: The database dictionary containing environment configuration
    
    Returns:
        Dict[str, Any]: Command execution result with all required keys
    """
    # Initialize environment if not present
    if 'environment' not in db:
        db['environment'] = {'system': {}, 'workspace': {}, 'session': {}}
    
    # Get current directory for result
    current_cwd = db.get("cwd", db.get("workspace_root", "/tmp"))
    
    if command.startswith('export '):
        # Handle export VAR=value
        var_assignment = command[7:].strip()
        if '=' not in var_assignment:
            return {
                'command': command,
                'directory': current_cwd,
                'stdout': '',
                'stderr': 'export: Invalid syntax. Use: export VAR=value\n',
                'returncode': 1,
                'pid': None,
                'process_group_id': None,
                'signal': None,
                'message': 'Export command failed: Invalid syntax'
            }
        
        key, value = var_assignment.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Remove quotes if present
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
            # Don't expand variables if the value was in single quotes
            if not value.startswith("'"):
                env = prepare_command_environment(db, '/tmp')  # temp dir not important for expansion
                value = expand_variables(value, env)
        else:
            # Expand variables in unquoted values
            env = prepare_command_environment(db, '/tmp')  # temp dir not important for expansion
            value = expand_variables(value, env)
        
        # Store the value in the session environment
        db['environment']['session'][key] = value
        return {
            'command': command,
            'directory': current_cwd,
            'stdout': '',
            'stderr': '',
            'returncode': 0,
            'pid': None,
            'process_group_id': None,
            'signal': None,
            'message': f'Exported {key}={value}'
        }
    
    elif command.startswith('unset '):
        # Handle unset VAR
        var = command[6:].strip()
        session_env = db['environment']['session']
        workspace_env = db['environment']['workspace']
        
        if var in session_env:
            del session_env[var]
            return {
                'command': command,
                'directory': current_cwd,
                'stdout': '',
                'stderr': '',
                'returncode': 0,
                'pid': None,
                'process_group_id': None,
                'signal': None,
                'message': f'Unset {var} from session environment'
            }
        elif var in workspace_env:
            del workspace_env[var]
            return {
                'command': command,
                'directory': current_cwd,
                'stdout': '',
                'stderr': '',
                'returncode': 0,
                'pid': None,
                'process_group_id': None,
                'signal': None,
                'message': f'Unset {var} from workspace environment'
            }
        else:
            return {
                'command': command,
                'directory': current_cwd,
                'stdout': '',
                'stderr': '',
                'returncode': 0,
                'pid': None,
                'process_group_id': None,
                'signal': None,
                'message': f'Variable {var} was not set'
            }
    
    elif command == 'env':
        # Show all environment variables
        env = prepare_command_environment(db, '/tmp')  # temp dir not important for listing
        output_lines = [f'{k}={v}' for k, v in sorted(env.items())]
        return {
            'command': command,
            'directory': current_cwd,
            'stdout': '\n'.join(output_lines) + '\n',
            'stderr': '',
            'returncode': 0,
            'pid': None,
            'process_group_id': None,
            'signal': None,
            'message': 'Environment variables listed'
        }
    
    return {
        'command': command,
        'directory': current_cwd,
        'stdout': '',
        'stderr': f'Unknown environment command: {command}\n',
        'returncode': 1,
        'pid': None,
        'process_group_id': None,
        'signal': None,
        'message': 'Invalid environment command'
    }

def save_workspace_environment(db: Dict[str, Any]) -> Optional[str]:
    """
    Save workspace environment to a .env file.
    
    Args:
        db: The database dictionary containing environment configuration
    
    Returns:
        Optional[str]: Path to the saved .env file or None if save failed
    """
    try:
        env_file = os.path.join(db['workspace_root'], '.env')
        workspace_env = db.get('environment', {}).get('workspace', {})
        
        with open(env_file, 'w') as f:
            for key, value in sorted(workspace_env.items()):
                f.write(f'export {key}={value}\n')
        
        return env_file
    except Exception as e:
        logger.error(f"Failed to save workspace environment: {e}")
        return None

def load_workspace_environment(db: Dict[str, Any]) -> bool:
    """
    Load workspace environment from .env file.
    
    Args:
        db: The database dictionary to update with loaded environment
    
    Returns:
        bool: True if environment was loaded successfully
    """
    try:
        env_file = os.path.join(db['workspace_root'], '.env')
        if not os.path.exists(env_file):
            return False
        
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('export '):
                    # Parse export VAR=value
                    var_assignment = line[7:].strip()
                    if '=' in var_assignment:
                        key, value = var_assignment.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        # Store in workspace environment
                        if 'environment' not in db:
                            db['environment'] = {'system': {}, 'workspace': {}, 'session': {}}
                        db['environment']['workspace'][key] = value
        
        return True
    except Exception as e:
        logger.error(f"Failed to load workspace environment: {e}")
        return False 