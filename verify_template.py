import os
import datetime
from jinja2 import Environment, FileSystemLoader

def render_email(template_path, context):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    return template.render(context)

def verify():
    template_path = 'email/templates/newsletter.html'
    today_str = datetime.datetime.now().strftime("%d-%B")
    
    # Mock data
    context = {
        'name': 'Test User',
        'subject': "Tirwin Pulse | Logistics Intelligence Brief", 
        'body': '<p>This is the personalized body content.</p>',
        'date': today_str
    }
    
    try:
        output = render_email(template_path, context)
        
        # Check for key elements
        if "Tirwin Pulse" in output and today_str in output:
            print(f"SUCCESS: Template rendered with banner and date: {today_str}")
        else:
            print("FAILURE: Banner or date missing.")
            
        with open('verification_output.html', 'w') as f:
            f.write(output)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify()
