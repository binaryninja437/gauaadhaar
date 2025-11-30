"""Quick fix for dashboard.py - replace broken section."""
import re

# Read the file
with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken section (lines 220-262)
# The section starts at "if response.status_code == 200:" and ends before "elif identify_button"

broken_pattern = r'(if response\.status_code == 200:.*?)(st\.warning\("Make sure the API server is running at http://localhost:8000"\)\s+elif identify_button)'

replacement = r'''\1
                            st.markdown("---")
                            st.success("""
                            **✅ AUTO-APPROVED - Strong Match**
                            
                            Confidence >= 85%. The uploaded photo strongly matches this registered cow.
                            No manual review required.
                            """)
                        
                        elif result['status'] == 'MANUAL_REVIEW':
                            st.warning("⚠️ MANUAL REVIEW REQUIRED - Potential match requiring verification")
                        
                        else:  # REJECTED
                            st.error("❌ REJECTED - No match found")
                    
                    else:
                        st.error(f"❌ Error: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")
                    st.warning("Make sure the API server is running at http://localhost:8000")
        
        \2'''

# Apply the fix
fixed_content = re.sub(broken_pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Dashboard fixed!")
