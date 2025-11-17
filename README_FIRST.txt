================================================================================
                        ⚠️ READ THIS FIRST! ⚠️
================================================================================

You're on Mac. Here's the EASIEST way to run this project:


METHOD 1: USING TERMINAL (EASIEST - GUARANTEED TO WORK)
========================================================

1. Open Terminal:
   - Press: Command + Space
   - Type: Terminal
   - Press: Enter

2. Copy and paste this EXACT command:
   cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"

3. Press Enter

4. For FIRST TIME SETUP, type:
   chmod +x SETUP.command RUN.command && ./SETUP.command

5. Press Enter
6. Wait for setup to finish (5-10 minutes)

7. To RUN the app, type:
   ./RUN.command

8. Press Enter
9. Wait 10 seconds
10. Browser opens automatically!


METHOD 2: DOUBLE-CLICK (IF METHOD 1 DOESN'T WORK)
===================================================

1. Right-click on: SETUP.command
2. Click: "Open"
3. If Mac says "Cannot be opened", click "Open" anyway
4. Wait for setup

5. Right-click on: RUN.command
6. Click: "Open"
7. If Mac says "Cannot be opened", click "Open" anyway
8. Wait 10 seconds
9. Browser opens!


WHAT EACH FILE DOES:
====================

SETUP.command - Run this ONCE (first time only)
  - Installs everything needed
  - Sets up database
  - Takes 5-10 minutes

RUN.command - Run this EVERY TIME you want to use the app
  - Starts the application
  - Opens browser automatically
  - Takes 10 seconds

SIMPLE_INSTRUCTIONS.txt - More detailed help


TROUBLESHOOTING:
================

Problem: "Permission denied"
Solution: Run this in Terminal first:
  chmod +x SETUP.command RUN.command

Problem: "Command not found"
Solution: Make sure you're in the project folder in Terminal

Problem: Files open in text editor instead of running
Solution: Use Terminal Method (Method 1 above)


NEED HELP?
==========

1. Check SIMPLE_INSTRUCTIONS.txt
2. All errors are saved in: flask.log, celery-worker.log, celery-beat.log


================================================================================
                    START WITH METHOD 1 - IT ALWAYS WORKS!
================================================================================

