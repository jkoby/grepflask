# app.py
import subprocess
import shlex
import os
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main search page."""
    return render_template('index.html', results=None, error=None)

@app.route('/search', methods=['POST'])
def search_files():
    """Handles the file search request using grep."""
    search_term = request.form.get('search_term', '')
    directory = request.form.get('directory', '.') # Default to current directory

    results = None
    error = None

    if not search_term:
        error = "Please provide a search term."
    elif not directory:
        error = "Please provide a directory to search in."
    elif not os.path.isdir(directory):
        error = f"Error: Directory '{directory}' does not exist or is not a directory."
    else:
        try:
            # Construct the grep command.
            # -r: recursive search
            # -n: show line number
            # -i: ignore case
            # shlex.split is used to safely split the command string into a list
            # for subprocess.run, preventing simple command injection.
            # Using 'cd' to change to the target directory before grep ensures
            # that grep's output paths are relative to the target directory.
            command = f"cd {shlex.quote(directory)} && grep -r -n -i {shlex.quote(search_term)} ."
            
            # Execute the command
            process = subprocess.run(
                command,
                shell=True, # shell=True is needed here because of the '&&' operator and 'cd'
                capture_output=True,
                text=True,
                check=False # Do not raise an exception for non-zero exit codes (e.g., grep finds no matches)
            )

            if process.returncode == 0:
                # Grep found matches
                results = process.stdout.strip()
            elif process.returncode == 1:
                # Grep found no matches
                results = "No matches found."
            else:
                # Other grep error
                error = f"Grep command failed with error: {process.stderr.strip()}"
                
        except Exception as e:
            error = f"An unexpected error occurred: {e}"
    
    # Render the index page with results or error
    return render_template('index.html', results=results, error=error, 
                           search_term=search_term, directory=directory)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True) # debug=True allows for automatic reloading on code changes
