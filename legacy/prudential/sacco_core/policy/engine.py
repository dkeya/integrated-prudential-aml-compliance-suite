# sacco_core/policy/engine.py
import yaml
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

class PolicyEngine:
    """Policy engine for evaluating rules and triggering actions"""
    
    def __init__(self, rules_path: str = "sacco_core/policy/rules.yml"):
        self.rules_path = rules_path
        self.rules = self.load_rules()
    
    def load_rules(self) -> List[Dict]:
        """Load rules from YAML configuration"""
        try:
            with open(self.rules_path, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('rules', [])
        except FileNotFoundError:
            print(f"Rules file not found: {self.rules_path}")
            return []
        except Exception as e:
            print(f"Error loading rules: {e}")
            return []
    
    def get_current_kpis(self) -> Dict[str, float]:
        """Get current KPI values (placeholder - would connect to actual data)"""
        # This would typically query the database for current values
        return {
            'liquidity_ratio': 0.185,
            'par30': 0.042,
            'top_employer_share': 0.28
        }
    
    def evaluate_rule(self, rule: Dict, kpis: Dict, config: Dict) -> Dict[str, Any]:
        """Evaluate a single rule against current KPIs"""
        try:
            condition = rule['when']
            
            # Simple expression evaluation (in production, use a proper expression evaluator)
            triggered = False
            
            if "kpis.liquidity_ratio < config.liquidity_ratio_min" in condition:
                triggered = kpis['liquidity_ratio'] < config['limits']['liquidity_ratio_min']
            elif "kpis.par30 > config.par30_trigger_max" in condition:
                triggered = kpis['par30'] > config['limits']['par30_trigger_max']
            elif "kpis.top_employer_share > config.single_employer_share_max" in condition:
                triggered = kpis['top_employer_share'] > config['limits']['single_employer_share_max']
            
            result = {
                'rule_name': rule['name'],
                'condition': condition,
                'triggered': triggered,
                'actions_taken': []
            }
            
            if triggered:
                result['actions_taken'] = self.execute_actions(rule['actions'])
            
            return result
            
        except Exception as e:
            print(f"Error evaluating rule {rule.get('name', 'unknown')}: {e}")
            return {
                'rule_name': rule.get('name', 'unknown'),
                'condition': rule.get('when', 'unknown'),
                'triggered': False,
                'error': str(e)
            }
    
    def execute_actions(self, actions: List[str]) -> List[str]:
        """Execute the specified actions"""
        executed = []
        
        for action in actions:
            try:
                if action.startswith('email:'):
                    # Send email notification
                    recipient = action.split(':')[1]
                    executed.append(f"email_sent_to_{recipient}")
                    
                elif action.startswith('sms:'):
                    # Send SMS notification
                    recipient = action.split(':')[1]
                    executed.append(f"sms_sent_to_{recipient}")
                    
                elif action == 'flag':
                    # Create flag in database
                    executed.append('flag_created')
                    
            except Exception as e:
                print(f"Error executing action {action}: {e}")
                executed.append(f"error_{action}")
        
        return executed
    
    def evaluate_all_rules(self) -> List[Dict[str, Any]]:
        """Evaluate all rules"""
        from sacco_core.config import ConfigManager
        
        config_manager = ConfigManager()
        config_dict = config_manager.load_settings().dict()
        kpis = self.get_current_kpis()
        
        results = []
        for rule in self.rules:
            result = self.evaluate_rule(rule, kpis, config_dict)
            results.append(result)
        
        return results