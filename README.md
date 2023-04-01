# GitLab-Container-Registry-Cleanup-Script

GitLab Cleanup is a Python script that helps manage and clean up GitLab container registries by removing old and unused tags. It also allows you to configure the number of tags to keep for important repositories, ignore specific repositories, and delete empty repositories.

## Features

- Delete tags older than a specified number of days
- Keep a specified number of tags for important repositories
- Ignore specific repositories
- Delete empty repositories
- Dry run mode to preview actions without making any changes

## Requirements

- Python 3.6 or higher
- `requests`, `python-dotenv`, and `termcolor` Python packages

## Installation

1. Clone this repository or download the script.
2. Install the required Python packages:
```bash
pip install requests python-dotenv termcolor
```
3. Create a .env file in the same directory as the script and set the following environment variables:
```makefile
GITLAB_API=https://gitlab.example.com/api/v4
GITLAB_PROJECT_ID=your_project_id
GITLAB_ACCESS_TOKEN=your_private_token
```
Replace `gitlab.example.com` with your GitLab instance domain, `your_project_id` with the project ID you want to manage, and `your_private_token` with your personal GitLab access token.

## Usage

1. Open the script in a text editor and configure the following settings as needed:
- `dry_run`: Set to False to perform actual deletions; set to True to preview actions without making any changes.
- `important_repositories`: Define the repository names and the number of tags to keep per repository.
- `ignored_repositories`: Define the repositories to ignore.
- `get_size_of_ignored_repositories`: Set to True to get the size of ignored repositories.
- `older_than_days`: Delete tags older than this number of days.
- `tags_per_page`: Set the number of tags to fetch per page (max 100).
- `delete_empty_repositories`: Set to True to delete empty repositories (with 0 tags).
2. Run the script:

```bash
python gitlab_cleanup.py
```

## Scheduling with Cron

You can use a cron job to execute the GitLab Cleanup script automatically every hour. Here's how to set up a cron job for the script:

### For Linux and macOS

1. Open the terminal.
2. Run the `crontab -e` command to edit your user's cron table.
3. Add the following line to the file:
```
Copy code
0 * * * * /path/to/python /path/to/gitlab_cleanup.py >> /path/to/logfile.log 2>&1
```
Replace `/path/to/python` with the path to your Python interpreter (you can find it with `which python`), `/path/to/gitlab_cleanup.py` with the path to the script, and `/path/to/logfile.log` with the path to the log file you want to create.

4. Save the file and exit the editor.

The cron job will now run the GitLab Cleanup script every hour and append the output to the specified log file.

### For Windows

1. Open the Windows Task Scheduler by pressing `Win + R`, typing `taskschd.msc`, and pressing `Enter`.
2. Click on "Create Basic Task..." in the right pane.
3. Enter a name and description for the task, then click "Next."
4. Choose the "Daily" trigger option and click "Next."
5. Set the start time and select "Recur every 1 days" then click "Next."
6. Choose the "Start a program" action and click "Next."
7. Click "Browse..." and navigate to the Python interpreter (usually located in `C:\Python{version}\python.exe`, where `{version}` is your installed Python version).
8. In the "Add arguments (optional)" field, enter the full path to the GitLab Cleanup script:
```bash
/path/to/gitlab_cleanup.py
```
9. In the "Start in (optional)" field, enter the directory containing the script.
10. Click "Next" and then "Finish" to create the task.

Now, right-click on the created task in the Task Scheduler Library and select "Properties." Go to the "Triggers" tab and click "Edit." In the "Advanced settings" section, check the "Repeat task every" box and choose "1 hour" from the dropdown menu. Click "OK" and "OK" again to save the changes.

The task will now run the GitLab Cleanup script every hour. You can view the script's output by setting up logging within the script or using a third-party tool to capture the output.