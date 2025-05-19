# PythonAnywhere Deployment Guide

This guide will walk you through the process of deploying your Python web application to PythonAnywhere using GitHub.

## Prerequisites

1. A PythonAnywhere account (free or paid)
2. Your code in a GitHub repository
3. Python web application (Flask, Django, etc.)

## Step 1: Set Up PythonAnywhere Account

1. Sign up at https://www.pythonanywhere.com
2. Choose your account type (Beginner account is free)
3. Log in to your PythonAnywhere dashboard

## Step 2: Clone Your GitHub Repository

1. Open a PythonAnywhere Bash console
2. Navigate to your desired directory:
   ```bash
   cd ~/myproject
   ```
3. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   ```

## Step 3: Set Up Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Configure Web App

1. Go to the Web tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose your framework (e.g., Flask, Django)
4. Configure your web app:
   - Set the path to your virtual environment
   - Set the path to your WSGI file
   - Configure your static files

## Step 5: Set Up WSGI File

1. In the Web tab, click on the WSGI configuration file link
2. Modify the WSGI file to point to your application:

For Flask:
```python
import sys
path = '/home/yourusername/myproject'
if path not in sys.path:
    sys.path.append(path)

from your_app import app as application
```

For Django:
```python
import os
import sys

path = '/home/yourusername/myproject'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'your_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Step 6: Configure Environment Variables

1. In the Web tab, find the "Environment variables" section
2. Add your environment variables:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   ```

## Step 7: Set Up Static Files

1. In the Web tab, find the "Static files" section
2. Add your static files configuration:
   - URL: /static/
   - Directory: /home/yourusername/myproject/static

## Step 8: Set Up Database (if needed)

1. Go to the Databases tab
2. Initialize your database:
   ```bash
   python manage.py migrate  # For Django
   ```

## Step 9: Set Up Automatic Deployment

1. Create a deployment script (deploy.sh):
   ```bash
   #!/bin/bash
   cd ~/myproject
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate  # For Django
   touch /var/www/yourusername_pythonanywhere_com_wsgi.py
   ```

2. Make it executable:
   ```bash
   chmod +x deploy.sh
   ```

3. Set up GitHub Actions (.github/workflows/deploy.yml):
   ```yaml
   name: Deploy to PythonAnywhere
   on:
     push:
       branches: [ main ]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - name: Deploy to PythonAnywhere
           uses: appleboy/ssh-action@master
           with:
             host: ${{ secrets.PYTHONANYWHERE_HOST }}
             username: ${{ secrets.PYTHONANYWHERE_USERNAME }}
             key: ${{ secrets.PYTHONANYWHERE_SSH_KEY }}
             script: |
               cd ~/myproject
               ./deploy.sh
   ```

## Step 10: Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following secrets:
   - PYTHONANYWHERE_HOST: Your PythonAnywhere hostname
   - PYTHONANYWHERE_USERNAME: Your PythonAnywhere username
   - PYTHONANYWHERE_SSH_KEY: Your SSH private key

## Common Issues and Solutions

### 1. Import Errors
- Check your virtual environment is activated
- Verify all requirements are installed
- Check your PYTHONPATH

### 2. Static Files Not Loading
- Verify static files configuration
- Check file permissions
- Clear browser cache

### 3. Database Issues
- Check database credentials
- Verify database migrations
- Check database permissions

## Maintenance Tips

1. Regular updates:
   - Keep dependencies updated
   - Monitor error logs
   - Backup database regularly

2. Security:
   - Use environment variables for sensitive data
   - Keep PythonAnywhere account secure
   - Regular security audits

3. Performance:
   - Monitor resource usage
   - Optimize database queries
   - Use caching when appropriate

## Support Resources

- PythonAnywhere Documentation: https://help.pythonanywhere.com
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- GitHub Actions Documentation: https://docs.github.com/en/actions

## Additional Notes

- Keep your PythonAnywhere credentials secure
- Document your deployment process
- Set up monitoring for your application
- Consider using a staging environment
- Regular backups are important

Remember to replace placeholder values (like `yourusername` and `myproject`) with your actual information when following these steps. 