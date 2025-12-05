# scripts/run_policy_engine.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sacco_core.policy.engine import PolicyEngine

def main():
    """Run the policy engine to evaluate rules and trigger actions"""
    print("Starting Policy Engine...")
    
    try:
        engine = PolicyEngine()
        results = engine.evaluate_all_rules()
        
        print(f"Evaluated {len(results)} rules")
        
        for result in results:
            if result['triggered']:
                print(f"🚨 Rule triggered: {result['rule_name']}")
                print(f"   Condition: {result['condition']}")
                print(f"   Actions: {result['actions_taken']}")
            else:
                print(f"✓ Rule not triggered: {result['rule_name']}")
                
    except Exception as e:
        print(f"Error running policy engine: {e}")

if __name__ == "__main__":
    main()